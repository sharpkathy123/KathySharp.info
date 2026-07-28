import os
import requests
from bs4 import BeautifulSoup

# Standard browser user-agent to prevent websites from blocking the checker
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Simple cache so we don't ping the exact same URL multiple times across different pages
url_status_cache = {}

def check_url(url):
    """Checks if an external URL is reachable (returns True if alive, False if broken)."""
    if url in url_status_cache:
        return url_status_cache[url]

    try:
        # Send a HEAD request first (faster); fall back to GET if HEAD fails
        response = requests.head(url, headers=HEADERS, allow_redirects=True, timeout=5)
        if response.status_code >= 400:
            response = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=5)
        
        is_ok = response.status_code < 400
    except requests.RequestException:
        is_ok = False

    url_status_cache[url] = is_ok
    return is_ok

def process_links_in_file(filepath):
    """Scans an HTML file for external links, tests them, and adds class='link-broken' if offline."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        modified = False
        links = soup.find_all("a", href=True)

        for a in links:
            href = a['href'].strip()

            # Only check external web links
            if href.startswith("http://") or href.startswith("https://"):
                print(f" Checking link in {os.path.basename(filepath)}: {href}")
                is_alive = check_url(href)

                if not is_alive:
                    # Append 'link-broken' class without overwriting existing classes
                    existing_classes = a.get("class", [])
                    if "link-broken" not in existing_classes:
                        existing_classes.append("link-broken")
                        a["class"] = existing_classes
                        modified = True
                        print(f" ❌ MARKED BROKEN: {href}")
                else:
                    print(f"  OK: {href}")

        if modified:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(str(soup.prettify()))
            print(f" Saved updates to: {filepath}")

    except Exception as e:
        print(f" Error processing {filepath}: {e}")

def run_link_checker():
    print("Starting broken link scan across all HTML files...\n")
    for root, _, files in os.walk(os.getcwd()):
        for file in files:
            if file.lower().endswith((".html", ".htm")):
                full_path = os.path.join(root, file)
                process_links_in_file(full_path)
    print("\n Link scan and marking complete!")

if __name__ == "__main__":
    run_link_checker()
