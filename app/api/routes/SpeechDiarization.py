from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import json
import os
import uuid
from app.core.Diarization import stream_diarization

diarization_router = APIRouter(tags=["Speech"])

@diarization_router.post("/diarization")
async def diarize_audio(file: UploadFile = File(...)):
    """
    Upload a WAV audio file and get diarization results with transcripts.
    Only accepts .wav files.
    """
    if not file.filename.lower().endswith('.wav'):
        raise HTTPException(
            status_code=400,
            detail="Only .wav files are accepted. Please upload a WAV audio file."
        )
    
    if file.content_type and not file.content_type.startswith('audio/'):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid content type: {file.content_type}. Expected audio file."
        )
    
    temp_filename = f"temp_{uuid.uuid4()}.wav"
    os.makedirs("temp", exist_ok=True)
    temp_path = os.path.join("temp", temp_filename)

    try:
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        def event_stream():
            try:
                for item in stream_diarization(temp_path):
                    yield json.dumps(item) + "\n"
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        return StreamingResponse(event_stream(), media_type="text/event-stream")
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise
