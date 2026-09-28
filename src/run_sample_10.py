#!/usr/bin/env python3
"""
Tamil Bible TTS — 10 Sample Verses using gTTS (Google TTS)
===========================================================
Engine  : gTTS (Google Translate Text-to-Speech)
Language: Tamil (ta)
Input   : C:\\Users\\asmit\\Downloads\\full_bible.json
Output  : D:\\bible_audio_samples\\  (MP3 files)
Cost    : $0.00 — free, uses Google Translate internally
Requires: pip install gtts

Usage:
  python run_sample_10.py           # Generate first 10 verses
  python run_sample_10.py --count 5 # Generate first 5 verses
"""

import os
import sys
import json
import time
import unicodedata
import argparse
from pathlib import Path

# ─── CONFIG ────────────────────────────────────────────────
INPUT_JSON  = r"C:\Users\asmit\Downloads\full_bible.json"
OUTPUT_DIR  = Path(r"D:\bible_audio_samples")
NUM_VERSES  = 10
LANGUAGE    = "ta"   # Tamil

# Tamil book abbreviation map
BOOK_ABBREV = {
    "ஆதியாகமம்": "Gen", "யாத்திராகமம்": "Exo", "லேவியராகமம்": "Lev",
    "எண்ணாகமம்": "Num", "உபாகமம்": "Deu", "யோசுவா": "Jos",
    "நியாயாதிபதிகள்": "Jdg", "ரூத்": "Rut", "1சாமுவேல்": "1Sa",
    "2சாமுவேல்": "2Sa", "1இராஜாக்கள்": "1Ki", "2இராஜாக்கள்": "2Ki",
    "1நாளாகமம்": "1Ch", "2நாளாகமம்": "2Ch", "எஸ்றா": "Ezr",
    "நெகேமியா": "Neh", "எஸ்தர்": "Est", "யோபு": "Job",
    "சங்கீதம்": "Psa", "நீதிமொழிகள்": "Pro", "பிரசங்கி": "Ecc",
    "உன்னதப்பாட்டு": "Son", "ஏசாயா": "Isa", "எரேமியா": "Jer",
    "புலம்பல்": "Lam", "எசேக்கியேல்": "Eze", "தானியேல்": "Dan",
    "ஓசியா": "Hos", "யோவேல்": "Joe", "ஆமோஸ்": "Amo",
    "ஒபதியா": "Oba", "யோனா": "Jon", "மீகா": "Mic",
    "நாகூம்": "Nah", "அபக்கூக்": "Hab", "செப்பனியா": "Zep",
    "ஆகாய்": "Hag", "சகரியா": "Zec", "மலாக்கி": "Mal",
    "மத்தேயு": "Mat", "மாற்கு": "Mar", "லூக்கா": "Luk",
    "யோவான்": "Joh", "அப்போஸ்தலர்": "Act", "ரோமர்": "Rom",
    "1கொரிந்தியர்": "1Co", "2கொரிந்தியர்": "2Co", "கலாத்தியர்": "Gal",
    "எபேசியர்": "Eph", "பிலிப்பியர்": "Phi", "கொலோசெயர்": "Col",
    "1தெசலோனிக்கேயர்": "1Th", "2தெசலோனிக்கேயர்": "2Th",
    "1தீமோத்தேயு": "1Ti", "2தீமோத்தேயு": "2Ti", "தீத்து": "Tit",
    "பிலேமோன்": "Phm", "எபிரேயர்": "Heb", "யாக்கோபு": "Jam",
    "1பேதுரு": "1Pe", "2பேதுரு": "2Pe", "1யோவான்": "1Jo",
    "2யோவான்": "2Jo", "3யோவான்": "3Jo", "யூதா": "Jud",
    "வெளிப்படுத்தல்": "Rev",
}
# ─────────────────────────────────────────────────────────────


def clean(text: str) -> str:
    """Normalize Tamil Unicode text before TTS."""
    text = unicodedata.normalize("NFC", text)
    text = "".join(c for c in text if not unicodedata.category(c).startswith("C"))
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u2026", "...")
    return " ".join(text.split()).strip()


def abbrev(book: str) -> str:
    return BOOK_ABBREV.get(book, book[:3].upper())


def check_gtts():
    try:
        from gtts import gTTS
        return gTTS
    except ImportError:
        print("\n[ERROR] gTTS is not installed.")
        print("  Run this first:  pip install gtts\n")
        sys.exit(1)


