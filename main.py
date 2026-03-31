import soundfile as sf
from kokoro import KPipeline

import os
import re
import requests
from pathlib import Path
pipeline = KPipeline(lang_code='a') 

def download_cover(book_id, folder_name):
    # Standard Gutenberg cover URL pattern
    cover_url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.cover.medium.jpg"
    
    try:
        img_response = requests.get(cover_url, timeout=10)
        if img_response.status_code == 200:
            cover_path = os.path.join(folder_name, "cover.jpg")
            with open(cover_path, "wb") as f:
                f.write(img_response.content)
            print("Cover image saved as cover.jpg")
        else:
            print("No cover image found for this book ID.")
    except Exception as e:
        print(f"Could not download cover: {e}")


def sanitize_filename(filename):
    # 1. Remove \r and \n
    filename = filename.replace('\r', '').replace('\n', ' ')
    # 2. Remove characters that Windows doesn't allow in folder names
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # 3. Strip extra whitespace
    return filename.strip()

def get_book_title(raw_text):
    # Gutenberg titles usually follow 'Title: [Actual Title]'
    match = re.search(r"Title:\s+(.*)", raw_text)
    if match:
        return sanitize_filename(match.group(1))
    return "Unknown_Book"

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
    
    # 1. Strip the legal headers/footers
    start_match = re.search(r"\*\*\* START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", raw_text)
    end_match = re.search(r"\*\*\* END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", raw_text)
    
    if start_match and end_match:
        body_text = raw_text[start_match.end():end_match.start()].strip()
    else:
        body_text = raw_text

    # 2. Split into chapters
    # pattern = r'\n\s*(?:(?:CHAPTER|Chapter|Book|PART)\s+[IVXLCDM\d\.]+|(?:\b[IVXLCDM]+\b\.?))'
    pattern = r'\n\s*(?:(?:CHAPTER|Chapter|Book|PART)\s+[IVXLCDM\d\.]+|(?:\b[IVXLCDM]+\b\.\s*\n)+|(?:\b[IVXLCDM]+\b\s*\n))'
    chapters = [c.strip() for c in re.split(pattern, body_text) if len(c) > 500]
    
    # if len(chapters) == 1:
    #     print("No chapters found in this book.")
    #     chapters = [body_text]

    # 3. Create Folder Safely
    Path(folder_name).mkdir(parents=True, exist_ok=True)
    download_cover(book_id, folder_name)

    # 4. Save files
         
    for i, content in enumerate(chapters, start=0):
        generator = pipeline(
                content, voice='af_bella', 
                speed=1, split_pattern=r'\n\n+'
            ) 
        file_path = os.path.join(folder_name, f"chapter_{i+1:02d}.wav")
        with sf.SoundFile(file_path, mode='w', samplerate=24000, channels=1) as f:
            for i, (gs, ps, audio) in enumerate(generator):
                f.write(audio)

        
        
            
    print(f"Successfully saved to folder: {folder_name}")
# [12122,1063,1952,5200,11]


save_chapters_advanced(35)