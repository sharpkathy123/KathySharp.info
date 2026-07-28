import os
import requests
from bs4 import BeautifulSoup

# Standard User-Agent header
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Cache results so we don't spam the Wayback API for duplicate links
wayback_cache = {}

def get_wayback_archive_url(original_url):
    """Queries the Internet Archive Availability API for the closest saved snapshot."""
    if original_url in wayback_cache:
        return wayback_cache[original_url]

    api_url = f"http://archive.org/wayback/available?url={original_url}"
    try:
        response = requests.get(api_url, headers=HEADERS, timeout=10)
        data = response.json()
        
        # Check if an archived snapshot exists
        archived_snapshots = data.get("archived_snapshots", {})
        closest = archived_snapshots.get("closest", {})
        
        if closest.get("available") and closest.get("url"):
            archive_url = closest["url"]
            # Convert http to https for archive links to prevent mixed-content warnings
            if archive_url.startswith("http://"):
                archive_url = archive_url.replace("http://", "https://", 1)
            wayback_cache[original_url] = archive_url
            return archive_url
    except Exception as e:
        print(f"  ⚠️ Error querying Wayback API for {original_url}: {e}")

    wayback_cache[original_url] = None
    return None

def process_file_with_wayback(filepath):
    """Finds links marked 'link-broken', fetches Wayback Machine equivalents, and updates href."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        modified = False
        # Find all anchor tags that have 'link-broken' class
        broken_links = soup.find_all("a", class_="link-broken")

        for a in broken_links:
            original_url = a.get("href", "").strip()
            
            # Skip if it's already a Wayback Machine link
            if "web.archive.org" in original_url or not original_url.startswith("http"):
                continue

            print(f" Searching Wayback Machine for: {original_url}")
            archive_url = get_wayback_archive_url(original_url)

            if archive_url:
                a["href"] = archive_url
                # Remove 'link-broken' class so CSS no longer strikes it out
                classes = a.get("class", [])
                classes.remove("link-broken")
                if classes:
                    a["class"] = classes
                else:
                    del a["class"]
                
                modified = True
                print(f"  ✅ REPLACED WITH ARCHIVE: {archive_url}")
            else:
                print(f"  ❌ No Wayback Machine capture found for: {original_url}")

        if modified:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(str(soup.prettify()))
            print(f" Saved archived links to: {filepath}")

    except Exception as e:
        print(f" Error processing {filepath}: {e}")

def run_wayback_fixer():
    print("Starting Internet Archive lookup for marked broken links...\n")
    for root, _, files in os.walk(os.getcwd()):
        for file in files:
            if file.lower().endswith((".html", ".htm")):
                full_path = os.path.join(root, file)
                process_file_with_wayback(full_path)
    print("\n Wayback Machine restoration complete!")

if __name__ == "__main__":
    run_wayback_fixer()
