import os
from pathlib import Path

import requests
import soundfile as sf
from kokoro import KPipeline

from .gutenberg import extract_body_text, fetch_book_text, get_book_title, split_into_chapters
from .metadata import build_book_metadata, write_book_metadata
from .supabase import upload_file_to_supabase, upload_folder_to_supabase


pipeline = KPipeline(lang_code="a")


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


def save_chapters_advanced(book_id):
    raw_text = fetch_book_text(book_id)
    book_title = get_book_title(raw_text)
    folder_name = f"{book_title}_{book_id}"

    body_text = extract_body_text(raw_text)
    chapters = split_into_chapters(body_text)

    Path(folder_name).mkdir(parents=True, exist_ok=True)
    sounds_dir = Path(folder_name) / "sounds"
    cover_dir = Path(folder_name) / "cover"
    sounds_dir.mkdir(parents=True, exist_ok=True)
    cover_dir.mkdir(parents=True, exist_ok=True)

    download_cover(book_id, str(cover_dir))
    metadata = build_book_metadata(book_id, raw_text, len(chapters))
    metadata_path = write_book_metadata(folder_name, metadata)

    for i, content in enumerate(chapters, start=0):
        generator = pipeline(
            content, voice="bm_george", speed=1, split_pattern=r"\n\n+"
            )
        file_path = os.path.join(sounds_dir, f"chapter_{i + 1:02d}.wav")
        with sf.SoundFile(file_path, mode="w", samplerate=24000, channels=1) as f:
            for _idx, (_gs, _ps, audio) in enumerate(generator):
                f.write(audio)

    upload_folder_to_supabase(str(sounds_dir), f"{folder_name}/sounds")
    upload_folder_to_supabase(str(cover_dir), f"{folder_name}/cover")
    upload_file_to_supabase(str(metadata_path), f"{folder_name}/metadata.json")

    print(f"Successfully saved to folder: {folder_name}")

