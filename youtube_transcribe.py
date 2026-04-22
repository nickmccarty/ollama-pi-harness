"""
youtube_transcribe.py — transcribe YouTube videos and direct media URLs.

YouTube watch URLs:
  1. youtube-transcript-api (no audio download, uses auto-captions)
  2. Fallback: pytubefix → openai-whisper

Direct media URLs (mp4, mp3, wav, webm, etc.):
  ffmpeg extracts audio → openai-whisper transcribes

Environment:
    WHISPER_MODEL   model size (default: base) — tiny|base|small|medium|large|turbo
    WHISPER_DEVICE  cpu | cuda (default: cpu)

Install:
    pip install -U openai-whisper pytubefix youtube-transcript-api imageio-ffmpeg
    # imageio-ffmpeg ships its own ffmpeg binary; no system install needed
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
_MEDIA_EXTENSIONS = {".mp4", ".mp3", ".wav", ".webm", ".ogg", ".m4a", ".mkv", ".flv", ".avi"}


def is_youtube_url(url: str) -> bool:
    return bool(_YT_PATTERN.match(url))


def is_media_url(url: str) -> bool:
    return Path(url.split("?")[0]).suffix.lower() in _MEDIA_EXTENSIONS


def _get_ffmpeg() -> str:
    """Return path to ffmpeg binary — system install or imageio_ffmpeg fallback."""
    import shutil
    sys_ffmpeg = shutil.which("ffmpeg")
    if sys_ffmpeg:
        return sys_ffmpeg
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"  # will surface a clear error if missing


def _ensure_ffmpeg() -> None:
    """Inject imageio_ffmpeg binary dir into PATH so whisper's subprocess finds it."""
    import shutil
    if shutil.which("ffmpeg"):
        return
    try:
        import imageio_ffmpeg
        ffmpeg_dir = os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
    except ImportError:
        pass


def _extract_video_id(url: str) -> str | None:
    m = re.search(r"(?:v=|youtu\.be/|shorts/)([\w\-]+)", url)
    return m.group(1) if m else None


def _whisper_transcribe(audio_path: str) -> str:
    try:
        import whisper
    except ImportError:
        print("  [transcribe] openai-whisper not installed (pip install openai-whisper)")
        return ""

    # Pre-convert to 16kHz mono wav using the known ffmpeg binary so whisper
    # never needs to find ffmpeg itself via PATH.
    ffmpeg = _get_ffmpeg()
    wav_path = audio_path + ".wav"
    try:
        subprocess.run(
            [ffmpeg, "-y", "-i", audio_path, "-ar", "16000", "-ac", "1", "-f", "wav", wav_path],
            check=True, capture_output=True,
        )
    except Exception as e:
        print(f"  [transcribe] ffmpeg pre-convert failed: {e}")
        wav_path = audio_path  # fall back; whisper will try on its own

    print(f"  [transcribe] whisper/{WHISPER_MODEL} on {WHISPER_DEVICE}...")
    try:
        model = whisper.load_model(WHISPER_MODEL, device=WHISPER_DEVICE)
        result = model.transcribe(wav_path)
    except Exception as e:
        print(f"  [transcribe] failed: {e}")
        return ""
    finally:
        if wav_path != audio_path and os.path.exists(wav_path):
            os.unlink(wav_path)

    text = (result.get("text") or "").strip()
    if text:
        lang = result.get("language", "?")
        print(f"  [transcribe] language={lang}  {len(text)} chars")
    return text


def _ffmpeg_extract_audio(media_url: str, out_path: str) -> bool:
    """Download/convert a direct media URL to wav via ffmpeg. Returns True on success."""
    result = subprocess.run(
        [_get_ffmpeg(), "-i", media_url, "-ar", "16000", "-ac", "1", "-vn", out_path, "-y"],
        capture_output=True,
        timeout=300,
    )
    return result.returncode == 0 and Path(out_path).exists()


def transcribe_youtube(url: str) -> str:
    """
    Transcribe a YouTube watch URL.
    Strategy B (transcript API) → fallback A (pytubefix + whisper).
    """
    video_id = _extract_video_id(url)

    # B: youtube-transcript-api — no audio download, uses auto-captions
    if video_id:
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            print(f"  [youtube] fetching auto-captions for {video_id}...")
            entries = YouTubeTranscriptApi.get_transcript(video_id)
            text = " ".join(e["text"] for e in entries).strip()
            if text:
                print(f"  [youtube] captions: {len(text)} chars")
                return f"[YouTube transcript — {url}]\n\n{text}"
        except Exception as e:
            print(f"  [youtube] transcript API failed ({e}), falling back to audio...")

    # A fallback: pytubefix downloads audio stream → whisper
    try:
        from pytubefix import YouTube
    except ImportError:
        print("  [youtube] pytubefix not installed (pip install pytubefix)")
        return ""

    with tempfile.TemporaryDirectory() as tmp_dir:
        try:
            print(f"  [youtube] fetching audio stream: {url[:70]}...")
            yt = YouTube(url)
            stream = yt.streams.filter(only_audio=True).order_by("abr").last()
            if not stream:
                print("  [youtube] no audio stream found")
                return ""
            audio_file = stream.download(output_path=tmp_dir, filename="audio")
        except Exception as e:
            print(f"  [youtube] stream fetch failed: {e}")
            return ""

        text = _whisper_transcribe(audio_file)
        if not text:
            return ""
        return f"[YouTube transcript — {url}]\n\n{text}"


def transcribe_media_url(url: str) -> str:
    """
    Transcribe a direct media URL (mp4, mp3, etc.) via ffmpeg + whisper.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_path = str(Path(tmp_dir) / "audio.wav")
        print(f"  [media] extracting audio: {url[:70]}...")
        if not _ffmpeg_extract_audio(url, out_path):
            print("  [media] ffmpeg failed")
            return ""
        text = _whisper_transcribe(out_path)
        if not text:
            return ""
        return f"[Media transcript — {url}]\n\n{text}"
