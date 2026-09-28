#!/usr/bin/env python3
"""
Tamil Bible TTS — Full Generation (All 31,102 Verses)
=====================================================
Engine  : Coqui TTS XTTS v2 — Multilingual (Tamil via language code "ta")
Voice   : Female — zero-shot cloning from SPEAKER_WAV, or built-in female speaker
Model   : tts_models/multilingual/multi-dataset/xtts_v2
Input   : C:/Users/asmit/Downloads/full_bible.json
Output  : D:\\bible_audio_google\\<BookName>\\<Abbrev>_<CCC>_<VVV>.wav
Resume  : Skips already-generated files automatically
Cost    : $0.00  |  No API Key  |  100% Local (~1.9 GB first download)
"""

import io, sys, json, unicodedata, time, os, logging
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from pathlib import Path
from datetime import datetime, timedelta
from tqdm import tqdm

# ── Config ───────────────────────────────────────────
INPUT_JSON    = r"C:\Users\asmit\Downloads\full_bible.json"
OUTPUT_DIR    = Path(r"D:\bible_audio_google")
LOG_FILE      = r"D:\google_bible_tts\generation_log_coqui_full.txt"
MANIFEST_FILE = r"D:\google_bible_tts\manifest_coqui_full.json"

# Coqui TTS model ID
MODEL_ID  = "tts_models/multilingual/multi-dataset/xtts_v2"
LANGUAGE  = "ta"   # Tamil

# ── Female Voice ─────────────────────────────────────
# Option A: Provide a 6-10 second clean Tamil FEMALE speaker WAV.
#           This gives the most natural Tamil female voice via zero-shot cloning.
#           Replace the path below with your actual female speaker WAV.
SPEAKER_WAV = r"D:\tamil_speaker_ref.wav"

# Option B: Built-in XTTS v2 female speaker — used as fallback if SPEAKER_WAV not found.
BUILTIN_FEMALE_SPEAKER = "Claribel Dervla"
# ─────────────────────────────────────────────────────

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

logger = logging.getLogger(__name__)


def clean(text: str) -> str:
    """Normalize Tamil Unicode text before TTS synthesis."""
    text = unicodedata.normalize("NFC", text)
    text = "".join(c for c in text if not unicodedata.category(c).startswith("C"))
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u2026", "...")
    return " ".join(text.split()).strip()


def get_output_path(book: str, chapter: int, verse: int) -> Path:
    abbrev   = BOOK_ABBREV.get(book, book[:3].upper())
    book_dir = OUTPUT_DIR / book
    book_dir.mkdir(parents=True, exist_ok=True)
    return book_dir / f"{abbrev}_{chapter:03d}_{verse:03d}.wav"


