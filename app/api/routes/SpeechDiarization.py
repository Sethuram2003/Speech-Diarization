from fastapi import FastAPI, APIRouter
from fastapi.responses import StreamingResponse
import json
from app.core.Diarization import stream_diarization

diarization_router = APIRouter(tags=["Speech"])

app = FastAPI()

@diarization_router.post("/diarization")
def diarize_audio(path:str):
    def event_stream():
        for item in stream_diarization(path):
            yield json.dumps(item) + "\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")
