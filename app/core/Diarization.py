import os
from pydub import AudioSegment
from dotenv import load_dotenv

import torch
from torch.serialization import add_safe_globals
import torch.torch_version

add_safe_globals([torch.torch_version.TorchVersion])

from pyannote.audio import Pipeline
from app.core.Transcription import transcribe

load_dotenv()

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    token=os.getenv("hf_token"),
)

def stream_diarization(audio_path: str):
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

if __name__ == "__main__":
    for item in stream_diarization(audio_path="audio.wav"):
        print(item)

