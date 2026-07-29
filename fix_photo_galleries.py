import os
from bs4 import BeautifulSoup

def process_photo_index(filepath):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        modified = False

        # Find all <img> tags or <a> tags containing <img> tags
        imgs = soup.find_all("img")
        if not imgs:
            return

        # Find groups of images or linked images that share a parent
        for img in imgs:
            parent = img.parent
            # Check if image is wrapped in a link <a>
            target_node = parent if parent.name == "a" else img
            container = target_node.parent

            # Skip if already inside a gallery container
            if container.get("class") and "photo-gallery" in container.get("class"):
                continue

            # Check if this container holds multiple image elements
            child_imgs = container.find_all("img")
            if len(child_imgs) > 1:
                # Wrap the child image elements into a photo-gallery div
                gallery_div = soup.new_tag("div", attrs={"class": "photo-gallery"})
                
                # Gather targets to move (either the <a> wrappers or standalone <img> tags)
                nodes_to_move = []
                for child in list(container.children):
                    if child.name == "img":
                        nodes_to_move.append(child)
                    elif child.name == "a" and child.find("img"):
                        nodes_to_move.append(child)

                if nodes_to_move:
                    # Insert gallery before the first image element
                    nodes_to_move[0].insert_before(gallery_div)
                    for node in nodes_to_move:
                        gallery_div.append(node.extract())
                    modified = True

        if modified:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(str(soup.prettify()))
            print(f" Grouped thumbnails into gallery: {filepath}")

    except Exception as e:
        print(f" Error processing {filepath}: {e}")

def run():
    photos_dir = os.path.join(os.getcwd(), "photos")
    if not os.path.exists(photos_dir):
        print(" 'photos' directory not found in the current root.")
        return

    print("Formatting thumbnail grids across photos directory...\n")
    for root, _, files in os.walk(photos_dir):
        for file in files:
            if file.lower() in ("index.html", "index.htm"):
                process_photo_index(os.path.join(root, file))
    print("\n Gallery formatting complete!")

if __name__ == "__main__":
    run()
