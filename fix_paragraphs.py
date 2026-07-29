import os
import re

def clean_paragraph_tags(filepath):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        original_content = content

        # 1. Remove stacked or duplicate closing paragraph tags (e.g., </p></p> or </p>   </p>)
        content = re.sub(r'(</p>\s*){2,}', '</p>', content, flags=re.IGNORECASE)

        # 2. Remove closing </p> tags that appear immediately after block-level closing tags
        # (Common artifact when parsers dump leftover tags before </div>, </table>, </body>, etc.)
        content = re.sub(r'(</(?:div|table|tr|td|body|html)>\s*)</p>', r'\1', content, flags=re.IGNORECASE)

        # 3. Remove orphaned </p> tags that appear directly before a new opening block tag without an opening <p>
        # e.g., </p> \n <h2>
        content = re.sub(r'</p>\s*(?=<h[1-6]|table|div|ul|ol|hr|blockquote)', '', content, flags=re.IGNORECASE)

        # 4. Convert unclosed <p> tags prior to a block element into cleanly closed paragraphs
        # If a <p> tag is followed by text/inline elements and then hits a block tag or another <p>, close it cleanly
        block_pattern = r'(<p\b[^>]*>[\s\S]*?)(?=\s*<(?:p|h[1-6]|table|div|ul|ol|hr|blockquote|body)\b)'
        
        def close_p(match):
            snippet = match.group(1)
            # If there's no closing </p> in this segment, add one before the next block element
            if '</p>' not in snippet.lower():
                return snippet.strip() + '</p>\n'
            return snippet

        content = re.sub(block_pattern, close_p, content, flags=re.IGNORECASE)

        if content != original_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Cleaned paragraph tags in: {filepath}")

    except Exception as e:
        print(f"Error processing {filepath}: {e}")

def run():
    print("Repairing malformed paragraph tags site-wide...\n")
    for root, _, files in os.walk(os.getcwd()):
        for file in files:
            if file.lower().endswith((".html", ".htm")):
                clean_paragraph_tags(os.path.join(root, file))
    print("\nParagraph repair complete!")

if __name__ == "__main__":
    run()
