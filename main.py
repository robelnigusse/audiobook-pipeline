import soundfile as sf
from kokoro import KPipeline

import os
import re
import requests
import mimetypes
import json
from pathlib import Path
from dotenv import load_dotenv

pipeline = KPipeline(lang_code='a') 

load_dotenv()


def get_supabase_config():
    
    supabase_url = os.getenv("SUPABASE_URL","")

    supabase_api_key = os.getenv("SUPABASE_KEY","")
    
    bucket_name = os.getenv("BUCKET_NAME","")
    return supabase_url, supabase_api_key, bucket_name


def upload_file_to_supabase(local_file_path, remote_path):
    supabase_url, supabase_api_key, bucket_name = get_supabase_config()
    if not supabase_url or not supabase_api_key or not bucket_name:
        print("Supabase config not set. Skipping upload.")
        return

    upload_url = f"{supabase_url}/storage/v1/object/{bucket_name}/{remote_path}"
    content_type = mimetypes.guess_type(local_file_path)[0] or "application/octet-stream"
    headers = {
        "apikey": supabase_api_key,
        "Authorization": f"Bearer {supabase_api_key}",
        "Content-Type": content_type,
        "x-upsert": "true",
    }

    with open(local_file_path, "rb") as f:
        response = requests.post(upload_url, headers=headers, data=f)

    # If object already exists and POST fails, try update.
    if response.status_code in (400, 409):
        with open(local_file_path, "rb") as f:
            response = requests.put(upload_url, headers=headers, data=f)

    if response.status_code not in (200, 201):
        print(f"Failed upload: {remote_path} -> {response.status_code} {response.text}")
    else:
        print(f"Uploaded to Supabase: {remote_path}")


def upload_folder_to_supabase(local_folder, remote_prefix):
    folder = Path(local_folder)
    if not folder.exists():
        return
    for file_path in folder.rglob("*"):
        if file_path.is_file():
            remote_path = f"{remote_prefix}/{file_path.relative_to(folder).as_posix()}"
            upload_file_to_supabase(str(file_path), remote_path)


def download_cover(book_id, cover_folder):
  
    cover_url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.cover.medium.jpg"
    
    try:
        img_response = requests.get(cover_url, timeout=10)
        if img_response.status_code == 200:
            cover_path = os.path.join(cover_folder, "cover.jpg")
            with open(cover_path, "wb") as f:
                f.write(img_response.content)
            print("Cover image saved as cover.jpg")
        else:
            print("No cover image found for this book ID.")
    except Exception as e:
        print(f"Could not download cover: {e}")


def sanitize_filename(filename):
    # Remove \r and \n
    filename = filename.replace('\r', '').replace('\n', ' ')
    # Remove characters that Windows doesn't allow in folder names
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Strip extra whitespace
    return filename.strip()

def get_book_title(raw_text):
    # Gutenberg titles usually follow 'Title: [Actual Title]'
    match = re.search(r"Title:\s+(.*)", raw_text)
    if match:
        return sanitize_filename(match.group(1))
    return "Unknown_Book"


def extract_gutenberg_field(raw_text, field_name):
    match = re.search(rf"^{field_name}:\s*(.+)$", raw_text, re.MULTILINE | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


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
    

    metadata = {
        "book_id": str(book_id),
        "title": title,
        "author": author,
        "language": language,
        "release_date": release_date,
        "release_year": extract_release_year(release_date),
        "chapter_count": chapter_count,
    }
    return metadata


def write_book_metadata(folder_name, metadata):
    metadata_path = Path(folder_name) / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"Metadata saved: {metadata_path}")
    return metadata_path

def save_chapters_advanced(book_id):
    url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
    print(f"Fetching Book ID: {book_id}...")
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Error: Could not find book with ID {book_id}")
        return

    raw_text = response.text
    
    # Extract and clean Title
    book_title = get_book_title(raw_text)
    folder_name = f"{book_title}_{book_id}"
    
    #  Strip the legal headers/footers
    start_match = re.search(r"\*\*\* START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", raw_text)
    end_match = re.search(r"\*\*\* END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", raw_text)
    
    if start_match and end_match:
        body_text = raw_text[start_match.end():end_match.start()].strip()
    else:
        body_text = raw_text

    #  Split into chapters
    # pattern = r'\n\s*(?:(?:CHAPTER|Chapter|Book|PART)\s+[IVXLCDM\d\.]+|(?:\b[IVXLCDM]+\b\.?))'
    pattern = r'\n\s*(?:(?:CHAPTER|Chapter|Book|PART)\s+[IVXLCDM\d\.]+|(?:\b[IVXLCDM]+\b\.\s*\n)+|(?:\b[IVXLCDM]+\b\s*\n))'
    chapters = [c.strip() for c in re.split(pattern, body_text) if len(c) > 500]
    

    # Create folder structure safely
    Path(folder_name).mkdir(parents=True, exist_ok=True)
    sounds_dir = Path(folder_name) / "sounds"
    cover_dir = Path(folder_name) / "cover"
    sounds_dir.mkdir(parents=True, exist_ok=True)
    cover_dir.mkdir(parents=True, exist_ok=True)
    download_cover(book_id, str(cover_dir))
    metadata = build_book_metadata(book_id, raw_text, len(chapters))
    metadata_path = write_book_metadata(folder_name, metadata)

    #  Save files
         
    for i, content in enumerate(chapters, start=0):
        generator = pipeline(
                "text-to-speech with vocoder", voice='af_bella', 
                speed=1, split_pattern=r'\n\n+'
            ) 
        file_path = os.path.join(sounds_dir, f"chapter_{i+1:02d}.wav")
        with sf.SoundFile(file_path, mode='w', samplerate=24000, channels=1) as f:
            for i, (gs, ps, audio) in enumerate(generator):
                f.write(audio)

    #  Upload generated assets to Supabase bucket
    upload_folder_to_supabase(str(sounds_dir), f"{folder_name}/sounds")
    upload_folder_to_supabase(str(cover_dir), f"{folder_name}/cover")
    upload_file_to_supabase(str(metadata_path), f"{folder_name}/metadata.json")
        
        
            
    print(f"Successfully saved to folder: {folder_name}")
# [12122,1063,1952,5200,11]


save_chapters_advanced(11)
