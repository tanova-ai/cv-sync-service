# CV Sync Service - Enterprise Deployment Guide

**Date:** December 4, 2025
**Version:** 1.0.0
**Target:** Small-to-Medium IT Organizations

---

## Executive Summary

The Tanova CV Sync Service is a Python-based file watcher that automatically uploads CV files to Tanova. This document analyzes its suitability for enterprise deployment and provides recommendations for production use.

**Quick Answer:** The current script is **functional** for SMBs but requires **productionization** for enterprise IT departments.

---

## Current Implementation Analysis

### ✅ Strengths

| Feature | Benefit |
|---------|---------|
| **Lightweight** | Only 2 dependencies (`requests`, `watchdog`) |
| **Cross-platform** | Works on Windows, macOS, Linux |
| **Simple deployment** | Single Python file, no complex setup |
| **No database required** | Uses local JSON file for sync history |
| **Safe operations** | Read-only on file system, only uploads to API |
| **Graceful error handling** | Automatic retries, comprehensive logging |
| **Low resource usage** | Idle CPU/memory when no file changes |
| **Recursive folder watching** | Monitors entire directory tree |
| **Duplicate detection** | SHA-256 checksums prevent re-uploads |
| **Metadata extraction** | Auto-detects job hints and emails from file paths |

### ⚠️ Enterprise Concerns

| Issue | Severity | Impact on IT Operations | Mitigation Priority |
|-------|----------|------------------------|---------------------|
| **No daemon/service mode** | 🟡 Medium | Runs in foreground, stops if terminal closes or user logs out | High |
| **No centralized logging** | 🟡 Medium | Logs only to console, difficult to monitor across multiple deployments | High |
| **API key in config file** | 🔴 High | Security risk if file permissions not properly configured | Critical |
| **No health monitoring** | 🟡 Medium | IT cannot verify service is running/working without manual checks | Medium |
| **Python dependency** | 🟢 Low | Requires Python 3.9+ installation on servers | Low |
| **No automatic updates** | 🟢 Low | Manual script replacement required for updates | Low |
| **Single-threaded** | 🟢 Low | Processes files sequentially (fine for typical CV volumes) | Low |
| **No rate limiting** | 🟡 Medium | Could overwhelm API if thousands of files added at once | Medium |
| **No disk space checks** | 🟢 Low | Sync history file grows indefinitely (very slowly) | Low |

---

## Deployment Options for Enterprises

### Option 1: Docker Container (Recommended for Modern IT)

**Best for:** Organizations with Docker/container infrastructure

**Dockerfile:**
```dockerfile
FROM python:3.9-slim

# Install dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy sync service
COPY tanova_sync.py .

# Create volume mount point for watched folder
VOLUME ["/cvs"]

# Environment variables (override in docker-compose or runtime)
ENV TANOVA_FOLDER_PATH=/cvs
ENV TANOVA_URL=https://tanova.ai

# Run as non-root user
RUN useradd -m -u 1000 tanova && chown -R tanova:tanova /app
USER tanova

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
  CMD test -f /tmp/tanova-health || exit 1

CMD ["python3", "tanova_sync.py"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  tanova-sync:
    build: .
    container_name: tanova-sync
    restart: unless-stopped
    volumes:
      - /path/to/cv/folder:/cvs:ro  # Read-only mount
      - sync-history:/home/tanova/.tanova  # Persist sync history
    environment:
      - TANOVA_API_KEY=${TANOVA_API_KEY}
      - TANOVA_URL=https://tanova.ai
      - TANOVA_FOLDER_PATH=/cvs
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp

volumes:
  sync-history:
```

**Benefits:**
- ✅ Isolated environment (no conflicts with other software)
- ✅ Built-in health checks
- ✅ Easy deployment with `docker-compose up -d`
- ✅ Automatic restart on failure
- ✅ Centralized logging (integrates with logging drivers)
- ✅ Works with orchestration (Kubernetes, Docker Swarm)
- ✅ Read-only file system for security
- ✅ No Python installation required on host

