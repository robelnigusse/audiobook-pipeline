import json
import re
from pathlib import Path
import requests

from .gutenberg import extract_gutenberg_field


def extract_release_year(release_date):
    if not release_date:
        return None
    year_match = re.search(r"\b(1[6-9]\d{2}|20\d{2})\b", release_date)
    if year_match:
        return int(year_match.group(1))
    return None

def fetch_gutendex_metadata(book_id):
    url = f"https://gutendex.com/books/{book_id}"
    
    try :
        response = requests.get(url)
    except Exception as e:
        raise ValueError(f"Error fetching Gutendex metadata for book id {book_id}: {e}")    
    return response.json()


def normalize_author(authors):
    if not authors:
        return None
    first_author = authors[0]
    return first_author.get("name")


def normalize_language(languages):
    if not languages:
        return None
    return languages[0]



def build_book_metadata(book_id, raw_text, chapter_count):
    release_date = extract_gutenberg_field(raw_text, "Release Date")
    release_year = extract_release_year(release_date)

    gutendex_data = fetch_gutendex_metadata(book_id)
    title = gutendex_data.get("title") or "Unknown_Book"
    author = normalize_author(gutendex_data.get("authors", []))
    language = normalize_language(gutendex_data.get("languages", []))
    category = gutendex_data.get("bookshelves", [])

    return {
        "book_id": str(book_id),
        "title": title,
        "author": author,
        "language": language,
        "release_year": release_year,
        "chapter_count": chapter_count,
        "Category": category,
    }


def write_book_metadata(folder_name, metadata):
    metadata_path = Path(folder_name) / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"Metadata saved: {metadata_path}")
    return metadata_path
