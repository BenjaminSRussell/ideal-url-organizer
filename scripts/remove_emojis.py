#!/usr/bin/env python3
"""
Remove all emojis from markdown files
"""
import re
from pathlib import Path


def remove_emojis(text: str) -> str:
    """Remove all emojis from text"""
    # Emoji pattern - matches most emojis
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001F900-\U0001F9FF"  # supplemental symbols
        u"\U0001FA00-\U0001FAFF"  # extended symbols
        "]+",
        flags=re.UNICODE
    )

    # Remove emojis
    text = emoji_pattern.sub('', text)

    # Clean up any double spaces that might result
    text = re.sub(r'  +', ' ', text)

    # Clean up lines that have only whitespace after emoji removal
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # If line becomes empty or just whitespace after stripping, keep it as empty
        if line.strip():
            cleaned_lines.append(line)
        elif not line.strip() and line:  # Preserve intentional blank lines
            cleaned_lines.append('')
        else:
            cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)


def process_file(file_path: Path):
    """Process a single markdown file"""
    print(f"Processing: {file_path}")

    # Read file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove emojis
    cleaned_content = remove_emojis(content)

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)

    print(f"  Cleaned: {file_path.name}")


def main():
    """Process all markdown files"""
    base_dir = Path(__file__).parent.parent

    # Find all markdown files (excluding data/ subdirectories)
    md_files = [
        base_dir / 'README.md',
        base_dir / 'IMPLEMENTATION_SUMMARY.md',
        base_dir / 'EXPERT_FEATURES.md',
        base_dir / 'WHATS_NEW.md',
        base_dir / 'ADVANCED_EXTRACTION.md',
        base_dir / 'FINAL_SUMMARY.md',
    ]

    print("Removing emojis from markdown files...")
    print("=" * 80)

    for md_file in md_files:
        if md_file.exists():
            process_file(md_file)

    print("=" * 80)
    print("Done! All emojis removed.")


if __name__ == '__main__':
    main()
