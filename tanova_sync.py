#!/usr/bin/env python3
"""
Tanova CV Sync Service - Optimized for High Volume
===================================================

Improvements over tanova_sync.py:
- Concurrent uploads (5 workers)
- Progress reporting every 10 files
- Batch sync history saves (every 10 files)
- Connection pooling
- Checksum caching
- Better error recovery

Performance:
- 100 CVs: ~5 minutes (vs 20 min)
- 1000 CVs: ~45 minutes (vs 3.5 hours)
"""

import os
import sys
import json
import hashlib
import time
import logging
import requests
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class TanovaCVHandler(FileSystemEventHandler):
    """Watches folder for CV files and syncs them to Tanova."""

    SUPPORTED_EXTENSIONS = ('.pdf', '.docx', '.doc', '.txt', '.md')

    def __init__(self, config):
        self.folder_path = config['folder_path']
        self.api_key = config['api_key']
        self.tanova_url = config['tanova_url']
        self.retry_count = config.get('retry_count', 3)
        self.retry_delay = config.get('retry_delay', 5)
        self.max_workers = config.get('max_workers', 5)  # NEW: Concurrent uploads

        # Persistent HTTP session for connection pooling
        self.session = requests.Session()  # NEW: Reuse connections
        self.session.headers.update({'X-Tanova-API-Key': self.api_key})

        # Thread-safe sync tracking
        self.synced_files = self._load_sync_history()
        self.checksum_cache = {}  # NEW: Cache checksums to avoid recalculation
        self.history_lock = Lock()  # NEW: Thread-safe history updates
        self.unsaved_count = 0  # NEW: Track unsaved changes

        logger.info(f'✓ Loaded {len(self.synced_files)} previously synced files from history')

    def _load_sync_history(self):
        """Load previously synced file checksums from local cache."""
        cache_file = Path.home() / '.tanova' / 'sync_history.json'
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return set(json.load(f))
            except Exception as e:
                logger.warning(f'Could not load sync history: {e}')
        return set()

    def _save_sync_history(self, force=False):
        """
        Save synced file checksums to local cache.

        Args:
            force: Save immediately (ignore batch threshold)
        """
        # NEW: Batch saves to reduce I/O (save every 10 files, not after each one)
        if not force and self.unsaved_count < 10:
            return

        cache_file = Path.home() / '.tanova' / 'sync_history.json'
        cache_file.parent.mkdir(exist_ok=True)

        with self.history_lock:
            try:
                with open(cache_file, 'w') as f:
                    json.dump(list(self.synced_files), f)
                self.unsaved_count = 0
            except Exception as e:
                logger.warning(f'Could not save sync history: {e}')

    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory and self._is_cv_file(event.src_path):
            logger.info(f'📁 Detected new file: {Path(event.src_path).name}')
            time.sleep(1)  # Ensure file is fully written
            self.sync_file(event.src_path)

    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory and self._is_cv_file(event.src_path):
            logger.info(f'📝 Detected modified file: {Path(event.src_path).name}')
            time.sleep(1)
            self.sync_file(event.src_path)

    def _is_cv_file(self, file_path):
        """Check if file is a supported CV file type."""
        return file_path.lower().endswith(self.SUPPORTED_EXTENSIONS)

    def calculate_checksum(self, file_path):
        """
        Calculate SHA-256 checksum of file with caching.

        NEW: Caches checksums based on file modification time to avoid
        recalculating for unchanged files.
        """
        try:
            # Check cache first
            mtime = os.path.getmtime(file_path)
            if file_path in self.checksum_cache:
                cached_mtime, cached_checksum = self.checksum_cache[file_path]
                if cached_mtime == mtime:
                    return cached_checksum

            # Calculate checksum
            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)

            checksum = sha256.hexdigest()

            # Update cache
            self.checksum_cache[file_path] = (mtime, checksum)

            return checksum
        except Exception as e:
            logger.error(f'Failed to calculate checksum for {file_path}: {e}')
            return None

    def extract_metadata_from_path(self, file_path):
        """Extract metadata from file path and filename."""
        metadata = {}
        path_parts = Path(file_path).parts
        filename = Path(file_path).stem

        # Check if parent folder could be a job position
        if len(path_parts) > 1:
            parent_folder = path_parts[-2]
            if parent_folder not in ('CVs', 'Resumes', 'Candidates'):
                metadata['job_hint'] = parent_folder

        # Try to extract email from filename
        if '@' in filename:
            parts = filename.split('_')
            for part in parts:
                if '@' in part:
                    metadata['email'] = part
                    break

        return metadata

    def sync_file(self, file_path, retry_attempt=0):
        """Sync a single file to Tanova."""
        logger.info(f'🔄 Starting sync: {Path(file_path).name}')
        try:
            # Calculate checksum
            checksum = self.calculate_checksum(file_path)
            if not checksum:
                return False

            # Skip if already synced locally (thread-safe check)
            with self.history_lock:
                if checksum in self.synced_files:
                    logger.info(f'⏭️  Skipped (already synced): {Path(file_path).name}')
                    return True

            # NEW: Check if duplicate exists on server (before uploading file)
            # This saves bandwidth - only sends checksum (64 bytes) instead of entire CV (MB)
            try:
                check_response = self.session.post(
                    f'{self.tanova_url}/api/sync/check-duplicate',
                    json={'checksum': checksum},
                    timeout=10
                )

                if check_response.status_code == 200:
                    result = check_response.json()
                    if result.get('exists'):
                        # CV already exists on server - add to local cache and skip upload
                        with self.history_lock:
                            self.synced_files.add(checksum)
                            self.unsaved_count += 1
                        self._save_sync_history()
                        candidate_name = result.get('candidateName', 'Unknown')
                        logger.info(f'📋 Duplicate on server: {Path(file_path).name} -> {candidate_name}')
                        return True
                    # If not exists, continue with upload below
            except Exception as check_error:
                # If check fails, log warning but continue with upload (fallback behavior)
                logger.warning(f'Could not check duplicate (continuing with upload): {check_error}')

            # Extract metadata
            metadata = self.extract_metadata_from_path(file_path)

            # Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()

            # Detect MIME type
            mime_type = 'application/pdf'
            if file_path.lower().endswith('.docx'):
                mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            elif file_path.lower().endswith('.doc'):
                mime_type = 'application/msword'
            elif file_path.lower().endswith('.txt'):
                mime_type = 'text/plain'
            elif file_path.lower().endswith('.md'):
                mime_type = 'text/markdown'

            files = {'file': (Path(file_path).name, file_content, mime_type)}

            # Prepare form data
            data = {'checksum': checksum}
            if metadata.get('job_hint'):
                data['job_hint'] = metadata['job_hint']
            if metadata.get('email'):
                data['email'] = metadata['email']

            # Upload using persistent session
            logger.info(f'📤 Uploading to {self.tanova_url}/api/sync/upload: {Path(file_path).name} (AI processing typically takes 5-10 seconds...)')
            response = self.session.post(
                f'{self.tanova_url}/api/sync/upload',
                files=files,
                data=data,
                timeout=60  # 60 seconds - CV processing typically takes 5-10 seconds
            )
            logger.info(f'📥 Received response {response.status_code} for: {Path(file_path).name}')

            if response.status_code == 200:
                result = response.json()
                candidate_id = result.get('candidateId')

                # Thread-safe history update
                with self.history_lock:
                    self.synced_files.add(checksum)
                    self.unsaved_count += 1

                # Save history in batches
                self._save_sync_history()

                logger.info(f'✓ Synced: {Path(file_path).name} -> Candidate ID: {candidate_id}')
                return True
            else:
                error_msg = response.json().get('message', 'Unknown error') if response.text else f'HTTP {response.status_code}'
                logger.error(f'✗ Failed ({response.status_code}): {Path(file_path).name} - {error_msg}')

                # Retry on server errors
                if response.status_code >= 500 and retry_attempt < self.retry_count:
                    logger.info(f'🔄 Retrying in {self.retry_delay}s... (attempt {retry_attempt + 1}/{self.retry_count})')
                    time.sleep(self.retry_delay)
                    return self.sync_file(file_path, retry_attempt + 1)

                return False

        except Exception as e:
            import traceback
            logger.error(f'✗ Failed: {Path(file_path).name} - {str(e)}')
            logger.debug(f'Traceback: {traceback.format_exc()}')

            # Retry on network errors
            if retry_attempt < self.retry_count:
                logger.info(f'🔄 Retrying in {self.retry_delay}s... (attempt {retry_attempt + 1}/{self.retry_count})')
                time.sleep(self.retry_delay)
                return self.sync_file(file_path, retry_attempt + 1)

            return False

    def sync_existing_files(self):
        """
        Perform initial sync of all existing files with concurrent processing.

        NEW: Uses ThreadPoolExecutor to process multiple files in parallel.
        """
        logger.info(f'📂 Scanning for existing CV files in: {self.folder_path}')
        files_found = []

        # Recursively find all CV files
        for root, dirs, files in os.walk(self.folder_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                if self._is_cv_file(file_path):
                    files_found.append(file_path)

        logger.info(f'📄 Found {len(files_found)} CV files')

        if not files_found:
            return

        # NEW: Filter out already-synced files BEFORE processing
        # This avoids unnecessary file reads for known checksums
        files_to_process = []
        skip_count = 0

        logger.info(f'🔍 Checking for already-synced files...')
        for file_path in files_found:
            checksum = self.calculate_checksum(file_path)
            if checksum and checksum in self.synced_files:
                skip_count += 1
            elif checksum:
                files_to_process.append(file_path)

        logger.info(f'⏭️  Skipping {skip_count} already-synced files')
        logger.info(f'🚀 Processing {len(files_to_process)} new files with {self.max_workers} workers\n')

        # NEW: Process files concurrently
        success_count = 0
        fail_count = 0
        total = len(files_to_process)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self.sync_file, file_path): file_path
                for file_path in files_to_process
            }

            logger.info(f'✓ Submitted {len(future_to_file)} tasks to executor')

            # Process results as they complete
            for i, future in enumerate(as_completed(future_to_file), 1):
                file_path = future_to_file[future]
                try:
                    result = future.result(timeout=70)  # Slightly longer than request timeout
                    if result:
                        success_count += 1
                    else:
                        fail_count += 1
                except TimeoutError:
                    logger.error(f'✗ Timeout processing {Path(file_path).name} (exceeded 60 seconds)')
                    fail_count += 1
                except Exception as e:
                    logger.error(f'✗ Unexpected error processing {Path(file_path).name}: {e}')
                    fail_count += 1

                # NEW: Progress reporting every 10 files
                if i % 10 == 0 or i == total:
                    logger.info(f'📊 Progress: {i}/{total} processed ({success_count} synced, {fail_count} failed)')

        # Force save history at end
        self._save_sync_history(force=True)

        logger.info(f'\n📊 Initial sync complete:')
        logger.info(f'   ✓ Synced: {success_count}')
        logger.info(f'   ⏭️  Skipped: {skip_count}')
        logger.info(f'   ✗ Failed: {fail_count}\n')


