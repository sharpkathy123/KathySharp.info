from email.utils import parsedate_to_datetime
from pathlib import Path
import re
import requests
import zoneinfo

BASE_URL = "https://kathysharp.info/"
AZ_TZ = zoneinfo.ZoneInfo("America/Phoenix")

# Matches the script tag containing 'dateStr'
SCRIPT_REGEX = re.compile(
    r'<script\b[^>]*>[\s\S]*?dateStr[\s\S]*?</script>',
    re.IGNORECASE
)

# Broad pattern to detect the start of a bottom navigation bar or footer area
NAV_BOTTOM_REGEX = re.compile(
    r'(</nav>|<footer\b|<div[^>]*class="[^"]*nav[^"]*"[^>]*>)', 
    re.IGNORECASE
)

html_files = list(Path(".").rglob("*.html"))
updated_count = 0

for file_path in html_files:
    # 1. Skip ONLY the root index.html home page
    if file_path.resolve() == Path("index.html").resolve():
        print(f"Skipping root home page: {file_path}")
        continue

    content = file_path.read_text(encoding="utf-8")

    # 2. Ensure the script tag containing dateStr exists
    if not SCRIPT_REGEX.search(content):
        continue

    # 3. Locate the bottom navigation boundary
    # If a nav bar or footer element is found, search for dateStr ONLY after it
    nav_matches = list(NAV_BOTTOM_REGEX.finditer(content))
    if nav_matches:
        # Split search at the last occurrence of bottom nav/footer element
        split_pos = nav_matches[-1].start()
        header_content = content[:split_pos]
        footer_content = content[split_pos:]

        # Verify dateStr is actually in the bottom section
        if not SCRIPT_REGEX.search(footer_content):
            print(f"Skipped {file_path}: dateStr found, but NOT below the bottom nav.")
            continue
        
        # Replace script tag inside the bottom section only
        new_footer_content = SCRIPT_REGEX.sub(
            lambda m: f'<span class="last-modified">Last updated: __DATE_PLACEHOLDER__</span>',
            footer_content,
            count=1
        )
        has_bottom_match = True
    else:
        # Fallback if no explicit nav tag exists: check full content
        has_bottom_match = True
        header_content = ""
        new_footer_content = content

    # 4. Fetch live server header and perform replacement
    rel_path = file_path.as_posix()
    live_url = f"{BASE_URL.rstrip('/')}/{rel_path.lstrip('/')}"

    try:
        response = requests.head(live_url, allow_redirects=True)

        if response.status_code == 200 and "Last-Modified" in response.headers:
            raw_date = response.headers["Last-Modified"]

            # Convert GMT to Arizona MST
            utc_dt = parsedate_to_datetime(raw_date)
            az_dt = utc_dt.astimezone(AZ_TZ)
            formatted_date = az_dt.strftime("%B %d, %Y").replace(" 0", " ")

            span_replacement = f'<span class="last-modified">Last updated: {formatted_date}</span>'

            if nav_matches:
                final_footer = new_footer_content.replace("__DATE_PLACEHOLDER__", formatted_date)
                final_content = header_content + final_footer
            else:
                final_content = SCRIPT_REGEX.sub(span_replacement, content, count=1)

            file_path.write_text(final_content, encoding="utf-8")
            updated_count += 1
            print(f"Updated: {file_path} -> {formatted_date} (MST)")
        else:
            print(f"Server returned {response.status_code} for {live_url}")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

print(f"\nDone! Updated {updated_count} file(s).")
