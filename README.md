Overleaf doesn’t provide a direct, hosted link to PDFs within its projects. Every time you make changes to your resume, you need to manually download the updated pdf for sharing.

This GitHub action automates fetching the latest pdf from overleaf and commits it to your GitHub repo, from where it can be easily hosted and shared.

## Example Usage

```yaml
name: Fetch overleaf resume

on:
  schedule:
    - cron: '0 0 * * *' # Daily at midnight
  workflow_dispatch: # Manual

jobs:
  fetch-pdf:
    runs-on: ubuntu-latest
    steps:
      - name: Fetch pdf from overleaf
        uses: Sbrjt/overleaf-resume-downloader@v1
        with:
          overleaf_url: 'replace-with-your-overleaf-url'
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

## Detailed Steps

- Create a repo for hosting the resume. [Example]()

- Go to your overleaf project and grab the read-only link. (Click on Share, turn on link sharing and copy the view-only link).

- Create a GitHub Actions workflow file with above code (at .github/workflows/update-resume.yml). Replace with your `overleaf_url`.

- Allow Read and Write permissions for GitHub Actions. (Settings > Actions > General > Workflow permissions > Read and write permissions).

- Enable Github pages for hosting. (Settings > Pages > Select branch > main > Save).

- Run the action manually once. (Actions > Fetch overleaf resume > Run workflow)

- Find your hosted resume at `https://<usrname>.github.io/resume/<your-pdf-name>.pdf`. This will sync automatically with your overleaf pdf.

- (Optional) Use [Zapier](https://youtu.be/d5g-pIeoUL4) to sync with google drive. [Eg](https://zapier.com/shared/97c52bfb5e6295840a45c82f90d4e6e7bcd23037).

Note: After the action finishes, the Github Pages deployment will start and this may take a while. Do a hard refresh if the pdf gets cached.

## Todo (Help Me!)

- Currently, the pdf is updated based on a scheduled cron job. Ideally, we'd like to check whether the pdf has been updated on overleaf before committing it to avoid unnecessary pushes. (Unfortunately, I could not find the last updated field on overleaf.)

- I'm using Selenium to fetch the pdf, as using curl didn’t work due to overleaf’s authentication measures on the read-only link. I'm curious if there's a more straightforward solution than this.

- More logging and error handling
