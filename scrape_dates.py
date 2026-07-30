import os
import re
import requests
from bs4 import BeautifulSoup

DOMAIN = "https://kathysharp.info"

# Common regex patterns for dates on the last line (e.g., 07/29/2026, July 29, 2026, 2026-07-29)
DATE_PATTERN = re.compile(
    r'(\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b)',
    re.IGNORECASE
)

def get_last_line_info(rel_path):
    url_path = rel_path.replace(os.sep, '/')
    url = f"{DOMAIN}/{url_path}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None, f"HTTP {response.status_code}"

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract visible text lines from body
        body = soup.find("body")
        if not body:
            return None, "No body element"

        # Strip whitespace and break into non-empty lines
        text_lines = [line.strip() for line in body.get_text(separator="\n").splitlines() if line.strip()]
        
        if not text_lines:
            return None, "Empty page text"

        last_line = text_lines[-1]
        
        # Check if the last line contains a date
        date_match = DATE_PATTERN.search(last_line)
        if date_match:
            return last_line, None
        else:
            return None, f"No date found on last line: '{last_line}'"

    except Exception as e:
        return None, str(e)

def run():
    root_dir = os.getcwd()
    print(f"Scanning subpages on {DOMAIN} for dates on the last displayed line...\n")
    print(f"{'FILE NAME':<35} | {'LAST DISPLAYED LINE'}")
    print("-" * 80)

    found_count = 0

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith(('.html', '.htm')):
                full_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(full_path, root_dir)

                # Skip top-level index.html / index.htm
                if rel_path.lower() in ('index.html', 'index.htm'):
                    continue

                last_line_text, error = get_last_line_info(rel_path)
                
                if last_line_text:
                    found_count += 1
                    print(f"{rel_path:<35} | {last_line_text}")

    print("-" * 80)
    print(f"\nScan complete. Found dates on {found_count} pages.")

if __name__ == "__main__":
    run()
