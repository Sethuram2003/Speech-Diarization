# app/core/Diarization.py
import os
import re
import importlib
import threading
from typing import Any, Optional, List

from pydub import AudioSegment
from dotenv import load_dotenv

import torch
from torch.serialization import add_safe_globals
from torch.serialization import safe_globals  # context manager, if needed

load_dotenv()

# HF token (ensure HF token is in your .env as HF_TOKEN or change name)
HF_TOKEN = os.getenv("hf_token") or os.getenv("HF_TOKEN")

# model id you use
MODEL_ID = "pyannote/speaker-diarization-3.1"

# internal singleton state
_pipeline = None
_pipeline_lock = threading.Lock()

# regex to extract unsupported global class name from error message
_RE_GLOBAL = re.compile(r"Unsupported global: GLOBAL ([\w\.]+) was not an allowed global")

def _resolve_global(name: str) -> Optional[Any]:
    """
    Given a dotted name like "pyannote.audio.core.task.Specifications",
    import the module and return the attribute (class/object). Returns None if not resolvable.
    """
    try:
        module_path, attr = name.rsplit(".", 1)
    except ValueError:
        return None

    try:
        module = importlib.import_module(module_path)
    except Exception:
        return None

    return getattr(module, attr, None)


def _allowlist_globals(names: List[str]):
    """
    Convert dotted names to objects and add them to torch safe globals.
    Ignores names that can't be resolved.
    """
    objs = []
    for name in names:
        obj = _resolve_global(name)
        if obj is not None:
            objs.append(obj)
    if objs:
        add_safe_globals(objs)
        return True
    return False


def _attempt_load_pipeline(max_retries: int = 8):
    """
    Try to load the pyannote pipeline. On UnpicklingError, parse the missing
    global(s) from the exception message, add them to safe globals and retry.
    Returns the loaded Pipeline on success or raises the last exception.
    """
    from pyannote.audio import Pipeline  # import here so it's after add_safe_globals when needed

    last_exc = None
    tried_names = set()

    for attempt in range(max_retries):
        try:
            pipeline = Pipeline.from_pretrained(MODEL_ID, token=HF_TOKEN)
            return pipeline
        except Exception as exc:
            last_exc = exc
            msg = str(exc)
            # find all missing global names in the message
            matches = _RE_GLOBAL.findall(msg)
            # sometimes the message may include multiple different lines; de-duplicate
            new_names = [m for m in matches if m not in tried_names]
            if not new_names:
                # nothing parsed -> re-raise
                break

            # try to resolve objects and add them to safe globals
            resolved = []
            for name in new_names:
                obj = _resolve_global(name)
                if obj is not None:
                    resolved.append(obj)
                    tried_names.add(name)

            if not resolved:
                # we couldn't resolve any of the parsed names -> break
                break

            # add to safe globals and retry
            add_safe_globals(resolved)
            continue

    # If we exit the loop without returning, re-raise the last exception
    raise last_exc


def get_pipeline():
    """
    Thread-safe lazy loader for the pyannote pipeline.
    On first call this loads the pipeline (with auto-allowlist retry).
    Subsequent calls return the cached pipeline.
    """
    global _pipeline
    if _pipeline is not None:
        return _pipeline

    with _pipeline_lock:
        if _pipeline is not None:
            return _pipeline

        # Attempt to load pipeline with retries and auto allowlisting
        _pipeline = _attempt_load_pipeline()
        return _pipeline


# -------------------- diarization streaming generator --------------------
from app.core.Transcription import transcribe  # import transcription func here


def stream_diarization(audio_path: str):
    """
    Generator that yields diarization + transcript items one by one.
    Uses lazy-loaded pipeline so importing this module does NOT load heavy models.
    """
    pipeline = get_pipeline()
    diarization = pipeline(audio_path)
    annotation = diarization.speaker_diarization

    merged_segments = []
    current_speaker = None
    current_start = None
    current_end = None

    for segment, _, speaker in annotation.itertracks(yield_label=True):
        start, end = segment.start, segment.end
        if speaker != current_speaker:
            if current_speaker is not None:
                merged_segments.append((current_start, current_end, current_speaker))
            current_speaker = speaker
            current_start = start
            current_end = end
        else:
            current_end = end

    if current_speaker is not None:
        merged_segments.append((current_start, current_end, current_speaker))

    audio = AudioSegment.from_wav(audio_path)
    os.makedirs("splits", exist_ok=True)

    for i, (start, end, speaker) in enumerate(merged_segments):
        start_ms = int(start * 1000)
        end_ms = int(end * 1000)

        split_path = f"splits/segment_{i+1}.wav"
        audio[start_ms:end_ms].export(split_path, format="wav")

        transcript = transcribe(split_path)

        yield {
            "segment_number": i + 1,
            "speaker": speaker,
            "start": start,
            "end": end,
            "transcript": transcript,
            "file_path": split_path,
        }


# for manual debugging (keeps behavior you used before)
if __name__ == "__main__":
    for item in stream_diarization("audio.wav"):
        print(item)
