# Changelog

All notable changes to the CV Sync Service will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2025-12-12 🎉

### Open Source Release

The CV Sync Service is now open source! Free for recruitment agencies to use, modify, and distribute.

**Repository:** https://github.com/tanova-ai/cv-sync-service
**License:** MIT

### Major Performance Improvements

Complete rewrite for high-volume agencies handling thousands of CVs.

**Performance gains:**
- **100 CVs:** 20 min → 5 min (4x faster)
- **1,000 CVs:** 3.5 hours → 45 min (4.7x faster)
- **10,000 CVs:** 35 hours → 7 hours (5x faster)

### Added

**Concurrent Upload System:**
- ThreadPoolExecutor with 5 workers (configurable via `max_workers`)
- Connection pooling for better network utilization
- Parallel file processing

**Progress Reporting:**
- Real-time updates every 10 files
- Shows upload count, duplicates skipped, errors
- Time estimates for large batches
- Detailed completion summary

**Smart Caching:**
- Batch cache updates (every 10 files instead of per-file)
- Checksum caching to avoid recomputation
- SHA-256-based duplicate detection

**Error Handling:**
- Automatic retries on network failures (configurable)
- Graceful degradation (continues on errors)
- Detailed error logging with stack traces
- Connection timeout handling

**Metadata Extraction:**
- Email from filename (`john_doe_john@example.com.pdf`)
- Job hints from folder names (`/CVs/Backend Engineer/resume.pdf`)
- Recursive subfolder scanning

### Changed
- Rewritten from synchronous to concurrent architecture
- Improved duplicate detection (local cache + server-side checksums)
- Better error messages and debugging output
- Optimized file I/O operations

### Performance Metrics
- **Throughput:** ~2-3 CVs/second (vs 0.5 CV/s in v1.0)
- **Memory usage:** ~50MB (unchanged)
- **Network:** Connection pooling reduces overhead by ~30%

---

## [1.0.0] - 2024-12-03

### Initial Release

First version of the CV Sync Service for Tanova customers.

### Features
- Watch folder for CV files (PDF, DOCX, TXT, MD)
- Automatic upload to Tanova via API
- Duplicate detection using SHA-256 checksums
- Local cache at `~/.tanova/sync_history.json`
- Recursive folder scanning
- File system watching (watchdog library)

### Supported File Types
- PDF (most common)
- DOCX, DOC (Microsoft Word)
- TXT (plain text resumes)
- MD (Markdown resumes)

### Performance
- **Sequential uploads:** ~0.5 CV/second
- **100 CVs:** ~20 minutes
- **1,000 CVs:** ~3.5 hours

---

## Links

- **Repository:** [github.com/tanova-ai/cv-sync-service](https://github.com/tanova-ai/cv-sync-service)
- **Documentation:** [README.md](README.md)
- **Tanova:** [tanova.ai](https://tanova.ai)
- **API Docs:** [tanova.ai/api-docs](https://tanova.ai/api-docs)

---

**Status:** Production Ready ✅
**Current Version:** 2.0.0
**License:** MIT