def generate_verse(gTTS, text: str, out_file: Path, verse_label: str) -> bool:
    """Generate TTS for one verse and save as MP3."""
    try:
        tts = gTTS(text=text, lang=LANGUAGE, slow=False)
        tts.save(str(out_file))
        return True
    except Exception as e:
        print(f"  [ERROR] {verse_label}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Tamil Bible TTS — 10 Sample Verses (gTTS, free, no install needed)"
    )
    parser.add_argument("--input", type=str, default=INPUT_JSON,
                        help=f"Path to full_bible.json (default: {INPUT_JSON})")
    parser.add_argument("--count", type=int, default=NUM_VERSES,
                        help=f"Number of verses to generate (default: {NUM_VERSES})")
    parser.add_argument("--out", type=str, default=str(OUTPUT_DIR),
                        help=f"Output directory (default: {OUTPUT_DIR})")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Check gTTS is installed
    gTTS = check_gtts()

    # Load Bible JSON
    if not os.path.exists(args.input):
        print(f"\n[ERROR] Bible JSON not found: {args.input}")
        print("  Make sure full_bible.json is at that path.\n")
        sys.exit(1)

    print(f"\nLoading Bible JSON from: {args.input}")
    with open(args.input, "r", encoding="utf-8") as f:
        verses = json.load(f)

    sample = verses[: args.count]
    total  = len(sample)

    print(f"  Loaded {len(verses):,} total verses. Generating first {total}.\n")
    print("=" * 65)
    print("  Tamil Bible TTS - Sample Generation")
    print(f"  Engine   : gTTS (Google Translate TTS)")
    print(f"  Language : Tamil (ta)")
    print(f"  Count    : {total} verses")
    print(f"  Output   : {out_dir}")
    print(f"  Format   : MP3")
    print(f"  Cost     : $0.00")
    print("=" * 65 + "\n")

    ok   = 0
    fail = 0

    for i, verse in enumerate(sample, 1):
        book    = verse.get("book", "Unknown")
        chapter = verse.get("chapter", 1)
        vnum    = verse.get("verse",   1)
        text    = clean(verse.get("text", ""))
        ab      = abbrev(book)
        label   = f"{ab} {chapter}:{vnum}"

        if not text:
            print(f"  [{i:02d}/{total}] {label}  - SKIP (empty text)")
            continue

        out_file = out_dir / f"{i:02d}_{ab}_{chapter:03d}_{vnum:03d}.mp3"

        # Skip if already generated
        if out_file.exists() and out_file.stat().st_size > 200:
            print(f"  [{i:02d}/{total}] {label}  - already exists, skipping")
            ok += 1
            continue

        print(f"  [{i:02d}/{total}] {label}  ({len(text)} chars)", end="", flush=True)
        t0      = time.time()
        success = generate_verse(gTTS, text, out_file, label)
        elapsed = time.time() - t0

        if success and out_file.exists() and out_file.stat().st_size > 200:
            size_kb = out_file.stat().st_size / 1024
            print(f"  ->  {out_file.name}  ({size_kb:.1f} KB)  [{elapsed:.1f}s]")
            ok += 1
        else:
            print(f"  ->  FAILED  [{elapsed:.1f}s]")
            fail += 1

        # Small pause to avoid rate-limiting
        time.sleep(0.5)

    print()
    print("=" * 65)
    print(f"  DONE!  {ok}/{total} verses generated successfully.")
    if fail:
        print(f"  Failed : {fail} verse(s)")
    print(f"  Files  : {out_dir}")
    print("=" * 65)
    print()
    print("--- HOW TO PROCEED -------------------------------------------")
    print("  1. Listen to the MP3s in:  D:\\bible_audio_samples\\")
    print("  2. If quality is acceptable, run the full generation:")
    print()
    print("     Full gTTS run (free, needs internet, ~31K MP3 files):")
    print("       python generate_full_gtts.py")
    print()
    print("     Full Coqui XTTS v2 run (local, best quality, WAV):")
    print("       python generate_tts.py")
    print()
    print("     Test Coqui with 10 verses only:")
    print("       python generate_tts.py --test")
    print()
    print("     Generate a specific book only (gTTS):")
    print("       python generate_full_gtts.py --book Genesis")
    print("--------------------------------------------------------------\n")


if __name__ == "__main__":
    main()
