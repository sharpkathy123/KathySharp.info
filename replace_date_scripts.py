import os
import re
import requests
from bs4 import BeautifulSoup

DOMAIN = "https://kathysharp.info"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Date regex
DATE_PATTERN = re.compile(
    r'(\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b)',
    re.IGNORECASE
)

KEYWORDS = ["lastmodified", "datestr", "display last modified date"]

def get_footer_date_text(rel_path):
    """Fetches live page and isolates text appearing after the bottom navigation/footer elements."""
    url_path = rel_path.replace(os.sep, '/')
    url = f"{DOMAIN}/{url_path}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"  [HTTP {response.status_code}] Could not fetch {url}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        
        # 1. Look for bottom navigation anchors or horizontal rules near footer
        nav_element = (
            soup.find("nav") or 
            soup.find(id=re.compile(r'nav|footer', re.I)) or 
            soup.find(class_=re.compile(r'nav|footer', re.I))
        )
        
        # Fall back to searching after the final <hr> if present
        if not nav_element:
            hr_tags = soup.find_all("hr")
            if hr_tags:
                nav_element = hr_tags[-1]

        # Extract text elements strictly after the nav/footer marker
        if nav_element:
            footer_nodes = nav_element.find_all_next(text=True)
            footer_text = [node.strip() for node in footer_nodes if node.strip()]
        else:
            # Fallback: inspect only the last 3 visible lines on the page
            body = soup.find("body") or soup
            all_lines = [line.strip() for line in body.get_text(separator="\n").splitlines() if line.strip()]
            footer_text = all_lines[-3:] if len(all_lines) >= 3 else all_lines

        # Search extracted footer lines for a date string
        for line in footer_text:
            if DATE_PATTERN.search(line):
                return line

        print(f"  [No footer date found] {url}")
        return None

    except Exception as e:
        print(f"  [Error fetching {url}]: {e}")
        return None

def update_file(full_path, rel_path):
    date_text = get_footer_date_text(rel_path)
    if not date_text:
        return

    try:
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        content_lower = content.lower()
        search_pos = 0
        replaced = False

        # Locate and replace script blocks containing keywords
        while True:
            script_start = content_lower.find("<script", search_pos)
            if script_start == -1:
                break
            
            script_end = content_lower.find("</script>", script_start)
            if script_end == -1:
                break
            
            script_end += len("</script>")
            script_block_lower = content_lower[script_start:script_end]

            if any(kw in script_block_lower for kw in KEYWORDS):
                replacement_html = f"<p>{date_text}</p>"
                content = content[:script_start] + replacement_html + content[script_end:]
                content_lower = content.lower()
                search_pos = script_start + len(replacement_html)
                replaced = True
            else:
                search_pos = script_end

        if replaced:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated {rel_path} -> '{date_text}'")

    except Exception as e:
        print(f"❌ Error reading/writing {rel_path}: {e}")

def run():
    root_dir = os.getcwd()
    print("Replacing date scripts with text strictly below bottom nav...\n" + "="*60)

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith(('.html', '.htm')):
                full_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(full_path, root_dir)

                # Skip top-level root index files
                if rel_path.lower() in ('index.html', 'index.htm'):
                    continue

                update_file(full_path, rel_path)

    print("="*60 + "\nProcessing complete!")

if __name__ == "__main__":
    run()
