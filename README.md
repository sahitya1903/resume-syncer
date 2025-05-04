Overleaf doesn’t provide a direct, hosted link to PDFs within its projects. Every time you make changes to your resume, you need to manually download the updated pdf for sharing.

This GitHub action automates fetching the latest pdf from overleaf and commits it to your GitHub repo, from where it can be easily hosted and shared.

## Example Usage

```yaml
name: Fetch Overleaf PDF

permissions:
  contents: write

on:
  schedule:
    - cron: '0 0 * * *' # Daily at midnight
  workflow_dispatch: # For manual trigger

jobs:
  fetch-pdf:
    runs-on: ubuntu-latest
    steps:
      - uses: Sbrjt/overleaf-resume-downloader@main
        with:
          overleaf_url: 'https://www.overleaf.com/read/your-project-id # Replace with your overleaf-url
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

<details>
<summary>
Detailed Steps
</summary>

1. Create a repo for hosting the resume. (Alternately, you can fork [this](https://github.com/Sbrjt/resume) template.)

1. Go to your overleaf project and grab the read-only link. (Click on Share, turn on link sharing and copy the view-only link).

1. Create a GitHub Actions workflow file with above code block (at .github/workflows/update-resume.yml). Replace with your `overleaf_url`.

1. Run the action manually once. (Actions > Fetch overleaf resume > Run workflow)

1. Enable Github pages for hosting. 

1. (Optional) Use [Zapier](https://youtu.be/d5g-pIeoUL4) to sync with google drive. [Eg](https://zapier.com/shared/97c52bfb5e6295840a45c82f90d4e6e7bcd23037).

</details>

## How it works

This is a GitHub composite action, which can be imported as `Sbrjt/overleaf-resume-downloader@v1` in any other GitHub Action. (See `action.yml` file.) The action takes in 2 inputs: the overleaf url and a github token.

First, it checks out the repo, installs python and selenium, and runs a python script to fetch the pdf.

`selenium_script.py` copies the latex code from overleaf and compares it with `resume.tex`. If there are changes, it finds the download button and clicks it to get the pdf. Otherwise, the action skips the next step.

The next step uses the GitHub token provided in the inputs to push the updated code on your behalf (using the GitHub Actions bot).

The action is intended to run on a scheduled cron job (eg, daily or weekly).

The most trivial solution seems like editing the `.tex` file locally in vscode with some latex previewer/builder but TeX-live is huge and too much of a hassle to set up. More info [here](https://mark-wang.com/blog/2022/latex/).

## Todo (Help Me!)

- Lazy loading is sometimes interfering with the copying of latex code.

- I'm using Selenium to fetch the pdf, as using `curl` didn’t work due to overleaf’s authentication measures on the read-only link. I'm curious if there's a more straightforward solution than this. (like directly intercepting from the payload)

- Tokens from the OAuth Playground expire in 1 day, so I couldn't automate the gdrive part.

- Using cache for python and requirements
