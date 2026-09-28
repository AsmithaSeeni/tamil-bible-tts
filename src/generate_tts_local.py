#!/usr/bin/env python3
"""
Tamil Bible TTS Generator — Coqui TTS XTTS v2 (Female Voice, Local)
====================================================================
Model  : tts_models/multilingual/multi-dataset/xtts_v2
Voice  : Female — zero-shot cloning from SPEAKER_WAV,
         or built-in female speaker if WAV not found.
Format : WAV (24kHz)
Input  : C:/Users/asmit/Downloads/full_bible.json
Output : D:/bible_audio_google/<BookName>/<Abbrev>_<CCC>_<VVV>.wav
Cost   : $0.00  |  No API Key  |  100% Local after first download (~1.9 GB)

Usage:
  python generate_tts_local.py              # Full generation (all verses)
  python generate_tts_local.py --test       # Test run (10 verses only)
  python generate_tts_local.py --book NAME  # Single Tamil book name
  python generate_tts_local.py --chapter N  # Specific chapter (use with --book)
  python generate_tts_local.py --speaker PATH  # Custom female speaker WAV
"""

import os
import sys
import json
import time
import logging
import argparse
import unicodedata
from pathlib import Path
from datetime import datetime, timedelta
from tqdm import tqdm

# ─────────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────────
INPUT_JSON    = r"C:\Users\asmit\Downloads\full_bible.json"
OUTPUT_DIR    = r"D:\bible_audio_google"
LOG_FILE      = r"D:\google_bible_tts\generation_log_coqui.txt"
MANIFEST_FILE = r"D:\google_bible_tts\manifest_coqui.json"

# Coqui TTS model ID
MODEL_ID = "tts_models/multilingual/multi-dataset/xtts_v2"
LANGUAGE = "ta"  # Tamil language code

# ── Female Voice ────────────────────────────────────────────────────────────
# Option A: Provide a 6-10 second clean Tamil FEMALE speaker WAV.
#           Enables zero-shot voice cloning — best quality for Tamil female.
#           Replace the path below with your actual female speaker WAV.
SPEAKER_WAV = r"D:\tamil_speaker_ref.wav"

# Option B: Built-in XTTS v2 female speaker.
#           Used automatically if SPEAKER_WAV file does not exist.
BUILTIN_FEMALE_SPEAKER = "Claribel Dervla"
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────
#  BOOK NAME MAPPING (Tamil -> Abbreviated ID)
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
#  LOGGING SETUP
# ─────────────────────────────────────────────
logger = logging.getLogger(__name__)


def setup_logging():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ]
    )


# ─────────────────────────────────────────────
#  TEXT PREPROCESSING
# ─────────────────────────────────────────────
def clean_tamil_text(text: str) -> str:
    """Normalize Tamil Unicode text before TTS synthesis."""
    text = unicodedata.normalize("NFC", text)
    text = "".join(c for c in text if not unicodedata.category(c).startswith("C"))
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u2026", "...")
    text = " ".join(text.split())
    return text.strip()


# ─────────────────────────────────────────────
#  FILE / PATH HELPERS
# ─────────────────────────────────────────────
def get_output_path(book: str, chapter: int, verse: int) -> Path:
    abbrev   = BOOK_ABBREV.get(book, book[:3].upper())
    book_dir = Path(OUTPUT_DIR) / book
    book_dir.mkdir(parents=True, exist_ok=True)
    return book_dir / f"{abbrev}_{chapter:03d}_{verse:03d}.wav"


def file_already_exists(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 500


# ─────────────────────────────────────────────
#  COQUI TTS ENGINE (XTTS v2 — Female Voice)
# ─────────────────────────────────────────────
class CoquiTamilTTS:
    """
    Coqui TTS XTTS v2 wrapper for Tamil female voice synthesis.

    Voice mode (auto-selected):
      - If SPEAKER_WAV exists  → zero-shot voice cloning from that WAV
                                  (ideal for Tamil female voice quality)
      - If SPEAKER_WAV missing → uses built-in female speaker 'Claribel Dervla'

    First run downloads the model (~1.9 GB) and caches it locally.
    All subsequent runs are fully offline.
    """

    def __init__(self, speaker_wav: str, builtin_speaker: str = BUILTIN_FEMALE_SPEAKER):
        try:
            import torch
            from TTS.api import TTS as CoquiTTS
        except ImportError:
            raise ImportError(
                "coqui-tts is not installed. Run:\n"
                "    pip install coqui-tts\n"
            )

        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Device       : {device.upper()}")
        logger.info("Loading Coqui TTS XTTS v2 model...")
        logger.info("(First run downloads ~1.9 GB — subsequent runs use local cache.)")

        self.tts_engine = CoquiTTS(MODEL_ID).to(device)

        # Auto-select voice mode
        if os.path.isfile(speaker_wav):
            self.speaker_wav     = speaker_wav
            self.builtin_speaker = None
            self.voice_mode      = "zero-shot-cloning"
            logger.info(f"Voice mode   : Zero-shot cloning → {speaker_wav}")
        else:
            self.speaker_wav     = None
            self.builtin_speaker = builtin_speaker
            self.voice_mode      = "builtin-female"
            logger.warning(
                f"Speaker WAV not found: {speaker_wav}\n"
                f"  Falling back to built-in female speaker: '{builtin_speaker}'"
            )

        self.sample_rate = 24000
        logger.info(f"Model ready! Sample rate: {self.sample_rate} Hz | Language: Tamil (ta)")

    def synthesize_and_save(self, text: str, output_path: Path) -> bool:
        """Convert Tamil text to female speech and save as WAV. Returns True on success."""
        text = clean_tamil_text(text)
        if not text:
            return False

        try:
            if self.voice_mode == "zero-shot-cloning":
                self.tts_engine.tts_to_file(
                    text=text,
                    speaker_wav=self.speaker_wav,
                    language=LANGUAGE,
                    file_path=str(output_path),
                )
            else:
                self.tts_engine.tts_to_file(
                    text=text,
                    speaker=self.builtin_speaker,
                    language=LANGUAGE,
                    file_path=str(output_path),
                )
            return True
        except Exception as e:
            logger.error(f"Synthesis error: {e}")
            return False


# ─────────────────────────────────────────────
#  MANIFEST
# ─────────────────────────────────────────────
def save_manifest(manifest: dict):
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────
#  MAIN GENERATION PIPELINE
# ─────────────────────────────────────────────
def run_generation(
    verses: list,
    speaker_wav: str,
    test_mode: bool = False,
    filter_book: str = None,
    filter_chapter: int = None,
):
    if filter_book:
        verses = [v for v in verses if v.get("book") == filter_book]
        logger.info(f"Filtered to book: {filter_book} ({len(verses)} verses)")
    if filter_chapter is not None:
        verses = [v for v in verses if int(v.get("chapter", 0)) == filter_chapter]
        logger.info(f"Filtered to chapter: {filter_chapter} ({len(verses)} verses)")
    if not verses:
        logger.error("No verses matched the given filters.")
        return
    if test_mode:
        verses = verses[:10]
        logger.info("TEST MODE: Processing first 10 verses only")

    total = len(verses)

    logger.info(f"\n{'='*60}")
    logger.info(f"  Tamil Bible TTS — Coqui XTTS v2 (Female Voice)")
    logger.info(f"  Model       : {MODEL_ID}")
    logger.info(f"  Speaker WAV : {speaker_wav}")
    logger.info(f"  Language    : Tamil (ta)")
    logger.info(f"  Verses      : {total:,}")
    logger.info(f"  Output dir  : {OUTPUT_DIR}")
    logger.info(f"  Cost        : $0.00 (fully local)")
    logger.info(f"{'='*60}\n")

    stats = {
        "total": total, "generated": 0, "skipped": 0, "errors": 0,
        "start_time": datetime.now().isoformat(),
        "model": MODEL_ID, "language": LANGUAGE, "voice": "female", "verses": []
    }

    # Resume support
    if os.path.exists(MANIFEST_FILE) and not test_mode:
        try:
            with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
                old = json.load(f)
            stats["generated"] = old.get("generated", 0)
            stats["verses"]    = old.get("verses", [])
            logger.info(f"Resuming — already completed: {stats['generated']:,}")
        except Exception:
            pass

    tts        = CoquiTamilTTS(speaker_wav=speaker_wav)
    start_time = time.time()

    with tqdm(total=total, desc="Generating", unit="verse",
              dynamic_ncols=True, colour="green") as pbar:

        for i, verse in enumerate(verses):
            book    = verse.get("book", "Unknown")
            chapter = int(verse.get("chapter", 1))
            verse_n = int(verse.get("verse", 1))
            text    = verse.get("text", "")

            output_path = get_output_path(book, chapter, verse_n)

            if file_already_exists(output_path) and not test_mode:
                stats["skipped"] += 1
                pbar.update(1)
                continue

            success = tts.synthesize_and_save(text, output_path)

            if success:
                size = output_path.stat().st_size
                stats["generated"] += 1
                stats["verses"].append({
                    "book": book, "chapter": chapter, "verse": verse_n,
                    "file": str(output_path),
                    "text_preview": text[:80] + ("..." if len(text) > 80 else ""),
                    "size_bytes": size,
                })
                logger.info(f"  ✓ {book} {chapter}:{verse_n} → {output_path.name} ({size/1024:.1f} KB)")
            else:
                stats["errors"] += 1
                logger.error(f"  ✗ FAILED: {book} {chapter}:{verse_n}")

            pbar.update(1)

            elapsed   = time.time() - start_time
            processed = stats["generated"] + stats["errors"]
            if processed > 0:
                remaining = (total - i - 1) / (processed / elapsed)
                pbar.set_postfix({
                    "book": book[:8],
                    "done": stats["generated"],
                    "ETA":  str(timedelta(seconds=int(remaining))),
                })

            if (i + 1) % 50 == 0:
                save_manifest(stats)

    stats["end_time"]           = datetime.now().isoformat()
    stats["total_time_seconds"] = int(time.time() - start_time)
    save_manifest(stats)

    logger.info(f"\n{'='*60}")
    logger.info(f"  GENERATION COMPLETE!")
    logger.info(f"  Generated : {stats['generated']:,} files")
    logger.info(f"  Skipped   : {stats['skipped']:,} (already existed)")
    logger.info(f"  Errors    : {stats['errors']:,}")
    logger.info(f"  Time taken: {timedelta(seconds=stats['total_time_seconds'])}")
    logger.info(f"  Output    : {OUTPUT_DIR}")
    logger.info(f"{'='*60}\n")

    if test_mode:
        logger.info("[OK] TEST COMPLETE — listen to files in:")
        logger.info(f"     {OUTPUT_DIR}")
        logger.info("     If quality is good, run without --test for full generation.")


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Tamil Bible TTS — Coqui XTTS v2 (Female Voice, No API, No Billing)"
    )
    parser.add_argument("--test",    action="store_true",
                        help="Test run (first 10 verses only)")
    parser.add_argument("--book",    type=str, default=None,
                        help="Process only a specific Tamil book name")
    parser.add_argument("--chapter", type=int, default=None,
                        help="Process only a specific chapter (use with --book)")
    parser.add_argument("--input",   type=str, default=INPUT_JSON,
                        help=f"Path to input JSON (default: {INPUT_JSON})")
    parser.add_argument("--speaker", type=str, default=SPEAKER_WAV,
                        help=f"Path to female speaker reference WAV (default: {SPEAKER_WAV})")
    args = parser.parse_args()

    setup_logging()

    input_path = args.input
    if not os.path.exists(input_path):
        logger.error(f"Input file not found: {input_path}")
        sys.exit(1)

    logger.info(f"Loading Bible JSON from: {input_path}")
    with open(input_path, "r", encoding="utf-8") as f:
        verses = json.load(f)
    logger.info(f"Loaded {len(verses):,} verses")

    run_generation(
        verses=verses,
        speaker_wav=args.speaker,
        test_mode=args.test,
        filter_book=args.book,
        filter_chapter=args.chapter,
    )


if __name__ == "__main__":
    main()
