#!/usr/bin/env python3
"""
Tamil Bible TTS - 10 Sample Verses (Female Voice)
=================================================
Engine  : Coqui TTS XTTS v2 — Multilingual (Tamil via language code "ta")
Voice   : Female — zero-shot cloning from SPEAKER_WAV,
          or built-in female speaker 'Claribel Dervla' if WAV not found.
Input   : C:/Users/asmit/Downloads/full_bible.json
Output  : D:\\bible_audio_google\\samples_coqui\\
Cost    : $0.00  |  No API Key  |  100% Local after first download (~1.9 GB)

Usage:
  python sample_10_verses.py                   # Generate 10 samples
  python sample_10_verses.py --speaker PATH    # Use custom female speaker WAV
  python sample_10_verses.py --count N         # Generate N samples instead of 10
"""

import sys, json, unicodedata, time, os, argparse
from typing import Optional

from pathlib import Path

# ── Config ───────────────────────────────────────────
INPUT_JSON = r"C:\Users\asmit\Downloads\full_bible.json"
#python src/generate_tts_local.py --input path/to/full_bible.json
OUTPUT_DIR = Path(r"D:\bible_audio_google\samples_coqui")
NUM_VERSES = 10
LANGUAGE   = "ta"       # Tamil language code for XTTS v2

# Coqui TTS model
MODEL_ID = "tts_models/multilingual/multi-dataset/xtts_v2"

# ── Female Voice ─────────────────────────────────────
# Option A: Provide a 6-10 second clean Tamil FEMALE speaker WAV.
#           Enables zero-shot voice cloning — best quality for Tamil female.
SPEAKER_WAV = r"D:\tamil_speaker_ref.wav"

# Option B: Built-in XTTS v2 female speaker.
#           Used automatically if SPEAKER_WAV file does not exist.
BUILTIN_FEMALE_SPEAKER = "Claribel Dervla"
# ─────────────────────────────────────────────────────

BOOK_ABBREV = {
    "ஆதியாகமம்": "Gen",  "யாத்திராகமம்": "Exo", "லேவியராகமம்": "Lev",
    "எண்ணாகமம்": "Num",  "உபாகமம்": "Deu",       "யோசுவா": "Jos",
    "சங்கீதம்": "Psa",   "மத்தேயு": "Mat",        "மாற்கு": "Mar",
    "லூக்கா": "Luk",     "யோவான்": "Joh",         "அப்போஸ்தலர்": "Act",
}

def abbrev(book): return BOOK_ABBREV.get(book, "Bk")


def clean(text: str) -> str:
    """Normalize Tamil Unicode text before TTS synthesis."""
    text = unicodedata.normalize("NFC", text)
    text = "".join(c for c in text if not unicodedata.category(c).startswith("C"))
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u2026", "...")
    return " ".join(text.split()).strip()


def load_tts(speaker_wav: str):
    """
    Load Coqui TTS XTTS v2 with female voice selection.
    Downloads ~1.9 GB on first run, then uses local cache.

    Returns: (tts_instance, voice_mode, speaker_wav_or_None, builtin_or_None)
    """
    try:
        import torch
        from TTS.api import TTS
    except ImportError:
        print("\n[ERROR] coqui-tts is not installed. Run:")
        print("    pip install coqui-tts\n")
        sys.exit(1)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"  Device       : {device.upper()}")
    print(f"  Loading XTTS v2 on {device.upper()}...")
    print("  (First run downloads ~1.9 GB — subsequent runs use local cache)")

    tts = TTS(MODEL_ID).to(device)

    if os.path.isfile(speaker_wav):
        voice_mode      = "zero-shot-cloning"
        effective_wav   = speaker_wav
        effective_spkr  = None
        print(f"  Voice mode   : Zero-shot cloning → {speaker_wav}")
    else:
        voice_mode      = "builtin-female"
        effective_wav   = None
        effective_spkr  = BUILTIN_FEMALE_SPEAKER
        print(f"  Speaker WAV not found: {speaker_wav}")
        print(f"  Voice mode   : Built-in female speaker '{BUILTIN_FEMALE_SPEAKER}'")

    print(f"  Model ready!\n")
    return tts, voice_mode, effective_wav, effective_spkr


def synthesize_verse(tts, voice_mode: str, wav: Optional[str], spkr: Optional[str],
                     text: str, out_file: Path) -> bool:
    """Synthesize a single verse to WAV using female voice."""
    try:
        if voice_mode == "zero-shot-cloning":
            tts.tts_to_file(
                text=text,
                speaker_wav=wav,
                language=LANGUAGE,
                file_path=str(out_file),
            )
        else:
            tts.tts_to_file(
                text=text,
                speaker=spkr,
                language=LANGUAGE,
                file_path=str(out_file),
            )
        return True
    except Exception as e:
        print(f"  [ERROR] Synthesis failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Tamil Bible TTS — 10 Sample Verses (Coqui XTTS v2, Female Voice)"
    )
    parser.add_argument("--speaker", type=str, default=SPEAKER_WAV,
                        help=f"Path to female speaker reference WAV (default: {SPEAKER_WAV})")
    parser.add_argument("--count",   type=int, default=NUM_VERSES,
                        help=f"Number of sample verses to generate (default: {NUM_VERSES})")
    parser.add_argument("--input",   type=str, default=INPUT_JSON,
                        help=f"Path to input JSON (default: {INPUT_JSON})")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading Bible JSON...")
    if not os.path.exists(args.input):
        print(f"[ERROR] Input file not found: {args.input}")
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        verses = json.load(f)
    sample = verses[:args.count]
    print(f"  Loaded {len(verses):,} total verses. Using first {args.count}.\n")

    print("=" * 60)
    print("  Tamil Bible TTS — Sample Generation")
    print(f"  Engine  : Coqui TTS XTTS v2")
    print(f"  Model   : {MODEL_ID}")
    print(f"  Voice   : Female")
    print(f"  Speaker : {args.speaker}")
    print(f"  Cost    : $0.00  |  No API key  |  Fully local")
    print(f"  Output  : {OUTPUT_DIR}")
    print("=" * 60)

    tts, voice_mode, effective_wav, effective_spkr = load_tts(args.speaker)

    ok = 0
    for i, verse in enumerate(sample, 1):
        book    = verse.get("book", "Unknown")
        chapter = verse.get("chapter", 1)
        vnum    = verse.get("verse", 1)
        text    = clean(verse.get("text", ""))
        ab      = abbrev(book)

        if not text:
            print(f"  [{i:02d}/{args.count}] SKIP - empty text")
            continue

        out_file = OUTPUT_DIR / f"sample_{i:02d}_{ab}_{chapter}_{vnum}.wav"
        print(f"  [{i:02d}/{args.count}] {ab} {chapter}:{vnum}  ({len(text)} chars)")

        t0      = time.time()
        success = synthesize_verse(tts, voice_mode, effective_wav, effective_spkr, text, out_file)
        elapsed = time.time() - t0

        if success and out_file.exists():
            size = out_file.stat().st_size / 1024
            print(f"         Saved: {out_file.name}  ({size:.1f} KB)  [{elapsed:.1f}s]\n")
            ok += 1
        else:
            print(f"         FAILED  [{elapsed:.1f}s]\n")

    print("=" * 60)
    print(f"  Done! {ok}/{args.count} verses generated successfully.")
    print(f"  Files in: {OUTPUT_DIR}")
    print(f"  Format: WAV 24kHz (plays in any media player)")
    print("=" * 60)


if __name__ == "__main__":
    main()
