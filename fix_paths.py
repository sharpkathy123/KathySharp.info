import os
from bs4 import BeautifulSoup

def fix_css_paths_in_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        modified = False

        # Calculate exact relative path based on directory depth
        # Root level = "css/modern-base.css"
        # Subfolder level = "../css/modern-base.css"
        rel_dir = os.path.relpath(os.path.dirname(filepath), os.getcwd())
        depth = 0 if rel_dir == "." else len(rel_dir.split(os.sep))
        prefix = "../" * depth
        correct_relative_path = f"{prefix}css/modern-base.css"

        # Find all link tags pointing to modern-base.css (including /css/...)
        link_tags = soup.find_all("link", rel=lambda r: r and "stylesheet" in r.lower())
        
        for link in link_tags:
            href = link.get("href", "")
            if "modern-base.css" in href:
                if href != correct_relative_path:
                    link["href"] = correct_relative_path
                    modified = True

        if modified:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(str(soup.prettify()))
            print(f"Fixed CSS path in: {filepath} -> {correct_relative_path}")

    except Exception as e:
        print(f"Error processing {filepath}: {e}")

def run():
    print("Updating /css/ absolute paths to relative paths...\n")
    for root, _, files in os.walk(os.getcwd()):
        for file in files:
            if file.lower().endswith((".html", ".htm")):
                fix_css_paths_in_file(os.path.join(root, file))
    print("\nPath conversion complete!")

if __name__ == "__main__":
    run()
