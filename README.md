# Audiobook Pipeline

Generate chapter-based audiobooks from Project Gutenberg texts, save cover/audio/metadata locally, and optionally upload outputs to Supabase Storage.

## Features

- Downloads Gutenberg plain-text books by ID
- Pulls metadata from Gutendex: `https://gutendex.com/books/{id}`
- Splits book content into chapter sections
- Generates `.wav` audio per chapter with Kokoro TTS
- Downloads a cover image when available
- Writes `metadata.json` in each book output folder
- Uploads `sounds/`, `cover/`, and `metadata.json` to Supabase (when configured)

## Project Structure

```text
audiobook_pipeline/
|- src/
|  |- __init__.py
|  |- config.py
|  |- gutenberg.py
|  |- metadata.py
|  |- processor.py
|  `- supabase.py
|- library_queue.csv
|- main.py
|- README.md
`- requirements.txt
```

## Requirements

- Python 3.11+
- Internet access for:
  - Gutenberg downloads
  - Gutendex metadata requests
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

If any value is missing, local files are still saved and Supabase upload is skipped.

## Run

`main.py` supports `--book_id`:

```powershell
python main.py --book_id 5200
```

Default value is `5200`:

```powershell
python main.py
```

## Output Layout

For each processed book:

```text
<Book_Title>_<Book_ID>/
|- metadata.json
|- cover/
|  `- cover.jpg
`- sounds/
   |- chapter_01.wav
   |- chapter_02.wav
   `- ...
```

Audio format:

- WAV
- mono
- 24 kHz sample rate

## Metadata Source and Schema

Metadata is sourced from Gutendex (`/books/{id}`)

`metadata.json` contains:

```json
{
  "book_id": "1211",
  "title": "A Selection from the Lyrical Poems of Robert Herrick",
  "author": "Herrick, Robert",
  "language": "en",
  "release_year": 2012,
  "chapter_count": 10,
  "Category": [
    "Category: Classics of Literature",
    "Category: German Literature",
    "Category: Novels",
    "Horror"
  ]
}
```

Fields:

- `book_id`
- `title`
- `author`
- `language`
- `release_year`
- `chapter_count`
- `Category`

## Supabase Upload Paths

When Supabase is configured:

- `<Book_Title>_<Book_ID>/sounds/*`
- `<Book_Title>_<Book_ID>/cover/*`
- `<Book_Title>_<Book_ID>/metadata.json`

## Notes

- Chapter splitting is regex-based and may vary by book formatting.
- The pipeline currently processes one book per command.
