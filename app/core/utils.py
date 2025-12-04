from dotenv import load_dotenv
import os
import re
import importlib
import threading
from typing import Any, Optional
from torch.serialization import add_safe_globals

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

            print(resolved)
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


