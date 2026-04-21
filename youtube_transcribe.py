"""
youtube_transcribe.py — transcribe YouTube videos for the research pipeline.

Called by agent.fetch_url_content() when a YouTube URL is detected.
Downloads audio with yt-dlp + ffmpeg, transcribes with openai-whisper, returns plain text.

Environment:
    WHISPER_MODEL   model size (default: base)
                    Options: tiny, base, small, medium, large, turbo
                    turbo = large-v3 distilled, fast and accurate but English-only for translation
    WHISPER_DEVICE  cpu | cuda (default: cpu — avoids competing with vLLM for VRAM)

Install:
    pip install -U openai-whisper yt-dlp
    # ffmpeg must be on PATH (apt/brew/choco install ffmpeg)
"""

from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path

WHISPER_MODEL  = os.environ.get("WHISPER_MODEL", "base")
WHISPER_DEVICE = os.environ.get("WHISPER_DEVICE", "cpu")

_YT_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.)?(?:youtube\.com/(?:watch\?.*v=|shorts/)|youtu\.be/)[\w\-]+"
)


def is_youtube_url(url: str) -> bool:
    return bool(_YT_PATTERN.match(url))


def transcribe_youtube(url: str) -> str:
    """
    Download audio from a YouTube URL and return a transcript.
    Returns empty string on any failure (pipeline continues without it).
    """
    try:
        import whisper
    except ImportError:
        print("  [youtube] openai-whisper not installed — skipping (pip install -U openai-whisper)")
        return ""

    with tempfile.TemporaryDirectory() as tmp_dir:
        audio_path = Path(tmp_dir) / "audio"

        # Download audio only via yt-dlp; ffmpeg converts to wav
        print(f"  [youtube] downloading audio: {url[:70]}...")
        dl = subprocess.run(
            [
                "yt-dlp",
                "-x", "--audio-format", "wav",
                "--audio-quality", "0",
                "--no-playlist",
                "--extractor-args", "youtube:player_client=android",
                "-o", str(audio_path),
            ] + [url],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if dl.returncode != 0:
            print(f"  [youtube] yt-dlp failed: {dl.stderr[:200]}")
            return ""

        candidates = list(Path(tmp_dir).glob("audio*"))
        if not candidates:
            print("  [youtube] no audio file produced by yt-dlp")
            return ""
        audio_file = str(candidates[0])

        # Transcribe
        print(f"  [youtube] transcribing with whisper/{WHISPER_MODEL} on {WHISPER_DEVICE}...")
        model = whisper.load_model(WHISPER_MODEL, device=WHISPER_DEVICE)
        result = model.transcribe(audio_file)
        transcript = (result.get("text") or "").strip()

        if not transcript:
            print("  [youtube] transcript empty")
            return ""

        lang = result.get("language", "?")
        print(f"  [youtube] language={lang}  {len(transcript)} chars")
        return f"[YouTube transcript — {url}]\n\n{transcript}"