def file_ok(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 500


def save_manifest(stats: dict):
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


def load_tts():
    """
    Load Coqui TTS XTTS v2 with female voice.
    Downloads ~1.9 GB on first run, then uses local cache.

    Voice mode:
      - If SPEAKER_WAV exists  → zero-shot cloning from Tamil female WAV
      - If SPEAKER_WAV missing → uses built-in female speaker 'Claribel Dervla'
    """
    try:
        import torch
        from TTS.api import TTS
    except ImportError:
        logger.error(
            "\n[ERROR] coqui-tts is not installed. Run:\n"
            "    pip install coqui-tts\n"
        )
        sys.exit(1)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Device       : {device.upper()}")
    logger.info("Loading Coqui TTS XTTS v2...")
    logger.info("(First run downloads ~1.9 GB — subsequent runs use local cache)")

    tts = TTS(MODEL_ID).to(device)

    use_wav = os.path.isfile(SPEAKER_WAV)
    if use_wav:
        logger.info(f"Voice mode   : Zero-shot cloning → {SPEAKER_WAV}")
    else:
        logger.warning(
            f"Speaker WAV not found: {SPEAKER_WAV}\n"
            f"  Using built-in female speaker: '{BUILTIN_FEMALE_SPEAKER}'"
        )
    logger.info("Model ready!")
    return tts, use_wav


def synthesize(tts, use_wav: bool, text: str, out: Path, retry: int = 0) -> bool:
    """Synthesize Tamil text with female voice and save to WAV. Retries up to 3x."""
    try:
        if use_wav:
            tts.tts_to_file(
                text=text,
                speaker_wav=SPEAKER_WAV,
                language=LANGUAGE,
                file_path=str(out),
            )
        else:
            tts.tts_to_file(
                text=text,
                speaker=BUILTIN_FEMALE_SPEAKER,
                language=LANGUAGE,
                file_path=str(out),
            )
        return True
    except Exception as e:
        if retry < 3:
            wait = 5 * (retry + 1)
            logger.warning(f"Retry {retry+1}/3 after {wait}s: {e}")
            time.sleep(wait)
            return synthesize(tts, use_wav, text, out, retry + 1)
        logger.error(f"Failed after 3 retries: {e}")
        return False


def main():
    setup_logging()

    logger.info("Loading Bible JSON...")
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        verses = json.load(f)
    total = len(verses)

    logger.info(f"")
    logger.info(f"{'='*60}")
    logger.info(f"  Tamil Bible TTS — Full Generation ({total:,} Verses)")
    logger.info(f"  Engine  : Coqui TTS XTTS v2")
    logger.info(f"  Model   : {MODEL_ID}")
    logger.info(f"  Voice   : Female (WAV cloning or built-in 'Claribel Dervla')")
    logger.info(f"  Speaker : {SPEAKER_WAV}")
    logger.info(f"  Language: Tamil (ta)")
    logger.info(f"  Output  : {OUTPUT_DIR}")
    logger.info(f"  Cost    : $0.00")
    logger.info(f"{'='*60}")
    logger.info(f"")

    stats = {
        "total": total, "generated": 0, "skipped": 0, "errors": 0,
        "start_time": datetime.now().isoformat(),
        "engine": "Coqui XTTS v2", "language": "ta", "voice": "female",
    }

    # Resume: load previous manifest if exists
    if os.path.exists(MANIFEST_FILE):
        try:
            with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
                old = json.load(f)
            stats["generated"] = old.get("generated", 0)
            stats["skipped"]   = old.get("skipped", 0)
            logger.info(f"Resuming — already done: {stats['generated']:,} verses")
        except Exception:
            pass

    tts, use_wav = load_tts()
    start_time   = time.time()

    with tqdm(total=total, desc="Generating", unit="verse",
              dynamic_ncols=True, colour="green") as pbar:

        for i, verse in enumerate(verses):
            book    = verse.get("book", "Unknown")
            chapter = int(verse.get("chapter", 1))
            vnum    = int(verse.get("verse", 1))
            text    = clean(verse.get("text", ""))

            out_path = get_output_path(book, chapter, vnum)

            # Skip already-generated files
            if file_ok(out_path):
                stats["skipped"] += 1
                pbar.update(1)
                continue

            if not text:
                stats["errors"] += 1
                pbar.update(1)
                continue

            success = synthesize(tts, use_wav, text, out_path)

            if success:
                stats["generated"] += 1
            else:
                stats["errors"] += 1

            pbar.update(1)

            # ETA display
            elapsed   = time.time() - start_time
            processed = stats["generated"] + stats["errors"]
            if processed > 0:
                remaining  = (total - i - 1) / (processed / elapsed)
                abbrev_disp = BOOK_ABBREV.get(book, "Bk")
                pbar.set_postfix({
                    "book": abbrev_disp,
                    "done": stats["generated"],
                    "skip": stats["skipped"],
                    "ETA":  str(timedelta(seconds=int(remaining))),
                })

            # Save manifest every 200 verses
            if (i + 1) % 200 == 0:
                save_manifest(stats)

    stats["end_time"]           = datetime.now().isoformat()
    stats["total_time_seconds"] = int(time.time() - start_time)
    save_manifest(stats)

    logger.info(f"")
    logger.info(f"{'='*60}")
    logger.info(f"  GENERATION COMPLETE!")
    logger.info(f"  Generated : {stats['generated']:,}")
    logger.info(f"  Skipped   : {stats['skipped']:,} (already existed)")
    logger.info(f"  Errors    : {stats['errors']:,}")
    logger.info(f"  Time      : {timedelta(seconds=stats['total_time_seconds'])}")
    logger.info(f"  Output    : {OUTPUT_DIR}")
    logger.info(f"{'='*60}")


if __name__ == "__main__":
    main()
