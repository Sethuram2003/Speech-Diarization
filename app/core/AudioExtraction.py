import os

from yt_dlp import YoutubeDL
from pydub import AudioSegment

def download_youtube_audio_as_wav(youtube_url: str, output_path: str = "audio.wav"):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'temp_audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)
        temp_file = ydl.prepare_filename(info).rsplit('.', 1)[0] + ".mp3"

    wav_file = output_path
    audio = AudioSegment.from_file(temp_file, format="mp3")
    audio.export(wav_file, format="wav")

    try:
        os.remove(temp_file)
    except OSError:
        pass

    print(f"Saved WAV audio to: {wav_file}")
    return wav_file

if __name__ == "__main__":
    url = input("Enter the YouTube URL: ").strip()
    download_youtube_audio_as_wav(url, output_path="audio.wav")