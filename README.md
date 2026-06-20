# Overleaf Resume Syncer 🔄📄

Overleaf is a fantastic LaTeX editor for writing resumes, but the free-tier plan lacks Git integration and cloud drive sync. Every time you update your resume, you have to manually download the new PDF for sharing—which quickly becomes tedious.

**Overleaf Resume Syncer** is a GitHub Action that automatically fetches the latest PDF and LaTeX source from your Overleaf project, commits it to your GitHub repository (useful for GitHub Pages hosting), and uploads it directly to your Google Drive.

---

## Key Features

- **Automated Sync**: Triggers on a schedule (e.g. every Monday) or manually via `workflow_dispatch`.
- **Selenium Scraper**: Simulates a real browser session to bypass Overleaf's anti-scraping protections.
- **Direct Google Drive Upload**: Uploads directly from the runner to your Google Drive—eliminating dependency on any external web hosting services.
- **Conflict-Free Git Pushing**: Uses a robust backup-reset-restore sequence to bypass git merge/rebase conflicts on binary PDF files, ensuring the remote repository is always safely updated.
- **Secrets-Driven Security**: Sensitive links and credentials are kept private using GitHub Secrets.

---

## How It Works

1. **Scraping**: A headless Selenium browser visits your view-only Overleaf share link. It extracts the raw LaTeX code directly from WebSocket logs and downloads the compiled PDF.
2. **Source Diffing**: It compares the new LaTeX code with the existing `resume.tex`. If no changes are detected, it skips the remaining steps.
3. **Conflict-Free Commit**: If changes exist, the action:
   - Temporarily backs up the new resume files.
   - Resets the local workspace to match the latest remote commit.
   - Overwrites the old files and commits them. This ensures there are **never merge conflicts** on binary files.
4. **Direct Drive Sync**: Uses your Google Service Account key (passed securely via environment variables) to update your existing resume PDF in-place on Google Drive.

---

## Action Inputs (`action.yml`)

| Input | Description | Required |
| :--- | :--- | :--- |
| `overleaf_url` | Your Overleaf view-only sharing link (Share -> Turn on link sharing -> view-only link). | **Yes** |
| `github_token` | The GitHub token for authentication (use `${{ secrets.GITHUB_TOKEN }}`). | **Yes** |
| `gdrive_link` | Sharing link to the specific PDF file in your Google Drive to be updated. | No |
| `gdrive_service_account_key` | Entire JSON content of your Google Service Account credentials. | No |

---

## Example Usage

Create a workflow file (e.g. `.github/workflows/sync-resume.yml`):

```yaml
name: Sync Overleaf Resume

on:
  schedule:
    - cron: '0 0 * * 1' # Every Monday at 00:00 UTC
  workflow_dispatch:    # Allows manual trigger

permissions:
  contents: write

jobs:
  sync-resume:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: sahitya1903/overleaf-resume-syncer@main
        with:
          overleaf_url: ${{ secrets.OVERLEAF_URL }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
          
          # Optional: Google Drive sync configuration
          gdrive_link: ${{ secrets.GDRIVE_LINK }}
          gdrive_service_account_key: ${{ secrets.GDRIVE_SERVICE_ACCOUNT }}
```

---

## Setup Guide

### Step 1: Get the Overleaf Share Link
1. Open your project on Overleaf.
2. Click **Share** at the top right.
3. Turn on **Link Sharing** and copy the **view-only link**.

### Step 2: Set up a Google Service Account (Optional)
If you want to sync your resume to Google Drive:
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project and enable the **Google Drive API**.
3. Navigate to **IAM & Admin > Service Accounts** and click **Create Service Account**.
4. Once created, click on the Service Account, go to the **Keys** tab, select **Add Key > Create New Key > JSON**, and download the file.
5. Create a blank PDF file named `resume.pdf` in your Google Drive. 
6. Share this file with the Service Account's email address (e.g. `your-uploader@...iam.gserviceaccount.com`) giving it **Editor** permissions. Copy the share link of the file.

### Step 3: Add Secrets to GitHub
In your GitHub repository, navigate to **Settings > Secrets and variables > Actions** and add the following repository secrets:

- `OVERLEAF_URL`: The view-only sharing link from Step 1.
- `GDRIVE_LINK`: The Google Drive file link from Step 2 (e.g. `https://drive.google.com/file/d/.../view?...`).
- `GDRIVE_SERVICE_ACCOUNT`: The **entire** JSON text content of the downloaded service account key file.