**Deployment:**
```bash
# 1. Set API key in environment
export TANOVA_API_KEY="tanova_sk_xxx"

# 2. Start service
docker-compose up -d

# 3. View logs
docker-compose logs -f tanova-sync

# 4. Check health
docker-compose ps
```

---

### Option 2: Standalone Binary (Best for Traditional Windows Environments)

**Best for:** Organizations without container infrastructure, Windows-heavy environments

**Build Script (build-binary.sh):**
```bash
#!/bin/bash
# Build standalone binary using PyInstaller

pip install pyinstaller

# Windows
pyinstaller --onefile \
  --name tanova-sync \
  --icon tanova.ico \
  --add-data "tanova-config.json:." \
  --hidden-import watchdog \
  --hidden-import requests \
  tanova_sync.py

# Linux/Mac
pyinstaller --onefile \
  --name tanova-sync \
  --hidden-import watchdog \
  --hidden-import requests \
  tanova_sync.py
```

**Benefits:**
- ✅ Single .exe file (Windows) or binary (Linux/Mac)
- ✅ No Python installation required
- ✅ Can be digitally signed for security policies
- ✅ Easier for IT to deploy via GPO or deployment tools
- ✅ Self-contained (includes all dependencies)

**Drawbacks:**
- ❌ Larger file size (~15-20 MB)
- ❌ Separate builds needed for each OS
- ❌ Updates require replacing binary

**Windows Service Wrapper (NSSM):**
```powershell
# Download NSSM (Non-Sucking Service Manager)
# https://nssm.cc/download

# Install as Windows Service
nssm install TanovaSync "C:\Program Files\Tanova\tanova-sync.exe"
nssm set TanovaSync AppDirectory "C:\Program Files\Tanova"
nssm set TanovaSync DisplayName "Tanova CV Sync Service"
nssm set TanovaSync Description "Automatically syncs CV files to Tanova"
nssm set TanovaSync Start SERVICE_AUTO_START

# Set environment variables
nssm set TanovaSync AppEnvironmentExtra TANOVA_API_KEY=tanova_sk_xxx
nssm set TanovaSync AppEnvironmentExtra TANOVA_FOLDER_PATH=C:\CVs

# Start service
nssm start TanovaSync
```

---

### Option 3: Python Script with Systemd (Linux) / Windows Service

**Best for:** Power users, customization needs, minimal infrastructure

#### Linux (systemd)

**Service File: `/etc/systemd/system/tanova-sync.service`**
```ini
[Unit]
Description=Tanova CV Sync Service
After=network.target

[Service]
Type=simple
User=tanova
Group=tanova
WorkingDirectory=/opt/tanova
ExecStart=/usr/bin/python3 /opt/tanova/tanova_sync.py
Restart=always
RestartSec=10

# Environment
Environment="TANOVA_API_KEY=tanova_sk_xxx"
Environment="TANOVA_FOLDER_PATH=/srv/cvs"
Environment="TANOVA_URL=https://tanova.ai"

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/srv/cvs /home/tanova/.tanova

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=tanova-sync

[Install]
WantedBy=multi-user.target
```

**Installation:**
```bash
# 1. Create user
sudo useradd -r -s /bin/false tanova

# 2. Install Python dependencies
sudo pip3 install requests watchdog

# 3. Copy script
sudo mkdir -p /opt/tanova
sudo cp tanova_sync.py /opt/tanova/
sudo chown -R tanova:tanova /opt/tanova

# 4. Install service
sudo cp tanova-sync.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tanova-sync
sudo systemctl start tanova-sync

# 5. Check status
sudo systemctl status tanova-sync
sudo journalctl -u tanova-sync -f
```

#### Windows (Python Service)

**Use `pywin32` to create native Windows service:**

```python
# windows_service.py
import win32serviceutil
import win32service
import win32event
import servicemanager
from tanova_sync import main

class TanovaSyncService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'TanovaSync'
    _svc_display_name_ = 'Tanova CV Sync Service'
    _svc_description_ = 'Automatically syncs CV files to Tanova'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        main()

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(TanovaSyncService)
```

**Install:**
```powershell
pip install pywin32
python windows_service.py install
python windows_service.py start
```

---

## Enterprise Features to Add

