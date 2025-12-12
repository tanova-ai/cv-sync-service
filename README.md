# Tanova CV Sync Service

**Automatically sync CV files from your computer to Tanova - Perfect for recruitment agencies**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

> **Free, open-source tool** for recruitment agencies receiving CVs via email, shared drives, or local storage. Watches a folder and automatically uploads CVs to your Tanova account for AI-powered evaluation.

---

## Why Use This?

### The Problem
Recruitment agencies receive CVs from multiple sources:
- 📧 **Email attachments** from candidates
- 📁 **Shared drives** (Dropbox, Google Drive, OneDrive)
- 💼 **Internal folders** organized by role/client

Manually uploading each CV to Tanova is time-consuming and error-prone.

### The Solution
The CV Sync Service **automatically watches your CV folder** and:
- ✅ Uploads new CVs instantly to Tanova
- ✅ Detects duplicates (no re-uploading)
- ✅ Extracts metadata (email, job hints from filename/folder)
- ✅ Handles 10,000+ CVs with high performance
- ✅ Works with PDF, DOCX, TXT, Markdown files

### The Result
- **Save hours** of manual CV uploads
- **Never miss a candidate** - all CVs synced automatically
- **Organize efficiently** - folder structure becomes job categories
- **Scale infinitely** - handles agencies with thousands of monthly applications

---

## Quick Start

### 1. Install Dependencies

```bash
pip3 install watchdog requests
```

### 2. Clone or Download

```bash
# Clone the repository
git clone https://github.com/tanova-ai/cv-sync-service.git
cd cv-sync-service

# Or download directly
curl -O https://raw.githubusercontent.com/tanova-ai/cv-sync-service/main/tanova_sync.py
curl -O https://raw.githubusercontent.com/tanova-ai/cv-sync-service/main/requirements.txt
```

### 3. Create Configuration File

Copy the example config:

```bash
cp tanova-config.json.example tanova-config.json
```

Edit `tanova-config.json`:

```json
{
  "folder_path": "/path/to/your/CVs",
  "api_key": "tanova_sk_your_key_here",
  "tanova_url": "https://tanova.ai",
  "max_workers": 5
}
```

**Get your API key:** Log in to Tanova → Settings → API Keys → Create New Key

### 4. Run the Service

```bash
python3 tanova_sync.py
```

**That's it!** The service will:
1. Scan your folder for existing CVs
2. Upload any new files
3. Watch for new CVs added to the folder
4. Run continuously until you stop it (Ctrl+C)

---

## Features

### ⚡ High Performance
- **Concurrent uploads:** 5 workers process files simultaneously
- **100 CVs:** ~5 minutes
- **1,000 CVs:** ~45 minutes
- **10,000 CVs:** ~7 hours

### 🔍 Smart Duplicate Detection
- SHA-256 checksum-based duplicate detection
- Checks local cache before uploading
- Server-side duplicate verification
- Never creates duplicate candidates

### 📊 Progress Reporting
- Real-time progress updates every 10 files
- Shows upload count, duplicates skipped, errors
- Time estimates for large batches

### 🛡️ Robust Error Handling
- Automatic retries on network failures
- Graceful degradation (continues on errors)
- Detailed error logging
- Connection pooling for reliability

### 📁 All File Types Supported
- PDF (most common)
- DOCX, DOC (Microsoft Word)
- TXT (plain text)
- MD (Markdown resumes)

### 🧠 Smart Metadata Extraction
- **Email from filename:** `john_doe_john@example.com.pdf` → extracts email
- **Job hints from folder:** `/CVs/Backend Engineer/resume.pdf` → job hint: "Backend Engineer"
- **Recursive scanning:** All subfolders processed automatically

---

## Folder Organization Examples

### Example 1: Organize by Role

```
CVs/
├── Backend Engineer/
│   ├── john_smith_resume.pdf
│   └── jane_doe_cv.pdf
├── Frontend Developer/
│   └── alex_johnson.pdf
└── Product Manager/
    └── sarah_wilson.docx
```

The sync service will:
- Extract job hint "Backend Engineer" from folder name
- Tag candidates accordingly in Tanova

### Example 2: Organize by Client

```
CVs/
├── Client_Acme_Corp/
│   ├── Senior_Engineer/
│   └── Junior_Designer/
└── Client_TechStartup/
    └── Full_Stack_Developer/
```

### Example 3: Email-Based Naming

```
CVs/
├── john_smith_john@example.com.pdf
├── jane_doe_jane.doe@company.com.docx
└── alex_alex123@email.com.pdf
```

Emails are automatically extracted and stored in Tanova.

---

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `folder_path` | Path to CV folder (can be relative or absolute) | *Required* |
| `api_key` | Your Tanova API key (get from Settings → API Keys) | *Required* |
| `tanova_url` | Tanova instance URL | `https://tanova.ai` |
| `max_workers` | Number of concurrent upload workers | `5` |
| `retry_count` | Number of retries on upload failure | `3` |
| `watch_mode` | Enable continuous watching (vs one-time sync) | `true` |

