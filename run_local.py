import os
import re
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


def sync(name, overleaf_url, gdrive_link, gdrive_key):
    # Capture the selenium script's skip output the same way GitHub Actions does
    fd, output_path = tempfile.mkstemp()
    os.close(fd)
    try:
        print(f'\n--- Running Selenium script for {name} ---')
        run('selenium_script.py', overleaf_url, name, env={**os.environ, 'GITHUB_OUTPUT': output_path})
        with open(output_path, encoding='utf-8') as f:
            unchanged = 'skip=True' in f.read()
    finally:
        os.remove(output_path)

    if unchanged:
        print(f'\n{name} unchanged. Skipping Google Drive upload.')
    elif not (gdrive_link and gdrive_key):
        print(f'\nGoogle Drive configuration not found for {name}. Skipping Google Drive upload.')
    else:
        print(f'\n--- Running Google Drive upload script for {name} ---')
        run('upload_to_gdrive.py', name, env={
            **os.environ,
            'GDRIVE_LINK': gdrive_link,
            'GDRIVE_SERVICE_ACCOUNT_KEY': gdrive_key,
        })


def main():
    try:
        with open('.secrets', encoding='utf-8') as f:
            secrets = parse_secrets(f.read())
    except FileNotFoundError:
        sys.exit('Error: .secrets file not found.')

    # OVERLEAF_URL syncs resume.*, and OVERLEAF_URL_<NAME> syncs <name>.* with GDRIVE_LINK_<NAME>
    resumes = [m for key in secrets if (m := re.fullmatch(r'OVERLEAF_URL(_\w+)?', key)) and secrets[key]]
    if not resumes:
        sys.exit('Error: no OVERLEAF_URL or OVERLEAF_URL_<NAME> found in .secrets')

    for m in resumes:
        suffix = m.group(1) or ''
        name = suffix[1:].lower() or 'resume'
        sync(name, secrets[m.group(0)], secrets.get(f'GDRIVE_LINK{suffix}'), secrets.get('GDRIVE_SERVICE_ACCOUNT'))


if __name__ == '__main__':
    main()