### 1. Health Check Endpoint (High Priority)

**Add to script:**
```python
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'healthy',
                'last_sync': handler.last_sync_time.isoformat(),
                'synced_count': len(handler.synced_files)
            }).encode())

def start_health_server(port=8080):
    server = HTTPServer(('', port), HealthCheckHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
```

**Benefits:**
- ✅ IT can monitor with HTTP checks
- ✅ Integrates with monitoring tools (Nagios, Prometheus, Datadog)
- ✅ Load balancers can detect failures

---

### 2. Centralized Logging (High Priority)

**Add syslog support:**
```python
import logging.handlers

# For Linux
syslog = logging.handlers.SysLogHandler(address='/dev/log')
syslog.setLevel(logging.INFO)
logger.addHandler(syslog)

# For Windows
eventlog = logging.handlers.NTEventLogHandler('TanovaSync')
eventlog.setLevel(logging.INFO)
logger.addHandler(eventlog)
```

**Benefits:**
- ✅ Centralized log aggregation
- ✅ Better troubleshooting across deployments
- ✅ Security audit trail

---

### 3. Rate Limiting (Medium Priority)

**Add to prevent API overload:**
```python
from collections import deque
from time import time

class RateLimiter:
    def __init__(self, max_per_minute=60):
        self.max_per_minute = max_per_minute
        self.requests = deque()

    def wait_if_needed(self):
        now = time()
        # Remove requests older than 1 minute
        while self.requests and self.requests[0] < now - 60:
            self.requests.popleft()

        if len(self.requests) >= self.max_per_minute:
            sleep_time = 60 - (now - self.requests[0])
            logger.info(f'Rate limit reached, waiting {sleep_time:.1f}s')
            time.sleep(sleep_time)

        self.requests.append(now)

# Usage in sync_file()
rate_limiter = RateLimiter(max_per_minute=60)
rate_limiter.wait_if_needed()
```

---

### 4. Metrics Endpoint (Medium Priority)

**Add Prometheus-compatible metrics:**
```python
metrics = {
    'files_synced_total': 0,
    'files_failed_total': 0,
    'files_duplicate_total': 0,
    'sync_duration_seconds': []
}

def metrics_endpoint():
    return f"""
# HELP files_synced_total Total files successfully synced
# TYPE files_synced_total counter
files_synced_total {metrics['files_synced_total']}

# HELP files_failed_total Total files that failed to sync
# TYPE files_failed_total counter
files_failed_total {metrics['files_failed_total']}
"""
```

---

### 5. Configuration Validation (Low Priority)

**Add startup validation:**
```python
def validate_config(config):
    errors = []

    # Check API key format
    if not config['api_key'].startswith('tanova_sk_'):
        errors.append('API key format invalid (should start with tanova_sk_)')

    # Check folder permissions
    if not os.access(config['folder_path'], os.R_OK):
        errors.append(f'No read access to folder: {config["folder_path"]}')

    # Check disk space
    stat = os.statvfs(Path.home())
    free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
    if free_gb < 1:
        errors.append(f'Low disk space: {free_gb:.1f} GB remaining')

    # Test API connectivity
    try:
        response = requests.get(f'{config["tanova_url"]}/api/health', timeout=5)
        if response.status_code != 200:
            errors.append('Cannot reach Tanova API')
    except:
        errors.append('Cannot connect to Tanova API')

    return errors
```

---

## Security Recommendations

### API Key Management

**Current Risk:** API key stored in plaintext JSON file

**Solutions (in order of preference):**

1. **Environment variables** (Already supported!)
   ```bash
   export TANOVA_API_KEY="tanova_sk_xxx"
   ```

2. **Secrets management service**
   - AWS Secrets Manager
   - Azure Key Vault
   - HashiCorp Vault
   - Docker secrets

3. **Encrypted config file**
   ```python
   from cryptography.fernet import Fernet

   def load_encrypted_config(key_file, config_file):
       with open(key_file, 'rb') as f:
           key = f.read()
       cipher = Fernet(key)

       with open(config_file, 'rb') as f:
           encrypted = f.read()

       decrypted = cipher.decrypt(encrypted)
       return json.loads(decrypted)
   ```

