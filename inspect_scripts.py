import os
from bs4 import BeautifulSoup

root_dir = os.getcwd()
found = 0

print("Scanning local HTML files for script tags...\n")

for dirpath, _, filenames in os.walk(root_dir):
    for filename in filenames:
        if filename.lower().endswith(('.html', '.htm')):
            rel_path = os.path.relpath(os.path.join(dirpath, filename), root_dir)
            if rel_path.lower() in ('index.html', 'index.htm'):
                continue
                
            with open(os.path.join(dirpath, filename), 'r', encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                scripts = soup.find_all('script')
                for s in scripts:
                    text = s.string or s.text or ""
                    # Check for key keywords regardless of exact case/formatting
                    if "lastmodified" in text.lower() or "datestr" in text.lower() or "modified" in text.lower():
                        found += 1
                        print(f"=== File: {rel_path} ===")
                        print(s.prettify())
                        print("-" * 50)

print(f"\nTotal matching scripts found: {found}")
