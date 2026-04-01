import json
import re
from pathlib import Path

from .gutenberg import extract_gutenberg_field


def extract_release_year(release_date):
    if not release_date:
        return None
    year_match = re.search(r"\b(1[6-9]\d{2}|20\d{2})\b", release_date)
    if year_match:
        return int(year_match.group(1))
    return None


def build_book_metadata(book_id, raw_text, chapter_count):
    title = extract_gutenberg_field(raw_text, "Title") or "Unknown_Book"
    author = extract_gutenberg_field(raw_text, "Author")
    language = extract_gutenberg_field(raw_text, "Language")
    release_date = extract_gutenberg_field(raw_text, "Release Date")
    

    return {
        "book_id": str(book_id),
        "title": title,
        "author": author,
        "language": language,
        "release_date": release_date,
        "release_year": extract_release_year(release_date),
        "chapter_count": chapter_count,
    }


def write_book_metadata(folder_name, metadata):
    metadata_path = Path(folder_name) / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"Metadata saved: {metadata_path}")
    return metadata_path

