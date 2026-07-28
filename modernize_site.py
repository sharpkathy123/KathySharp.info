import os
from bs4 import BeautifulSoup

# 1. Define modern-base.css content
MODERN_CSS_CONTENT = """/* =========================================================
   Global Layout & Mobile Modernization
   ========================================================= */

*, *::before, *::after {
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  line-height: 1.6;
  color: #222222;
  background-color: #fcfcfc;
  margin: 0;
  padding: 1rem;
}

/* Force vintage fixed tables into responsive containers */
table {
  max-width: 100% !important;
  width: 100% !important;
  height: auto !important;
  border-collapse: collapse;
}

/* Scale photos/embeds to fit mobile screens */
img, iframe, embed, object {
  max-width: 100% !important;
  height: auto !important;
}

a {
  color: #0056b3;
  text-decoration: underline;
}

a:hover {
  color: #003366;
}

/* Styling for broken/archived links */
a.link-broken {
  color: #777777 !important;
  text-decoration: line-through !important;
  opacity: 0.8;
}

a.link-broken::after {
  content: " [offline]";
  font-size: 0.75em;
  color: #b00000;
  text-decoration: none;
  font-style: italic;
}
"""

def setup_css_folder():
    """Ensure css directory exists and write modern-base.css"""
    css_dir = os.path.join(os.getcwd(), "css")
    os.makedirs(css_dir, exist_ok=True)
    
    css_path = os.path.join(css_dir, "modern-base.css")
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(MODERN_CSS_CONTENT)
    print(" Created/Updated: css/modern-base.css")

def cleanup_and_modernize_html(soup):
    """Clean legacy HTML clutter and inject modern head tags."""
    # Ensure <head> exists
    if not soup.head:
        head_tag = soup.new_tag("head")
        if soup.html:
            soup.html.insert(0, head_tag)
        else:
            soup.insert(0, head_tag)

    # Remove deprecated layout/presentational attributes from body/tables
    for tag in soup.find_all(True):
        # Remove legacy inline styling attributes that break CSS overrides
        for attr in ["bgcolor", "text", "link", "vlink", "alink", "width", "height", "border"]:
            if attr in tag.attrs and tag.name in ["body", "table", "td", "tr", "th"]:
                del tag.attrs[attr]

    # Check if modern-base.css is already linked
    has_modern_css = any(
        link.get("href") == "/css/modern-base.css" for link in soup.find_all("link")
    )

    if not has_modern_css:
        # Create <meta name="viewport">
        viewport = soup.new_tag("meta")
        viewport.attrs["name"] = "viewport"
        viewport.attrs["content"] = "width=device-width, initial-scale=1.0"
        soup.head.append(viewport)

        # Create <meta http-equiv="Content-Security-Policy">
        csp = soup.new_tag("meta")
        csp.attrs["http-equiv"] = "Content-Security-Policy"
        csp.attrs["content"] = "upgrade-insecure-requests"
        soup.head.append(csp)

        # Link modern-base.css
        css_link = soup.new_tag("link")
        css_link.attrs["rel"] = "stylesheet"
        css_link.attrs["href"] = "/css/modern-base.css"
        soup.head.append(css_link)

    return soup

def process_html_file(filepath):
    """Reads, parses, cleans up, and overwrites an HTML file."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Parse with BeautifulSoup (automatically fixes unclosed/malformed tags)
        soup = BeautifulSoup(content, "html.parser")
        
        # Clean messy markup & inject metadata
        cleaned_soup = cleanup_and_modernize_html(soup)

        # Save the formatted output back to the file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(str(cleaned_soup.prettify()))
        
        print(f" Cleaned & Modernized: {filepath}")

    except Exception as e:
        print(f" Error processing {filepath}: {e}")

def run_modernization():
    """Traverse all files in the repository"""
    setup_css_folder()
    
    print("\nScanning repository for HTML files...")
    for root, _, files in os.walk(os.getcwd()):
        for file in files:
            if file.lower().endswith((".html", ".htm")):
                full_path = os.path.join(root, file)
                process_html_file(full_path)

if __name__ == "__main__":
    run_modernization()