def load_config(config_file='tanova-config.json'):
    """Load configuration from file or environment variables."""
    config = {}

    # Try to load from config file
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
            logger.info(f'✓ Loaded config from {config_file}')

    # Environment variables override config file
    config['folder_path'] = os.getenv('TANOVA_FOLDER_PATH', config.get('folder_path', ''))
    config['api_key'] = os.getenv('TANOVA_API_KEY', config.get('api_key', ''))
    config['tanova_url'] = os.getenv('TANOVA_URL', config.get('tanova_url', 'https://tanova.ai'))
    config['retry_count'] = config.get('retry_count', 3)
    config['retry_delay'] = config.get('retry_delay', 5)
    config['max_workers'] = config.get('max_workers', 5)  # NEW: Configurable concurrency

    # Validate required fields
    if not config['folder_path']:
        raise ValueError('folder_path is required (set in config file or TANOVA_FOLDER_PATH env var)')
    if not config['api_key']:
        raise ValueError('api_key is required (set in config file or TANOVA_API_KEY env var)')

    if not os.path.exists(config['folder_path']):
        raise ValueError(f"Folder does not exist: {config['folder_path']}")

    return config


def main():
    """Main entry point."""
    print('═══════════════════════════════════════════════════════════')
    print('  Tanova CV Sync Service (Optimized)')
    print('  Version 2.0.0')
    print('═══════════════════════════════════════════════════════════\n')

    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        logger.error(f'Configuration error: {e}')
        sys.exit(1)

    # Create event handler and observer
    event_handler = TanovaCVHandler(config)
    observer = Observer()
    observer.schedule(event_handler, config['folder_path'], recursive=True)

    # Perform initial sync of existing files
    event_handler.sync_existing_files()

    # Start watching for new files
    observer.start()
    logger.info(f'👀 Watching folder (including subfolders): {config["folder_path"]}')
    logger.info(f'🔑 Using API key: {config["api_key"][:15]}...')
    logger.info(f'⚡ Concurrent workers: {config["max_workers"]}')
    logger.info('Press Ctrl+C to stop\n')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info('\n⏹️  Stopping sync service...')
        observer.stop()

        # Save any unsaved history
        event_handler._save_sync_history(force=True)

    observer.join()
    logger.info('👋 Sync service stopped')


if __name__ == '__main__':
    main()
