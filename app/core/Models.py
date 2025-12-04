import os
from dotenv import load_dotenv
from transformers import AudioFlamingo3ForConditionalGeneration, AutoProcessor
from pyannote.audio import Pipeline

load_dotenv()

class ModelStore:
    diarization_pipeline = None
    flamingo_model = None
    flamingo_processor = None

model_store = ModelStore()

async def load_models():
    """Load all heavy ML models once at FastAPI startup."""
    print("🔄 Loading diarization & transcription models...")

    model_store.diarization_pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        token=os.getenv("hf_token"),
    )

    model_id = "nvidia/audio-flamingo-3-hf"
    model_store.flamingo_processor = AutoProcessor.from_pretrained(model_id)
    model_store.flamingo_model = AudioFlamingo3ForConditionalGeneration.from_pretrained(
        model_id,
        device_map="cpu",
    )

    print("✅ All models loaded successfully.")
