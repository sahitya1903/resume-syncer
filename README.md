Overleaf is a popular LaTeX editor used for writing resumes. But the free-tier plan lacks Git and cloud drive integration. So every time you update your resume, you have to manually download the latest pdf for sharing - which quickly becomes tedious.

This GitHub action solves this by automatically fetching the latest pdf from overleaf and commits it to your GitHub repo, from where it can be easily hosted and shared.

## Example Usage

```yaml
name: Sync Overleaf PDF

permissions:
  contents: write

on:
  schedule:
    - cron: '0 0 * * *' # Daily at midnight
  workflow_dispatch:    # For manual trigger

jobs:
  get-pdf:
    runs-on: ubuntu-latest
    steps:
      - uses: Sbrjt/overleaf-resume-syncer@main
        with:
          overleaf_url: 'https://www.overleaf.com/read/your-project-id' 
          # Replace with your overleaf sharing link (not your project url!)
          # Share > link sharing > view-only link

          gdrive_link: 'your-gdrive-link'
          # Make sure you give edit permission to my service account: 
          # overleaf-resume-syncer@overleaf-resume-syncer-462412.iam.gserviceaccount.com

          github_token: ${{ secrets.GITHUB_TOKEN }}
```

<details>
<summary>
Detailed Steps
</summary>

1. Create a repo for hosting the resume. (Alternately, you can fork [this](https://github.com/Sbrjt/resume) template.)

1. Go to your overleaf project and grab the read-only link. (Click on Share, turn on link sharing and copy the view-only link).

1. Create a GitHub Actions workflow file with above code block (at .github/workflows/update-resume.yml).

1. (Optional) Create a file named `resume.pdf` in your Google Drive and share its edit access to `overleaf-resume-syncer@overleaf-resume-syncer-462412.iam.gserviceaccount.com`.

1. Run the action manually once. (Actions > Fetch overleaf resume > Run workflow)

1. Enable Github pages for hosting. 

</details>

<details>
<summary>
How it works
</summary>

<br>

This is a GitHub composite action, which can be imported as `Sbrjt/overleaf-resume-syncer@v1` in any other GitHub Action. (See `action.yml` file.) The action takes in 2 inputs: your overleaf url and a github token.

First, it checks out the repo, installs python and selenium, and runs a python script to fetch the pdf.

`selenium_script.py` get the latex code from overleaf by inspecting websockets frames and compares it with the existing `resume.tex`. If there are changes, it finds the download button and clicks it to get the new pdf. Otherwise, the action skips the next step.

Then it uses the GitHub token provided in the inputs to push the updated code on your behalf (as GitHub Actions bot).

The action is intended to run on a scheduled cron job (eg, daily or weekly).


</details>

#

The most trivial solution might seem like having some latex previewer/builder and editing the `.tex` file locally. But TeX distributions like TeX-live are huge and can be a hassle to set up. More info [here](https://mark-wang.com/blog/2022/latex/).

Using Selenium sidesteps Overleaf's protections (which block curl and unauthenticated scrapers) by simulating an actual user session.