---

## Cache Management

The sync service maintains a local cache at `~/.tanova/sync_history.json` to avoid re-uploading files.

### Clear Cache

```bash
rm ~/.tanova/sync_history.json
```

Use when:
- Testing the sync service
- Want to force re-upload
- Cache becomes corrupted

**Note:** Server still checks for duplicates using checksums, so clearing cache won't create duplicates in Tanova.

---

## Running as a Background Service

### macOS/Linux (systemd)

Create `/etc/systemd/system/tanova-sync.service`:

```ini
[Unit]
Description=Tanova CV Sync Service
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/cv-sync-service
ExecStart=/usr/bin/python3 tanova_sync.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable tanova-sync
sudo systemctl start tanova-sync
```

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task → "Tanova CV Sync"
3. Trigger: "When the computer starts"
4. Action: Start a program → `python.exe`
5. Arguments: `C:\path\to\tanova_sync.py`

### macOS (launchd)

Create `~/Library/LaunchAgents/com.tanova.sync.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.tanova.sync</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/tanova_sync.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Load:

```bash
launchctl load ~/Library/LaunchAgents/com.tanova.sync.plist
```

---

## Documentation

- **[Setup Guide](docs/CV_SYNC_SERVICE.md)** - Complete installation and configuration guide
- **[Enterprise Deployment](docs/SYNC_SERVICE_ENTERPRISE_DEPLOYMENT.md)** - Running at scale, monitoring, GDPR compliance
- **[Performance Comparison](docs/SYNC_PERFORMANCE_COMPARISON.md)** - v1 vs v2 benchmarks
- **[GDPR Quick Guide](docs/CV_SYNC_GDPR_QUICK_GUIDE.md)** - Data privacy and compliance

---

## Performance Benchmarks

**Tested on MacBook Pro M1, 50 Mbps connection:**

| CVs | v1.0 (Legacy) | v2.0 (Current) | Speedup |
|-----|---------------|----------------|---------|
| 100 | 20 min | 5 min | **4x faster** |
| 1,000 | 3.5 hours | 45 min | **4.7x faster** |
| 10,000 | 35 hours | 7 hours | **5x faster** |

**Key improvements in v2.0:**
- Concurrent uploads (5 workers)
- Connection pooling
- Batch cache updates
- Checksum caching

---

## Troubleshooting

### "API key invalid"
- Verify API key in `tanova-config.json`
- Ensure key starts with `tanova_sk_`
- Check you're an admin in Tanova

### "Permission denied" on folder
- Check folder path exists
- Verify read permissions
- Use absolute path instead of relative

### Uploads are slow
- Increase `max_workers` (try 10)
- Check internet connection speed
- Verify files aren't too large (>10MB)

### Duplicates still uploading
- Clear cache: `rm ~/.tanova/sync_history.json`
- Ensure filenames are consistent
- Check server-side duplicates in Tanova

### Service crashes
- Check Python version: `python3 --version` (need 3.7+)
- Reinstall dependencies: `pip3 install -r requirements.txt`
- Check logs in terminal output

---

## Requirements

- **Python 3.7 or higher**
- **Tanova account** (sign up at [tanova.ai](https://tanova.ai))
- **API key** (create in Settings → API Keys)

---

## License

MIT License - Free to use, modify, and distribute

See [LICENSE](LICENSE) for full terms.

---

## About Tanova

**Tanova** is an AI-powered candidate evaluation platform that goes beyond keyword matching to find exceptional talent.

- **Website:** [tanova.ai](https://tanova.ai)
- **API Docs:** [tanova.ai/api-docs](https://tanova.ai/api-docs)
- **7D Framework:** [github.com/tanova-ai/7d-framework](https://github.com/tanova-ai/7d-framework)
- **Skills Taxonomy:** [github.com/tanova-ai/skills-taxonomy](https://github.com/tanova-ai/skills-taxonomy)

### Why Tanova?

Traditional ATS systems reject 75% of qualified candidates using keyword matching. Tanova uses the 7D Framework to evaluate candidates across seven dimensions:

1. **Qualification Match** - Skills alignment
2. **Capability Confidence** - Evidence of ability
3. **Situational Stability** - Likelihood to join/stay
4. **Reward Potential** - Upside if they succeed
5. **Cultural Fit** - Work style alignment
6. **Career Trajectory** - Growth pattern
7. **Compensation Alignment** - Salary fit

**Result:** Find 3-5x more qualified candidates, including "hidden gems" that traditional systems miss.

---

## Contributing

Found a bug or have a feature request? Open an issue or submit a PR!

- **Issues:** [github.com/tanova-ai/cv-sync-service/issues](https://github.com/tanova-ai/cv-sync-service/issues)
- **Email:** [hello@tanova.ai](mailto:hello@tanova.ai)

---

## Version

**Current:** v2.0 (Optimized for high volume)

See [CHANGELOG](CHANGELOG.md) for version history.

---

**Made with ❤️ by [Tanova](https://tanova.ai) - Find talent that traditional ATS systems miss.**