4. **File permissions** (Minimum requirement)
   ```bash
   # Linux/Mac
   chmod 600 tanova-config.json  # Only owner can read/write
   chown tanova:tanova tanova-config.json

   # Windows
   icacls tanova-config.json /inheritance:r
   icacls tanova-config.json /grant:r "TANOVA_USER:(R)"
   ```

### Network Security

1. **TLS/HTTPS only** (Already implemented - uses `https://tanova.ai`)
2. **Firewall rules:** Only allow outbound HTTPS (443) to tanova.ai
3. **Proxy support:** Add for organizations with corporate proxies

```python
proxies = {
    'http': os.getenv('HTTP_PROXY'),
    'https': os.getenv('HTTPS_PROXY')
}

response = requests.post(url, proxies=proxies, ...)
```

### File System Security

1. **Read-only access** to CV folder (sync service shouldn't write)
2. **Separate user account** with minimal permissions
3. **Audit logging** of all file access

---

## Monitoring & Alerting

### What to Monitor

| Metric | Alert Threshold | Action |
|--------|----------------|--------|
| **Service running** | Down for > 5 minutes | Restart service, notify IT |
| **Successful uploads** | 0 uploads in 24 hours (if files exist) | Check API key, network, logs |
| **Failed uploads** | > 10% failure rate | Check API quota, investigate errors |
| **Disk space** | < 1 GB free | Clean up sync history, expand disk |
| **CPU usage** | > 50% sustained | Investigate file system issues |
| **Memory usage** | > 500 MB | Potential memory leak, restart |

### Monitoring Tools Integration

**Nagios/Icinga:**
```bash
#!/bin/bash
# check_tanova_sync.sh
curl -f http://localhost:8080/health || exit 2
```

**Prometheus:**
```yaml
scrape_configs:
  - job_name: 'tanova-sync'
    static_configs:
      - targets: ['localhost:8080']
```

**Datadog:**
```python
from datadog import statsd

statsd.increment('tanova.sync.success')
statsd.increment('tanova.sync.failed')
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] Review security policy compliance
- [ ] Obtain API key from Tanova
- [ ] Identify CV folder location
- [ ] Determine deployment method (Docker/Binary/Script)
- [ ] Plan monitoring strategy
- [ ] Set up logging infrastructure
- [ ] Configure firewall rules (outbound HTTPS to tanova.ai)
- [ ] Create service account with minimal permissions

### Deployment

- [ ] Install dependencies (Docker/Python/NSSM)
- [ ] Copy sync service files
- [ ] Configure API key (environment or config file)
- [ ] Set file permissions (600 for config, read-only for CV folder)
- [ ] Test connectivity to Tanova API
- [ ] Perform initial sync manually
- [ ] Install as service/daemon
- [ ] Configure automatic start on boot
- [ ] Set up log rotation

### Post-Deployment

- [ ] Monitor logs for 24 hours
- [ ] Verify files are uploading successfully
- [ ] Test service restart behavior
- [ ] Document deployment for IT team
- [ ] Set up monitoring alerts
- [ ] Schedule periodic reviews (monthly)
- [ ] Plan update procedure

---

## Troubleshooting Guide

### Service Won't Start

**Symptoms:** Service fails to start or stops immediately

**Checks:**
1. Verify Python version: `python3 --version` (must be 3.9+)
2. Check dependencies: `pip list | grep -E 'requests|watchdog'`
3. Test config: `python3 tanova_sync.py` (run manually)
4. Check folder exists: `ls -la /path/to/cv/folder`
5. Verify API key format: Should start with `tanova_sk_`
6. Check logs: `journalctl -u tanova-sync -n 50`

### Files Not Syncing

**Symptoms:** Files added but not appearing in Tanova

**Checks:**
1. File extension supported: `.pdf`, `.docx`, `.doc`, `.txt`, `.md`
2. API key permissions: Must have `canUpload=true`
3. Network connectivity: `curl https://tanova.ai`
4. Check sync history: `cat ~/.tanova/sync_history.json`
5. Watch logs live: `journalctl -u tanova-sync -f`
6. Test API manually:
   ```bash
   curl -X POST https://tanova.ai/api/sync/upload \
     -H "X-Tanova-API-Key: tanova_sk_xxx" \
     -F "file=@test.pdf"
   ```

### High Resource Usage

**Symptoms:** CPU or memory usage higher than expected

**Causes:**
- Very large files (100+ MB PDFs)
- Thousands of files added simultaneously
- Recursive folder with millions of files
- Corrupted file causing infinite retry loop

**Solutions:**
1. Add file size limit check
2. Implement rate limiting (see above)
3. Exclude unnecessary subfolders
4. Monitor with `top` or `htop`

### Duplicate Files

**Symptoms:** Same file synced multiple times

**Causes:**
- Sync history file deleted/corrupted
- File modified (different checksum)
- Multiple sync services running

**Solutions:**
1. Check sync history: `cat ~/.tanova/sync_history.json`
2. Verify only one instance: `ps aux | grep tanova_sync`
3. Tanova handles duplicates gracefully (no data loss)

---

## Cost & Performance Estimates

### Resource Requirements

| Deployment Size | Files/Day | CPU | RAM | Disk | Network |
|----------------|-----------|-----|-----|------|---------|
| **Small** (1-10 CVs/day) | 10 | < 1% | 50 MB | 100 MB | 10 MB/day |
| **Medium** (10-100 CVs/day) | 100 | 1-5% | 100 MB | 500 MB | 100 MB/day |
| **Large** (100-1000 CVs/day) | 1000 | 5-10% | 200 MB | 1 GB | 1 GB/day |

### Pricing Impact

- **API calls:** Free (included with Tanova subscription)
- **Infrastructure:** Minimal (can run on any existing server)
- **Storage:** S3 costs for CV files (~$0.023/GB/month)

---

## Update Procedure

### Docker

```bash
# Pull latest image
docker-compose pull

# Restart with new version
docker-compose up -d

# Verify
docker-compose logs tanova-sync
```

### Binary

```bash
# Download new version
wget https://tanova.ai/downloads/tanova-sync-v1.1.0.exe

# Stop service
nssm stop TanovaSync

# Replace binary
cp tanova-sync-v1.1.0.exe "C:\Program Files\Tanova\tanova-sync.exe"

# Start service
nssm start TanovaSync
```

### Python Script

```bash
# Backup current version
cp tanova_sync.py tanova_sync.py.backup

# Download new version
wget https://tanova.ai/downloads/tanova_sync.py

# Restart service
sudo systemctl restart tanova-sync
```

---

## Support & Resources

### Documentation
- Main docs: [/docs/CV_SYNC_SERVICE.md](./CV_SYNC_SERVICE.md)
- GDPR guide: [/docs/CV_SYNC_GDPR_QUICK_GUIDE.md](./CV_SYNC_GDPR_QUICK_GUIDE.md)
- API reference: https://tanova.ai/docs/api

### Getting Help
- Email support: support@tanova.ai
- GitHub issues: https://github.com/tanova-ai/sync-service/issues
- Enterprise support: Available for paid plans

### Version History
- v1.0.0 (2025-12-04): Initial release

---

## Conclusion

**Current State:** The Python sync script is **functional and safe** for SMB deployment.

**Recommendations by Organization Type:**

| Organization Type | Recommended Approach | Estimated Setup Time |
|-------------------|---------------------|---------------------|
| **Startup / Small Business** | Python script with systemd | 30 minutes |
| **Modern IT (Docker-savvy)** | Docker container | 15 minutes |
| **Traditional Enterprise** | Standalone binary + NSSM | 1 hour |
| **Large Enterprise** | Docker + centralized logging + monitoring | 4 hours |

**Priority Improvements:**
1. 🔴 **Critical:** Add to enterprise feature roadmap (health checks, syslog)
2. 🟡 **High:** Create Docker image and binary releases
3. 🟢 **Medium:** Add monitoring/metrics
4. 🟢 **Low:** Auto-update mechanism

The sync service is **ready for production use** with appropriate deployment method for your infrastructure.
