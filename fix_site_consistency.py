#!/usr/bin/env python3
"""Fix common legacy site consistency issues while skipping the misc folder.

This script intentionally targets the patterns seen in this repo:
- malformed HTML tags and attributes in legacy pages
- duplicate CSS rules in the shared site styles
- common spacing/normalization issues in navigation and page body markup
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

DEFAULT_EXCLUDES = {"misc", ".git", ".github", "node_modules", "__pycache__"}


def normalize_meta_tag(text: str) -> str:
    """Fix malformed meta tags like <metacontent="..."http-equiv="...">."""
    text = re.sub(
        r'<metacontent="([^"]+)"http-equiv="([^"]+)"\s*/?>',
        r'<meta content="\1" http-equiv="\2" />',
        text,
    )
    text = re.sub(
        r'<meta\s+content="([^"]+)"\s*http-equiv="([^"]+)"\s*/?>',
        r'<meta content="\1" http-equiv="\2" />',
        text,
    )
    return text


def normalize_tag_spacing(text: str) -> str:
    """Fix common no-space attribute issues such as <divclass=...> and <ahref=...>."""
    patterns = [
        (r'<divclass=', '<div class='),
        (r'<ahref=', '<a href='),
        (r'<nav><small>', '<nav><small>'),
        (r'\s+class="([^"]+)"data-topic=', ' class="\\1" data-topic='),
        (r'data-topic="([^"]+)"data-photo=', ' data-topic="\\1" data-photo='),
        (r'data-photo="([^"]+)"data-page=', ' data-photo="\\1" data-page='),
        (r'data-page="([^"]+)"\s*data-alt=', ' data-page="\\1" data-alt='),
        (r'\s+data-alt="([^"]+)"\s*>', ' data-alt="\\1" >'),
        (
            r'https:\s*\/\s*\/web\.archive\.org\/web\/20150820102235\/https:\s*\/\s*kathysharp\.shutterfly\.com\/',
            'https://web.archive.org/web/20150820102235/https://kathysharp.shutterfly.com/',
        ),
    ]
    for old, new in patterns:
        text = text.replace(old, new)
    return text


def normalize_html_text(text: str) -> str:
    text = normalize_meta_tag(text)
    text = normalize_tag_spacing(text)
    text = re.sub(r'\s+<', ' <', text)
    text = re.sub(r'>\s+', '> ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip() + '\n'


def dedupe_css_rules(css_text: str) -> str:
    """Remove duplicate CSS rule blocks while preserving ordering."""
    chunks = re.findall(r'(?s)([^{}]+\{[^{}]*\})', css_text)
    seen = set()
    ordered = []
    for chunk in chunks:
        norm = re.sub(r'\s+', ' ', chunk).strip()
        if norm in seen:
            continue
        seen.add(norm)
        ordered.append(chunk)
    return '\n\n'.join(ordered).strip() + ('\n' if ordered else '')


def clean_html_file(path: Path, dry_run: bool = False) -> bool:
    original = path.read_text(encoding='utf-8', errors='replace')
    cleaned = normalize_html_text(original)
    if cleaned != original:
        if not dry_run:
            path.write_text(cleaned, encoding='utf-8')
        return True
    return False


def clean_css_file(path: Path, dry_run: bool = False) -> bool:
    original = path.read_text(encoding='utf-8', errors='replace')
    cleaned = dedupe_css_rules(original)
    if cleaned != original:
        if not dry_run:
            path.write_text(cleaned, encoding='utf-8')
        return True
    return False


def iter_project_files(root: Path):
    for path in root.rglob('*'):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in DEFAULT_EXCLUDES for part in rel.parts[:2]):
            continue
        if rel.parts and rel.parts[0] in DEFAULT_EXCLUDES:
            continue
        if path.suffix.lower() in {'.html', '.css'}:
            yield path


def main() -> int:
    parser = argparse.ArgumentParser(description='Normalize legacy HTML/CSS files while excluding misc.')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1], help='Project root to scan')
    parser.add_argument('--dry-run', action='store_true', help='Preview but do not write changes')
    args = parser.parse_args()

    root = args.root.resolve()
    changed = []

    for path in sorted(iter_project_files(root)):
        try:
            if path.suffix.lower() == '.html':
                if clean_html_file(path, dry_run=args.dry_run):
                    changed.append(str(path.relative_to(root)))
            elif path.suffix.lower() == '.css':
                if clean_css_file(path, dry_run=args.dry_run):
                    changed.append(str(path.relative_to(root)))
        except Exception as exc:  # pragma: no cover
            print(f'WARN: failed to process {path}: {exc}')

    if args.dry_run:
        print(f'DRY RUN: {len(changed)} files would change.')
    else:
        print(f'Updated {len(changed)} files.')

    for item in changed:
        print(item)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())