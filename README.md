# Tamil Bible Verse-to-Voice Generation System

A Python-based Text-to-Speech pipeline for converting Tamil Bible verses into individually organized audio files using multilingual TTS models.

## Overview

This project converts a structured Tamil Bible dataset into speech at the individual verse level. It was developed to automate large-scale Tamil text-to-speech generation while maintaining organized book, chapter, and verse-based audio outputs.

The project includes both a **gTTS-based implementation** and a **local Coqui XTTS v2 implementation**.

## Key Features

* Tamil text-to-speech generation
* Tamil Unicode text normalization and cleaning
* Support for approximately **31,102 verses**
* gTTS-based Tamil MP3 generation
* Local Coqui XTTS v2-based WAV generation
* Female voice support
* Optional speaker-reference voice input with XTTS v2
* Automatic CPU/GPU selection
* Book and chapter filtering
* Test mode for sample verse generation
* Automatic skipping of already-generated audio
* Resume-friendly batch processing
* Retry handling for failed generations
* Generation progress tracking and logging
* Book/chapter/verse-based output organization

## System Workflow

```text
Tamil Bible JSON
       ↓
Verse Extraction
       ↓
Tamil Text Normalization
       ↓
TTS Engine
   ↙          ↘
gTTS       Coqui XTTS v2
   ↓            ↓
MP3          WAV
       ↓
Book / Chapter / Verse Organization
       ↓
Generation Logs / Manifest
```

## Technologies

* Python
* Coqui TTS / XTTS v2
* gTTS
* PyTorch
* tqdm
* JSON
* Unicode text processing

## TTS Approaches

### 1. gTTS

The project includes a gTTS-based implementation for Tamil speech generation.

It can be used for generating sample or batch MP3 audio from Tamil Bible verses.

### 2. Coqui XTTS v2

The project also includes a local implementation using:

`tts_models/multilingual/multi-dataset/xtts_v2`

The implementation automatically selects CUDA when available and falls back to CPU otherwise.

XTTS v2 also supports an optional speaker-reference WAV for voice characteristics.

## Input

The system expects a structured JSON file containing Bible verse information such as:

```text
Book
Chapter
Verse
Text
```

The dataset itself is **not included in this repository**.

Users should provide a legally obtained dataset that they have permission to process and redistribute as applicable.

## Output

Generated audio is organized using book, chapter, and verse identifiers.

Example:

```text
Gen_001_001.wav
```

represents the corresponding book, chapter, and verse.

Generated audio files are not included in the repository to avoid unnecessarily large repository size and potential redistribution/licensing issues.

## Text Processing

Before synthesis, Tamil text is normalized and cleaned using Unicode normalization and whitespace/control-character handling.

This helps provide cleaner and more consistent input to the TTS engine.

## Batch Processing

The project is designed for large-scale verse processing rather than only single-text conversion.

The generation pipeline can:

* Process verses sequentially
* Skip existing output files
* Retry failed synthesis
* Track generated/skipped/failed items
* Save generation information for monitoring and resuming

## Sample / Test Mode

A small number of verses can be generated first to verify:

* Tamil pronunciation
* Voice quality
* Output format
* File organization
* Model configuration

This avoids starting a full-generation run before validating the configuration.

## Project Structure

```text
tamil-bible-tts/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── src/
│   ├── generate_tts.py
│   ├── generate_tts_local.py
│   ├── generate_full_gtts.py
│   ├── run_sample_10.py
│   └── sample_10_verses.py
│
└── docs/
    └── screenshots/
```

## Project Highlights

* Large-scale Tamil speech generation
* Multilingual TTS model integration
* Local AI inference
* Tamil Unicode preprocessing
* Batch automation
* Resume-friendly processing
* Error handling and retry logic
* Structured audio organization

## Future Improvements

* Web-based interface for selecting books and chapters
* Integrated audio player
* Additional Tamil voice options
* Searchable verse index
* Chapter-level audio generation
* Audio metadata
* Speech-quality evaluation
* Mobile application integration

## Important Note

This repository contains the **software implementation** for the TTS pipeline. The Bible dataset and generated audio files are intentionally excluded from the repository.

Users are responsible for ensuring that any text, audio, speaker-reference recordings, and other resources they use comply with the applicable copyright, licensing, privacy, and redistribution requirements.
