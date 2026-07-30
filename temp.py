from email.utils import parsedate_to_datetime
from pathlib import Path
import re
import requests
import zoneinfo

BASE_URL = "https://kathysharp.info/"
AZ_TZ = zoneinfo.ZoneInfo("America/Phoenix")

# Matches the script tag containing 'dateStr' (and optional surrounding whitespaces)
SCRIPT_REGEX = re.compile(
    r'<script\b[^>]*>[\s\S]*?dateStr[\s\S]*?</script>',
    re.IGNORECASE
)

html_files = list(Path(".").rglob("*.html"))

updated_count = 0

for file_path in html_files:
    # 1. Skip index.html files
    if file_path.name.lower() == "index.html":
        continue

    # Read content first to check if dateStr exists in this file
    content = file_path.read_text(encoding="utf-8")
    if not SCRIPT_REGEX.search(content):
        continue

    # 2. Build live URL path
    rel_path = file_path.as_posix()
    live_url = f"{BASE_URL.rstrip('/')}/{rel_path.lstrip('/')}"

    try:
        response = requests.head(live_url, allow_redirects=True)

        if response.status_code == 200 and "Last-Modified" in response.headers:
            raw_date = response.headers["Last-Modified"]

            # Parse GMT header and convert to America/Phoenix (MST)
            utc_dt = parsedate_to_datetime(raw_date)
            az_dt = utc_dt.astimezone(AZ_TZ)

            # Format date (e.g., "February 2, 2014")
            formatted_date = az_dt.strftime("%B %d, %Y").replace(" 0", " ")

            new_footer_html = (
                f'<span class="last-modified">Last updated: {formatted_date}</span>'
            )

            # Replace the script block containing 'dateStr'
            new_content = SCRIPT_REGEX.sub(new_footer_html, content)
            file_path.write_text(new_content, encoding="utf-8")

            updated_count += 1
            print(f"Updated: {file_path} -> {formatted_date} (MST)")
        else:
            print(f"Server returned {response.status_code} for {live_url}")

    except Exception as e:
        print(f"Error on {file_path}: {e}")

print(f"\nDone! Updated {updated_count} file(s).")
