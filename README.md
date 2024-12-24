# Fetch Overleaf PDF Action

This GitHub Action downloads a PDF file from an Overleaf document and commits it to the repository.

## Example Usage

```yaml
name: Fetch Overleaf PDF

on:
  workflow_dispatch:
	schedule:
		- cron: '0 0 * * 0' # This will run every Sunday (at 00:00 UTC)

jobs:
  fetch-pdf:
    runs-on: ubuntu-latest
    steps:
      - name: Fetch PDF from Overleaf
        uses: sbrjt/overleaf-resume@v1.0.0
        with:
          overleaf_url: 'your-overleaf-read-only-url'
```
