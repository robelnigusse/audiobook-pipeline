import re

import requests


def fetch_book_text(book_id):
    url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
    print(f"Fetching Book ID: {book_id}...")
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Error: Could not find book with ID {book_id}")
    return response.text


def sanitize_filename(filename):
    filename = filename.replace("\r", "").replace("\n", " ")
    filename = re.sub(r'[<>:"/\\|?*]', "", filename)
    return filename.strip()


def extract_gutenberg_field(raw_text, field_name):
    match = re.search(rf"^{field_name}:\s*(.+)$", raw_text, re.MULTILINE | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def get_book_title(raw_text):
    title = extract_gutenberg_field(raw_text, "Title")
    if title:
        return sanitize_filename(title)
    return "Unknown_Book"


def extract_body_text(raw_text):
    start_match = re.search(r"\*\*\* START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", raw_text)
    end_match = re.search(r"\*\*\* END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", raw_text)
    if start_match and end_match:
        return raw_text[start_match.end():end_match.start()].strip()
    return raw_text


def split_into_chapters(body_text):
    pattern = r"\n\s*(?:(?:CHAPTER|Chapter|Book|PART)\s+[IVXLCDM\d\.]+|(?:\b[IVXLCDM]+\b\.\s*\n)+|(?:\b[IVXLCDM]+\b\s*\n))"
    return [c.strip() for c in re.split(pattern, body_text) if len(c) > 500]

