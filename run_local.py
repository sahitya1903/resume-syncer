import os
import subprocess
import sys
    
def parse_secrets(content):
    secrets = {}
    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith('#'):
            i += 1
            continue
        if '=' in line:
            key, val = line.split('=', 1)
            key = key.strip()
            val = val.strip()
            
            # Check for quoted values (might be multi-line)
            if val.startswith("'") or val.startswith('"'):
                quote_char = val[0]
                if len(val) > 1 and val.endswith(quote_char) and not val.endswith('\\' + quote_char):
                    secrets[key] = val[1:-1]
                else:
                    accumulated = [val[1:]]
                    i += 1
                    while i < len(lines):
                        next_line = lines[i]
                        if next_line.rstrip().endswith(quote_char):
                            accumulated.append(next_line.rstrip()[:-1])
                            break
                        else:
                            accumulated.append(next_line)
                        i += 1
                    secrets[key] = '\n'.join(accumulated)
            else:
                secrets[key] = val
        i += 1
    return secrets

def main():
    secrets_path = '.secrets'
    if not os.path.exists(secrets_path):
        print(f"Error: {secrets_path} file not found.")
        sys.exit(1)
        
    print(f"Reading secrets from {secrets_path}...")
    with open(secrets_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    secrets = parse_secrets(content)

    # Ensure required secrets exist
    overleaf_url = secrets.get('OVERLEAF_URL')
    if not overleaf_url:
        print("Error: OVERLEAF_URL not found in .secrets")
        sys.exit(1)

    # 2. Run the Selenium script to download the resume
    print("\n--- Running Selenium script ---")
    try:
        subprocess.run([sys.executable, 'selenium_script.py', overleaf_url], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Selenium script failed with exit code {e.returncode}")
        sys.exit(e.returncode)

    # 3. Run GDrive Sync Script if credentials exist
    gdrive_link = secrets.get('GDRIVE_LINK')
    gdrive_sa = secrets.get('GDRIVE_SERVICE_ACCOUNT')
    
    if gdrive_link and gdrive_sa:
        print("\n--- Running Google Drive upload script ---")
        # Set environment variables for the subprocess
        env = os.environ.copy()
        env['GDRIVE_LINK'] = gdrive_link
        env['GDRIVE_SERVICE_ACCOUNT_KEY'] = gdrive_sa
        
        try:
            subprocess.run([sys.executable, 'upload_to_gdrive.py'], env=env, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Google Drive upload script failed with exit code {e.returncode}")
            sys.exit(e.returncode)
    else:
        print("\nGoogle Drive configuration not found. Skipping Google Drive upload.")

if __name__ == '__main__':
    main()
