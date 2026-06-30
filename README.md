# Resume Syncer

Overleaf is a fantastic LaTeX editor for writing resumes, but the free-tier plan lacks Git integration and cloud drive sync. Every time you update your resume, you have to manually download the new PDF for sharing—which quickly becomes tedious.

**Resume Syncer** is a fully self-contained, serverless GitHub Action that automatically fetches the latest PDF and LaTeX source from your Overleaf project, commits it to your GitHub repository (useful for GitHub Pages hosting), uploads it directly to your Google Drive, and pushes the compiled PDF to your external portfolio repository to trigger CI/CD pipelines (e.g., Azure Web App deployment).

> [!IMPORTANT]
> **Privacy & Security Best Practice**: Storing your PDF resume in a public GitHub repository exposes your personal contact details (phone, email, home address) to scrapers, bots, and search engines. 
> To protect your privacy, we recommend running this action in a **private repository** to safely archive your LaTeX source and PDF history, while using the built-in **Google Drive Sync** feature to update a public-facing resume link.

---

## Key Features

- **Automated Sync**: Triggers automatically on a cron schedule (every 24 hours) or manually via `workflow_dispatch`.
- **Selenium Scraper**: Simulates a real browser session to bypass Overleaf's anti-scraping protections.
- **Line Ending Normalization**: Automatically normalizes CRLF vs. LF line endings to prevent redundant ghost commits of the binary PDF.
- **Cross-Repository Sync**: Pushes the compiled `resume.pdf` to a specific directory (like `public/resume.pdf`) in your external portfolio/website repository, triggering automated rebuilds/deployments.
- **Direct Google Drive Sync**: Updates your existing resume PDF in-place on Google Drive using a self-contained Python script within the runner—eliminating the need to host any external backend servers or expose public API endpoints.
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
4. **Portfolio Push**: If configured, clones the target portfolio repository, copies the new PDF to `public/resume.pdf`, and commits/pushes to trigger any automated deployments.
5. **Direct Drive Sync**: Uses your Google Service Account key (passed securely via environment variables) to update your existing resume PDF in-place on Google Drive.

---

## Action Inputs (`action.yml`)

| Input | Description | Required |
| :--- | :--- | :--- |
| `overleaf_url` | Your Overleaf view-only sharing link (Share -> Turn on link sharing -> view-only link). | **Yes** |
| `github_token` | The GitHub token for authentication (use `${{ secrets.GITHUB_TOKEN }}`). | **Yes** |
| `gdrive_link` | Sharing link or raw File ID of the specific PDF file in your Google Drive to be updated. | No |
| `gdrive_service_account_key` | Entire JSON content of your Google Service Account credentials. | No |
| `portfolio_repo` | Target portfolio repository path (e.g., `username/repo`). | No |
| `portfolio_token` | GitHub Personal Access Token (PAT) with write access to target repository. | No |

---

## Example Usage

Create a workflow file (e.g. `.github/workflows/sync-resume.yml`):

```yaml
name: Resume Syncer

on:
  schedule:
    - cron: '0 0 * * *' # Every 24 hours
  workflow_dispatch:    # Allows manual trigger

permissions:
  contents: write

jobs:
  sync-resume:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7 
      - uses: sahitya1903/resume-syncer@v1
        with:
          overleaf_url: ${{ secrets.OVERLEAF_URL }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
          
          # Optional: Google Drive sync configuration
          gdrive_link: ${{ secrets.GDRIVE_LINK }}
          gdrive_service_account_key: ${{ secrets.GDRIVE_SERVICE_ACCOUNT }}

          # Optional: Portfolio repository sync configuration
          portfolio_repo: ${{ secrets.PORTFOLIO_REPO }}
          portfolio_token: ${{ secrets.PORTFOLIO_TOKEN }}
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

### Step 3: Set up Portfolio Repository Sync (Optional)
If you want to sync your resume directly to your portfolio repository:
1. Go to your GitHub account **Settings > Developer Settings > Personal Access Tokens (classic or fine-grained)**.
2. Generate a new token with **Write** permissions (specifically `contents:write` for target repo).
3. Copy this token.

### Step 4: Add Secrets to GitHub
In your GitHub repository, navigate to **Settings > Secrets and variables > Actions** and add the following repository secrets:

- `OVERLEAF_URL`: The view-only sharing link from Step 1.
- `GDRIVE_LINK`: The Google Drive file link from Step 2 (e.g. `https://drive.google.com/file/d/.../view?...`) or the raw File ID directly.
- `GDRIVE_SERVICE_ACCOUNT`: The **entire** JSON text content of the downloaded service account key file.
- `PORTFOLIO_REPO`: The target portfolio repository path (e.g., `username/repo`).
- `PORTFOLIO_TOKEN`: The Personal Access Token generated in Step 3.

### Step 5: Local Clutter Prevention (.gitignore)
Since the Action compiles and updates the resume files dynamically, you might want to prevent these auto-generated files from cluttering your local development workspace. 

You can safely add the following lines to your local `.gitignore`:
```gitignore
# Ignore auto-synced resume files locally
resume.pdf
resume.tex
temp/
```
The GitHub Action is configured to force-add (`git add -f`) these files during the sync, so they will still be committed to the remote repository successfully even if they are in your `.gitignore`.

---

## Credits

This project is inspired by and built upon the work of the original creator. Special thanks to [Sbrjt](https://github.com/Sbrjt) for the original project [overleaf-resume-syncer](https://github.com/Sbrjt/overleaf-resume-syncer).

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.