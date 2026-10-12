import os
import subprocess
import sys
import tempfile


def parse_secrets(content):
    """Parse KEY=VALUE lines; quoted values may span multiple lines (e.g. a JSON key)."""
    secrets = {}
    lines = iter(content.splitlines())
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue

        key, val = (part.strip() for part in line.split('=', 1))
        quote = val[:1]
        if quote in ('"', "'"):
            parts = [val[1:]]
            while not parts[-1].rstrip().endswith(quote):
                parts.append(next(lines, quote))
            val = '\n'.join(parts).rstrip()[:-1]
        secrets[key] = val
    return secrets


def run(script, *args, env=None):
    result = subprocess.run([sys.executable, script, *args], env=env)
    if result.returncode:
        sys.exit(result.returncode)


def main():
    try:
        with open('.secrets', encoding='utf-8') as f:
            secrets = parse_secrets(f.read())
    except FileNotFoundError:
        sys.exit('Error: .secrets file not found.')

    overleaf_url = secrets.get('OVERLEAF_URL')
    if not overleaf_url:
        sys.exit('Error: OVERLEAF_URL not found in .secrets')

    # Capture the selenium script's skip output the same way GitHub Actions does
    fd, output_path = tempfile.mkstemp()
    os.close(fd)
    try:
        print('\n--- Running Selenium script ---')
        run('selenium_script.py', overleaf_url, env={**os.environ, 'GITHUB_OUTPUT': output_path})
        with open(output_path, encoding='utf-8') as f:
            unchanged = 'skip=True' in f.read()
    finally:
        os.remove(output_path)

    gdrive_link = secrets.get('GDRIVE_LINK')
    gdrive_key = secrets.get('GDRIVE_SERVICE_ACCOUNT')
    if unchanged:
        print('\nResume unchanged. Skipping Google Drive upload.')
    elif not (gdrive_link and gdrive_key):
        print('\nGoogle Drive configuration not found. Skipping Google Drive upload.')
    else:
        print('\n--- Running Google Drive upload script ---')
        run('upload_to_gdrive.py', env={
            **os.environ,
            'GDRIVE_LINK': gdrive_link,
            'GDRIVE_SERVICE_ACCOUNT_KEY': gdrive_key,
        })


if __name__ == '__main__':
    main()
