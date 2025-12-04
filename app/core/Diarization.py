import os
from pydub import AudioSegment
from dotenv import load_dotenv
from pyannote.audio import Pipeline
from app.core.Transcription import transcribe

load_dotenv()

# ------------------- LOAD DIARIZATION MODEL -------------------
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    token=os.getenv("hf_token"),
)

audio_path = "audio.wav"

diarization = pipeline(audio_path)
annotation = diarization.speaker_diarization

# ------------------- MERGE SPEAKER SEGMENTS -------------------
merged_segments = []
current_speaker = None
current_start = None
current_end = None

for segment, _, speaker in annotation.itertracks(yield_label=True):
    start = segment.start
    end = segment.end

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


# ------------------- LOAD AUDIO FOR SPLITTING -------------------
audio = AudioSegment.from_wav(audio_path)
os.makedirs("splits", exist_ok=True)

# ------------------- SPLIT + TRANSCRIBE EACH SEGMENT -------------------
print("\n===== FINAL OUTPUT =====\n")

for i, (start, end, speaker) in enumerate(merged_segments):
    start_ms = int(start * 1000)
    end_ms = int(end * 1000)

    split_path = f"splits/segment_{i+1}.wav"

    # Export the audio chunk
    audio[start_ms:end_ms].export(split_path, format="wav")

    # Transcribe the audio chunk
    transcript = transcribe(split_path)

    print(f"Segment {i+1} | {speaker}")
    print(f"Time: {start:.2f}s → {end:.2f}s")
    print(f"Transcript: {transcript}")
    print("-" * 50)