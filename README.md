# Audiobook Pipeline

This project turns Project Gutenberg books into chapter-by-chapter audiobook files using the `kokoro` text-to-speech pipeline.

For a given Gutenberg book ID, the script:

- downloads the plain-text ebook from Project Gutenberg
- extracts the book title from the metadata
- removes the standard Gutenberg header and footer
- splits the book into chapter-sized sections with a regex-based parser
- generates a WAV file for each chapter using Kokoro TTS
- downloads the Gutenberg cover image when one is available

## What is in the repo

- `main.py` - the current end-to-end script
- `library_queue.csv` - a list of Gutenberg books that could be used as future input
- `README.md` - project documentation

## Requirements

- Python 3.11+ recommended
- Internet access for:
  - fetching Gutenberg text files
  - fetching cover images
  - downloading Kokoro model assets on first run

Python packages used by the script:

- `kokoro`
- `soundfile`
- `requests`

## Setup

Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install kokoro soundfile requests
```

## How it works

The main entry point is currently hardcoded at the bottom of `main.py`:

```python
save_chapters_advanced(35)
```

That means running the script will generate audio for Gutenberg book ID `35`.

To process a different book, change that number to another Gutenberg ID:

```python
save_chapters_advanced(84)
```

Then run:

```powershell
python main.py
```

## Output

For each processed book, the script creates a folder named like:

```text
<Book_Title>_<Gutenberg_ID>
```

Example:

```text
The_Time_Machine_35
```

Inside that folder you should get:

- `cover.jpg` if Gutenberg has a matching cover image
- `chapter_01.wav`
- `chapter_02.wav`
- `chapter_03.wav`
- and so on

Audio is written as:

- WAV format
- mono
- 24 kHz sample rate

## Project structure and behavior

Key functions in `main.py`:

- `download_cover(book_id, folder_name)` downloads the Gutenberg cover image
- `sanitize_filename(filename)` removes characters that are invalid in Windows folder names
- `get_book_title(raw_text)` extracts the book title from Gutenberg metadata
- `save_chapters_advanced(book_id)` downloads the book, splits chapters, and writes chapter audio files

The TTS pipeline is initialized with:

```python
pipeline = KPipeline(lang_code='a')
```

and chapter audio is generated with:

```python
voice='af_bella'
speed=1
split_pattern=r'\n\n+'
```

## Notes and current limitations

- The script currently processes one hardcoded Gutenberg ID at a time.
- `library_queue.csv` is present in the repo, but it is not yet connected to the script.
- Chapter splitting is regex-based, so books with unusual formatting may split poorly.
- Very short sections are skipped because only chunks longer than 500 characters are kept.
- Output is written as WAV only; there is no MP3 or M4B packaging yet.
- Error handling is minimal, so network failures or unusual source formatting may require manual retries or code tweaks.

## Example use cases

- generating public-domain audiobook drafts
- testing Kokoro voices on long-form text
- building a batch audiobook workflow from Gutenberg sources
- experimenting with chapter segmentation for TTS pipelines

## Future improvements

- read book IDs directly from `library_queue.csv`
- accept book IDs from the command line
- support configurable voice, speed, and output format
- improve chapter detection for inconsistent ebook formatting
- add retries, logging, and better failure reporting
- export metadata for audiobook players

## License and source content

This repository contains code for generating audio from public-domain Project Gutenberg texts. Make sure you review the terms and usage guidance for any external models, packages, or source content you use with this pipeline.
