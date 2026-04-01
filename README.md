# Audiobook Pipeline

Generate chapter-based audiobooks from Project Gutenberg texts, save cover/audio/metadata locally, and optionally upload outputs to Supabase Storage.

## Features

- Downloads Gutenberg plain-text books by book ID
- Extracts core book metadata
- Splits book content into chapter-like sections
- Generates `.wav` audio per chapter with Kokoro TTS
- Downloads the cover image (if available)
- Writes `metadata.json` in each book output folder
- Uploads `sounds/`, `cover/`, and `metadata.json` to Supabase (when configured)

## Project Structure

```text
audiobook_pipeline/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── gutenberg.py
│   ├── metadata.py
│   ├── processor.py
│   └── supabase.py
├── library_queue.csv
├── main.py
├── README.md
└── requirements.txt
```

## Requirements

- Python 3.11+
- Internet access for:
  - Project Gutenberg downloads
  - Supabase uploads (if enabled)
  - Kokoro model/assets

Install dependencies:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root:

```env
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-supabase-api-key
BUCKET_NAME=your-storage-bucket
```

If any value is missing, the pipeline still saves files locally and skips Supabase upload.

## Run

`main.py` accepts a CLI argument:

```powershell
python main.py --book_id 5200
```

`--book_id` defaults to `5200` when not provided:

```powershell
python main.py
```

## Output Layout

For each book, output is created in:

```text
<Book_Title>_<Book_ID>/
├── metadata.json
├── cover/
│   └── cover.jpg
└── sounds/
    ├── chapter_01.wav
    ├── chapter_02.wav
    └── ...
```

Audio format:
- WAV
- mono
- 24 kHz sample rate

## Metadata Schema

`metadata.json` contains:

```json
{
  "book_id": "5200",
  "title": "Metamorphosis",
  "author": "Franz Kafka",
  "language": "English",
  "release_date": "August 16, 2012 [eBook #5200]",
  "release_year": 2012,
  "chapter_count": 12
}
```

Fields:
- `book_id`
- `title`
- `author`
- `language`
- `release_date`
- `release_year`
- `chapter_count`

## Supabase Upload Paths

When Supabase is configured, uploads are stored as:

- `<Book_Title>_<Book_ID>/sounds/*`
- `<Book_Title>_<Book_ID>/cover/*`
- `<Book_Title>_<Book_ID>/metadata.json`

## Notes

- Chapter splitting is regex-based and may vary by book formatting.
- The pipeline currently processes one book per command.
