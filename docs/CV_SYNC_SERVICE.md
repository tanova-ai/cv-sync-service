# CV Sync Service - Complete Guide

**Automatically sync CV files from your computer to Tanova**

---

## 🎯 What is the CV Sync Service?

The CV Sync Service is a lightweight application that runs on your computer and automatically uploads CV files from a folder to your Tanova account. Perfect for recruitment agencies that receive CVs via email, shared drives, or local storage.

### Key Features

✅ **Automatic Syncing** - Watches your folder for new/updated CVs and uploads them instantly
✅ **Duplicate Detection** - Never upload the same CV twice (uses SHA-256 checksums)
✅ **Recursive Scanning** - Scans all subfolders automatically
✅ **Smart Metadata** - Extracts emails and job hints from filenames/folder names
✅ **Cross-Platform** - Works on Windows, macOS, and Linux
✅ **Secure** - Uses API keys for authentication
✅ **Retry Logic** - Automatically retries failed uploads

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step 1: Create an API Key](#step-1-create-an-api-key)
3. [Step 2: Install the Sync Service](#step-2-install-the-sync-service)
4. [Step 3: Configure the Service](#step-3-configure-the-service)
5. [Step 4: Run the Service](#step-4-run-the-service)
6. [Advanced Configuration](#advanced-configuration)
7. [Folder Organization Tips](#folder-organization-tips)
8. [Running as a Background Service](#running-as-a-background-service)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- **Python 3.7 or higher** installed on your computer
  - Windows: Download from [python.org](https://www.python.org/downloads/)
  - macOS: Comes pre-installed, or use `brew install python3`
  - Linux: Usually pre-installed, or use `sudo apt install python3`

- **Admin access to Tanova** (to create API keys)

---

## Step 1: Create an API Key

### 1.1 Log in to Tanova

Go to [tanova.ai](https://tanova.ai) and log in with your account.

### 1.2 Navigate to Settings

Click on your profile icon → **Settings** → **Integrations** tab

### 1.3 Create a New API Key

1. Click **"Create API Key"**
2. Enter a descriptive name (e.g., "Office Sync Service")
3. Choose an expiration period (optional):
   - **Never expires** (recommended for permanent setups)
   - 30/90/365 days (for temporary or testing)
4. Click **"Create API Key"**

### 1.4 Save Your API Key

⚠️ **IMPORTANT**: Copy your API key immediately!

```
tanova_sk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

You will **not** be able to see this key again. Store it securely (we recommend using a password manager).

---

## Step 2: Install the Sync Service

### 2.1 Download the Sync Service

Download the latest version from your Tanova dashboard:
- Go to **Settings → Integrations**
- Click **"Download Sync Service"**
- Or get it from: [github.com/tanova-ai/sync-service](https://github.com/your-org/sync-service)

### 2.2 Extract the Files

Extract the ZIP file to a location on your computer:
- Windows: `C:\Program Files\TanovaSync\`
- macOS/Linux: `~/TanovaSync/`

### 2.3 Install Dependencies

Open a terminal/command prompt in the extracted folder and run:

```bash
pip3.7 install -r requirements.txt
```

This installs two packages:
- `requests` (for API communication)
- `watchdog` (for folder monitoring)

---

## Step 3: Configure the Service

### 3.1 Create Configuration File

Copy the example config file:

```bash
cp tanova-config.json.example tanova-config.json
```

### 3.2 Edit Configuration

Open `tanova-config.json` in a text editor and fill in your details:

```json
{
  "folder_path": "/path/to/your/cv/folder",
  "api_key": "tanova_sk_your_key_here",
  "tanova_url": "https://tanova.ai",
  "retry_count": 3,
  "retry_delay": 5
}
```

**Configuration Options:**

| Option | Description | Example |
|--------|-------------|---------|
| `folder_path` | Full path to your CV folder | `C:\CVs` or `/Users/john/CVs` |
| `api_key` | Your Tanova API key | `tanova_sk_abc123...` |
| `tanova_url` | Tanova server URL | `https://tanova.ai` |
| `retry_count` | Number of retry attempts | `3` |
| `retry_delay` | Seconds between retries | `5` |

---

## Step 4: Run the Service

### 4.1 Test Run

Run the service manually to test:

```bash
python tanova_sync.py
```

You should see output like:

```
═══════════════════════════════════════════════════════════
  Tanova CV Sync Service
  Version 1.0.0
═══════════════════════════════════════════════════════════

✓ Loaded config from tanova-config.json
📂 Scanning for existing CV files in: /Users/john/CVs
📄 Found 15 CV files
✓ Synced: John_Doe_Resume.pdf -> Candidate ID: 123
✓ Synced: Jane_Smith_CV.docx -> Candidate ID: 124
⏭️  Skipped (already synced): Alice_Johnson.pdf
...
📊 Initial sync complete:
   ✓ Synced: 12
   ⏭️  Skipped: 3
   ✗ Failed: 0

👀 Watching folder (including subfolders): /Users/john/CVs
🔑 Using API key: tanova_sk_abc12...
Press Ctrl+C to stop
```

### 4.2 Test with a New File

1. Keep the service running
2. Drop a CV file into your folder
3. Watch the console - you should see:
   ```
   ✓ Synced: New_Candidate_CV.pdf -> Candidate ID: 125
   ```

### 4.3 Stop the Service

Press `Ctrl+C` to stop the service.

---

## Advanced Configuration

### Environment Variables

Instead of using `tanova-config.json`, you can use environment variables:

```bash
export TANOVA_FOLDER_PATH="/path/to/cvs"
export TANOVA_API_KEY="tanova_sk_your_key"
export TANOVA_URL="https://tanova.ai"

python tanova_sync.py
```

---

## Folder Organization Tips

### Organize by Job Position

```
/CVs/
  /Software Engineer/
    john_doe.pdf
    jane_smith.pdf
  /Sales Manager/
    bob_jones.docx
  /Marketing Specialist/
    alice_williams.pdf
```

The sync service will extract "Software Engineer", "Sales Manager", etc. as tags!

### Include Email in Filename

```
/CVs/
  john.doe@example.com_Resume.pdf
  jane.smith@company.com_CV.docx
```

The service will automatically extract emails from filenames.

### Supported File Types

- `.pdf` (recommended)
- `.docx` / `.doc`
- `.txt`
- `.md`

---

## Running as a Background Service

For production use, you'll want the sync service to run automatically in the background.

### Windows (Run as Service)

#### Option A: Using NSSM (Recommended)

1. Download NSSM from [nssm.cc](https://nssm.cc)
2. Open Command Prompt as Administrator
3. Run:
   ```cmd
   nssm install TanovaSync "C:\Python39\python.exe" "C:\TanovaSync\tanova_sync.py"
   nssm start TanovaSync
   ```

#### Option B: Using Task Scheduler

1. Open **Task Scheduler**
2. Create New Task:
   - **Name**: Tanova CV Sync
   - **Trigger**: At startup
   - **Action**: Start program
   - **Program**: `C:\Python39\python.exe`
   - **Arguments**: `C:\TanovaSync\tanova_sync.py`
   - **Start in**: `C:\TanovaSync\`
3. Check "Run whether user is logged on or not"
4. Save and run the task

### macOS (Using launchd)

1. Create service file:
   ```bash
   nano ~/Library/LaunchAgents/com.tanova.sync.plist
   ```

2. Paste this content:
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>Label</key>
       <string>com.tanova.sync</string>
       <key>ProgramArguments</key>
       <array>
           <string>/usr/local/bin/python3</string>
           <string>/Users/YourUsername/TanovaSync/tanova_sync.py</string>
       </array>
       <key>WorkingDirectory</key>
       <string>/Users/YourUsername/TanovaSync</string>
       <key>RunAtLoad</key>
       <true/>
       <key>KeepAlive</key>
       <true/>
       <key>StandardOutPath</key>
       <string>/Users/YourUsername/TanovaSync/sync.log</string>
       <key>StandardErrorPath</key>
       <string>/Users/YourUsername/TanovaSync/sync-error.log</string>
   </dict>
   </plist>
   ```

3. Load and start:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.tanova.sync.plist
   launchctl start com.tanova.sync
   ```

### Linux (Using systemd)

1. Create service file:
   ```bash
   sudo nano /etc/systemd/system/tanova-sync.service
   ```

2. Paste this content:
   ```ini
   [Unit]
   Description=Tanova CV Sync Service
   After=network.target

   [Service]
   Type=simple
   User=your-username
   WorkingDirectory=/home/your-username/TanovaSync
   ExecStart=/usr/bin/python3 /home/your-username/TanovaSync/tanova_sync.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start:
   ```bash
   sudo systemctl enable tanova-sync
   sudo systemctl start tanova-sync
   sudo systemctl status tanova-sync
   ```

4. View logs:
   ```bash
   sudo journalctl -u tanova-sync -f
   ```

---

## Troubleshooting

### "Permission Denied" Error

**Problem**: Can't read files in the folder

**Solution**:
- Windows: Right-click folder → Properties → Security → Give your user "Read" permission
- macOS/Linux: `chmod +r /path/to/cvs/*`

### "Invalid API Key" Error

**Problem**: API key not recognized

**Solutions**:
1. Check if you copied the key correctly (should start with `tanova_sk_`)
2. Verify the key hasn't expired (check in Settings → Integrations)
3. Make sure there are no extra spaces or quotes in the config file

### "Connection Error" or "Timeout"

**Problem**: Can't reach Tanova servers

**Solutions**:
1. Check your internet connection
2. Try accessing https://tanova.ai in your browser
3. Check if a firewall is blocking Python
4. Increase timeout in the script (edit `timeout=300` to `timeout=600`)

### Files Not Syncing

**Problem**: New files added but not uploaded

**Checklist**:
1. ✅ Is the service running? (Check terminal/task manager)
2. ✅ Is the file type supported? (.pdf, .docx, .doc, .txt, .md only)
3. ✅ Is the file fully written? (Service waits 1 second to ensure file is complete)
4. ✅ Check the console/logs for error messages

### Duplicate CVs Being Created

**Problem**: Same CV uploaded multiple times

**Explanation**: The sync service uses file **content** checksums, not filenames. If the CV content changes (even slightly), it's treated as a new candidate. This is usually the correct behavior (updated CVs should create new candidates).

**Solution** (if needed):
- The local cache tracks uploaded files at `~/.tanova/sync_history.json`
- If corrupted, delete this file to rebuild the history
- The service will re-scan but skip duplicates that already exist on the server

### Test Your API Key

Run this command to test connectivity:

```bash
curl -H "X-Tanova-API-Key: your_key_here" https://tanova.ai/api/sync/health
```

Expected response:
```json
{
  "success": true,
  "authenticated": true,
  "message": "API key is valid",
  "agency": "Your Agency Name",
  "permissions": {
    "canUpload": true,
    "canRead": false
  }
}
```

---

## Security Best Practices

### Protect Your API Key

- ❌ Don't commit config files to Git/version control
- ❌ Don't share your API key with others
- ✅ Use environment variables in shared environments
- ✅ Rotate keys periodically
- ✅ Delete keys you're no longer using

### Monitor API Key Usage

Check API key usage in **Settings → Integrations**:
- Last used timestamp
- Total request count
- Create alerts for suspicious activity

---

## 🔒 GDPR Compliance & Data Protection

### Legal Basis for Processing

When CVs are uploaded via the sync service, Tanova processes them under **GDPR Article 6(1)(f) - Legitimate Interest**:

> "Processing is necessary for the purposes of the legitimate interests pursued by the controller"

**The legitimate interest**: Recruitment agencies have a legitimate business interest in processing CVs sent to them for job opportunities.

### Important GDPR Requirements

#### ✅ What Tanova Does Automatically

1. **Automatic Data Retention**
   - CVs are automatically deleted after your configured retention period (default: 2 years)
   - Set in Settings → GDPR & Compliance → Candidate & CV Data Retention
   - Helps comply with GDPR storage limitation principle

2. **Data Minimization**
   - Only essential candidate information is extracted
   - No unnecessary personal data is collected

3. **Security Measures**
   - CVs encrypted in transit (HTTPS)
   - CVs stored securely in S3 with access controls
   - API keys for authentication
   - Audit logs of all access

4. **Data Subject Rights**
   - Candidates can request data deletion via your agency
   - Agencies can manually delete candidates at any time
   - Export functionality for data portability (Settings → GDPR)

#### ⚠️ What YOU Must Do (Legal Requirements)

1. **Inform Candidates About Automated Processing**

   You MUST inform candidates that their CVs may be processed automatically. Add this to:
   - Your website privacy policy
   - Email signatures when corresponding with candidates
   - Job postings

   **Example Notice:**
   ```
   "CVs sent to us may be processed using automated recruitment software
   to match candidates with suitable positions. By sending your CV, you
   acknowledge this processing under our legitimate business interest.
   See our privacy policy: [link]"
   ```

2. **Maintain a Privacy Policy**

   Your privacy policy must mention:
   - What data you collect (name, contact info, work history, skills)
   - Why you collect it (recruitment purposes)
   - How long you keep it (state your retention period)
   - Candidate rights (access, deletion, portability)
   - Automated decision-making (if using AI evaluations)

3. **Respect Candidate Rights**

   Candidates have the right to:
   - **Access**: Request a copy of their data (use Tanova's export feature)
   - **Rectification**: Correct inaccurate information (edit in Tanova)
   - **Erasure**: Request deletion (delete in Tanova)
   - **Object**: Object to processing (stop processing their application)
   - **Portability**: Get their data in machine-readable format (export feature)

4. **Document Your Legal Basis**

   Keep records showing:
   - Why you're processing CVs (legitimate interest assessment)
   - How candidates are informed about processing
   - Your data retention policies
   - How you handle deletion requests

### Legitimate Interest Assessment (LIA)

Under GDPR, you should document why legitimate interest applies:

**Example LIA for CV Sync Service:**

| Question | Answer |
|----------|--------|
| **What is the purpose?** | To efficiently process candidate applications for job vacancies |
| **Is it necessary?** | Yes - manual processing would delay candidate responses and reduce recruitment efficiency |
| **Is there a less intrusive way?** | No - candidates voluntarily send CVs for job opportunities |
| **What are the candidate's interests?** | Candidates want their applications processed quickly and fairly |
| **What are the risks?** | Low - only recruitment-relevant data is processed, with secure storage and automatic deletion |
| **Balancing test** | Business interest in efficient recruitment outweighs minimal privacy risk, as candidates expect their CVs to be processed when applying |

### Data Retention Settings

Configure in Tanova:

1. Go to **Settings → GDPR & Compliance**
2. Set **"Candidate & CV Data Retention"**
   - Recommended: **730 days (2 years)**
   - GDPR requires you don't keep data longer than necessary
3. After this period, CVs and candidate data are **automatically deleted**

### Handling Deletion Requests

If a candidate requests deletion:

1. Find candidate in Tanova
2. Click **"Delete"** or go to Settings → GDPR → Export & Delete Data
3. Confirm deletion - this:
   - Removes candidate record from database
   - Deletes CV file from S3 storage
   - Anonymizes any evaluation data (for analytics)
   - Logs the deletion (audit trail)

### GDPR Checklist for Sync Service

Before using the CV sync service, ensure:

- ☑️ You have a privacy policy mentioning automated CV processing
- ☑️ Your website/emails inform candidates about data processing
- ☑️ You've set appropriate data retention periods in Tanova
- ☑️ You have procedures to handle data subject requests
- ☑️ Only authorized staff have access to Tanova
- ☑️ API keys are stored securely (not in version control)
- ☑️ You've documented your legitimate interest assessment

### Need Legal Advice?

**⚠️ Important**: This documentation provides general GDPR guidance but is not legal advice. Consult with a data protection lawyer or DPO (Data Protection Officer) for your specific situation, especially if:

- You process sensitive categories of personal data (health, race, religion, etc.)
- You're a large organization (>250 employees)
- You process data about children
- You make solely automated decisions affecting candidates
- You transfer data internationally

### Useful Resources

- 📜 **GDPR Full Text**: https://gdpr-info.eu
- 📖 **ICO Guidance (UK)**: https://ico.org.uk/for-organisations/guide-to-data-protection/
- 🇪🇺 **EU Guidelines**: https://edpb.europa.eu
- 📋 **Legitimate Interest Template**: https://ico.org.uk/for-organisations/guide-to-data-protection/guide-to-the-general-data-protection-regulation-gdpr/legitimate-interests/how-do-we-apply-legitimate-interests-in-practice/

---

## Support

### Need Help?

- 📧 Email: support@tanova.ai
- 💬 Chat: Available in-app
- 📚 Documentation: https://docs.tanova.ai
- 🐛 Report bugs: https://github.com/tanova-ai/sync-service/issues

### Feature Requests

We'd love to hear your ideas! Email us at feedback@tanova.ai or use the in-app feedback button.

---

## Changelog

### v1.0.0 (December 2025)
- Initial release
- Recursive folder scanning
- SHA-256 duplicate detection
- Metadata extraction from paths/filenames
- Automatic retry logic
- Cross-platform support
