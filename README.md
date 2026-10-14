# Resume Syncer

**Resume Syncer** is a serverless GitHub Action that automatically syncs your latest PDF and LaTeX source from Overleaf to your GitHub repository and, optionally, Google Drive.

> [!IMPORTANT]
> Run this action in a **private repository** to protect your personal contact details, while using the **Google Drive Sync** feature to update a public-facing resume link.

---

## Key Features & How It Works

- **Automated Sync & Diffing**: Runs on a cron schedule or manual trigger, comparing the LaTeX source to skip execution if no changes are detected.
- **Selenium WebSocket Scraper**: Uses headless Chrome to bypass Overleaf protections and recursively extract the LaTeX code from WebSocket performance logs.
- **Conflict-Free Git Commits**: Resets onto the latest remote commit while keeping the new files in the working tree, so the PDF and LaTeX source are committed without merge/rebase conflicts.
- **Direct Google Drive Sync**: Updates your public resume PDF in-place on Google Drive using a self-contained Python script.
- **Local Debugging Support**: Built to run locally on your machine for easy testing and debugging without crashing on missing GitHub environments.

---

## Action Inputs (`action.yml`)

| Input | Description | Required |
| :--- | :--- | :--- |
| `overleaf_url` | Your Overleaf view-only sharing link (Share -> Turn on link sharing -> view-only link). | **Yes** |
| `github_token` | The GitHub token for authentication (use `${{ secrets.GITHUB_TOKEN }}`). | **Yes** |
| `resume_name` | Base name of the synced files (default `resume` → `resume.tex`, `resume.pdf`). Use a different name per resume when syncing several. | No |
| `gdrive_link` | Sharing link or raw File ID of the specific PDF file in your Google Drive to be updated. | No |
| `gdrive_service_account_key` | Entire JSON content of your Google Service Account credentials. | No |

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
      - uses: sahitya1903/resume-syncer@v1
        with:
          overleaf_url: ${{ secrets.OVERLEAF_URL }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
          
          # Optional: Google Drive sync configuration
          gdrive_link: ${{ secrets.GDRIVE_LINK }}
          gdrive_service_account_key: ${{ secrets.GDRIVE_SERVICE_ACCOUNT }}
```

### Syncing Multiple Resumes

To sync several Overleaf projects (e.g. a core and an IT resume) into the same repository, add one step per resume with a distinct `resume_name`. Each one gets its own Overleaf link and Drive file, while the service account key can be shared:

```yaml
    steps:
      - uses: sahitya1903/resume-syncer@v1
        with:
          resume_name: core # Syncs core.tex and core.pdf
          overleaf_url: ${{ secrets.OVERLEAF_URL_CORE }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
          gdrive_link: ${{ secrets.GDRIVE_LINK_CORE }}
          gdrive_service_account_key: ${{ secrets.GDRIVE_SERVICE_ACCOUNT }}

      - uses: sahitya1903/resume-syncer@v1
        with:
          resume_name: it # Syncs it.tex and it.pdf
          overleaf_url: ${{ secrets.OVERLEAF_URL_IT }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
          gdrive_link: ${{ secrets.GDRIVE_LINK_IT }}
          gdrive_service_account_key: ${{ secrets.GDRIVE_SERVICE_ACCOUNT }}
```

Keep these as sequential steps in one job rather than parallel jobs, so their commits don't race each other when pushing.

---

## Setup Guide

### Step 1: Get the Overleaf Share Link
1. Click **Share** at the top right of your Overleaf project, enable **Link Sharing**, and copy the **view-only link**.

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
- `GDRIVE_LINK`: The Google Drive file link from Step 2 (e.g. `https://drive.google.com/file/d/.../view?...`) or the raw File ID directly.
- `GDRIVE_SERVICE_ACCOUNT`: The **entire** JSON text content of the downloaded service account key file.

When syncing multiple resumes, add an `OVERLEAF_URL_<NAME>` and `GDRIVE_LINK_<NAME>` pair per resume (e.g. `OVERLEAF_URL_CORE`, `GDRIVE_LINK_CORE`) and share the Drive file of each one with the service account.

> [!IMPORTANT]
> Always use **GitHub Secrets** (and not GitHub Variables) for sensitive values like `GDRIVE_SERVICE_ACCOUNT` (which contains a private key) and `OVERLEAF_URL` (which contains a view token), to ensure they remain encrypted and are masked in workflow logs.

### Step 4: Ignore Local Synced Files
Add these lines to your `.gitignore` to prevent auto-generated files from cluttering your local workspace (the workflow will still commit them using force-add):
```gitignore
*.pdf
*.tex
.secrets
```

---

## Local Execution & Debugging

You can run the sync pipeline locally using the provided automated script `run_local.py`:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create a `.secrets` file** in the root of the project to store your credentials (this file is already gitignored):
   ```ini
   OVERLEAF_URL=https://www.overleaf.com/read/xxxxxx
   GDRIVE_LINK=https://drive.google.com/file/d/yyyyyy/view?usp=drive_link
   
   # Wrap the entire JSON block in single quotes (even if it spans multiple lines)
   GDRIVE_SERVICE_ACCOUNT='{
     "type": "service_account",
     "project_id": "...",
     "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
     ...
   }'
   ```

   To sync multiple resumes, use a suffixed `OVERLEAF_URL_<NAME>` (and optionally `GDRIVE_LINK_<NAME>`) per resume instead. Each one is synced to `<name>.tex` and `<name>.pdf`, and they all share `GDRIVE_SERVICE_ACCOUNT`:
   ```ini
   OVERLEAF_URL_CORE=https://www.overleaf.com/read/xxxxxx
   GDRIVE_LINK_CORE=https://drive.google.com/file/d/yyyyyy/view?usp=drive_link
   OVERLEAF_URL_IT=https://www.overleaf.com/read/zzzzzz
   GDRIVE_LINK_IT=https://drive.google.com/file/d/wwwwww/view?usp=drive_link
   ```

3. **Run the local sync script:**
   ```bash
   python run_local.py
   ```
   This script automatically reads your `.secrets` file, parses the multi-line service account key, downloads the files using your local Chrome browser, and syncs them to Google Drive if credentials are provided and the resume has changed. Every resume configured in `.secrets` is synced in turn.

---

## Credits

This project is inspired by and built upon the work of the original creator. Special thanks to [Sbrjt](https://github.com/Sbrjt) for the original project [overleaf-resume-syncer](https://github.com/Sbrjt/overleaf-resume-syncer).

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.