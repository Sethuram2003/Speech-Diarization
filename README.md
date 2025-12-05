# Speech Diarization API

A FastAPI-based service that performs speaker diarization and transcription on audio files. The API identifies different speakers in an audio recording, segments the audio by speaker, and transcribes each segment using state-of-the-art AI models.

## Features

- **Speaker Diarization**: Automatically identifies and separates different speakers in audio files
- **Speech Transcription**: Transcribes each speaker segment using NVIDIA's Audio Flamingo model
- **Streaming Response**: Returns results as they're processed via Server-Sent Events (SSE)
- **Docker Support**: Fully containerized application for easy deployment
- **WAV File Support**: Accepts WAV audio files for processing

## Technology Stack

- **FastAPI**: Modern, high-performance web framework
- **PyAnnote Audio**: Speaker diarization pipeline (v3.1)
- **NVIDIA Audio Flamingo**: Advanced audio transcription model
- **Docker**: Containerization for consistent deployment
- **Python 3.12**: Latest Python runtime

## Project Structure

```
.
├── app/
│   ├── main.py                          # FastAPI application entry point
│   ├── api/
│   │   └── routes/
│   │       ├── HealthCheck.py           # Health check endpoint
│   │       └── SpeechDiarization.py     # Main diarization endpoint
│   └── core/
│       ├── AudioExtraction.py           # YouTube audio download utility
│       ├── Diarization.py               # Speaker diarization logic
│       ├── Models.py                    # ML model loading and management
│       └── Transcription.py             # Audio transcription logic
├── splits/                              # Output directory for audio segments
├── temp/                                # Temporary file storage
├── Dockerfile                           # Docker container configuration
├── compose.yaml                         # Docker Compose configuration
├── requirements.txt                     # Python dependencies
└── .env                                 # Environment variables (not in git)
```

## Prerequisites

- **Docker Desktop**: Required for running the application
  - [Download Docker for Mac](https://docs.docker.com/desktop/install/mac-install/)
- **Hugging Face Account**: Required for model access
- **8GB+ RAM**: Recommended for model loading

## Getting Started

### 1. Hugging Face Setup

The application uses models from Hugging Face that require authentication and acceptance of terms.

#### Step 1: Create a Hugging Face Account
1. Go to [huggingface.co](https://huggingface.co) and sign up for a free account
2. Verify your email address

#### Step 2: Accept Model Terms
You must accept the terms for the following models:

1. **Speaker Diarization Model**:
   - Visit: [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)
   - Click "Agree and access repository"

2. **Speaker Diarization Pipeline**:
   - Visit: [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
   - Click "Agree and access repository"

#### Step 3: Generate Access Token
1. Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Click "New token"
3. Give it a name (e.g., "speech-diarization-api")
4. Select "Read" permission
5. Click "Generate token"
6. **Copy the token** (it starts with `hf_...`)

### 2. Environment Configuration

Create a `.env` file in the project root:

```bash
cp .env.sample .env
```

Edit `.env` and add your Hugging Face token:

```env
hf_token="hf_YOUR_TOKEN_HERE"
```

**Important**: Replace `hf_YOUR_TOKEN_HERE` with your actual token from Step 3 above.

### 3. Running the Application

The application **must** be run using Docker on Mac:

```bash
docker compose up --build
```

This command will:
- Build the Docker image with all dependencies
- Install FFmpeg and required system libraries
- Download and cache the ML models (first run takes longer)
- Start the FastAPI server on port 8000

**First Run Note**: The initial startup takes 5-10 minutes as it downloads large ML models (~2GB). Subsequent runs are much faster due to Docker volume caching.

### 4. Verify the Service

Once running, you should see:
```
✅ All models loaded successfully.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Test the health endpoint:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"message": "Service is up and running"}
```

## API Documentation

### Interactive API Docs

Once the service is running, access the interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints

#### 1. Health Check
```http
GET /health
```

Returns service status.

**Response**:
```json
{
  "message": "Service is up and running"
}
```

#### 2. Audio Diarization
```http
POST /diarization
Content-Type: multipart/form-data
```

Upload a WAV audio file for speaker diarization and transcription.

**Parameters**:
- `file` (required): WAV audio file

**Response**: Server-Sent Events (SSE) stream with JSON objects

Each segment returns:
```json
{
  "segment_number": 1,
  "speaker": "SPEAKER_00",
  "start": 0.33471875,
  "end": 4.95846875,
  "transcript": "amy it says you are trained in technology that's very good are you adept at excel",
  "file_path": "splits/segment_1.wav"
}
```

### Example Usage

#### Using cURL
```bash
curl -X POST "http://localhost:8000/diarization" \
  -H "accept: text/event-stream" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@audio.wav"
```

#### Using Python
```python
import requests

url = "http://localhost:8000/diarization"
files = {"file": open("audio.wav", "rb")}

response = requests.post(url, files=files, stream=True)

for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

#### Using JavaScript/Fetch
```javascript
const formData = new FormData();
formData.append('file', audioFile);

const response = await fetch('http://localhost:8000/diarization', {
  method: 'POST',
  body: formData
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  const lines = chunk.split('\n').filter(line => line.trim());
  
  lines.forEach(line => {
    const data = JSON.parse(line);
    console.log(data);
  });
}
```

## Example Output

An example audio file (`audio.wav`) is included in the repository. When processed, it produces output like:

```json
{"segment_number": 1, "speaker": "SPEAKER_00", "start": 0.33471875, "end": 4.95846875, "transcript": "amy it says you are trained in technology that's very good are you adept at excel", "file_path": "splits/segment_1.wav"}
{"segment_number": 2, "speaker": "SPEAKER_01", "start": 6.00471875, "end": 6.494093750000001, "transcript": "no", "file_path": "splits/segment_2.wav"}
{"segment_number": 3, "speaker": "SPEAKER_00", "start": 7.27034375, "end": 7.87784375, "transcript": "powerpoint", "file_path": "splits/segment_3.wav"}
```

The audio segments are saved in the `splits/` directory for further processing or review.

## How It Works

### 1. Model Loading (Startup)
- **Diarization Pipeline**: PyAnnote's speaker-diarization-3.1 model identifies speakers
- **Transcription Model**: NVIDIA's Audio Flamingo-3 model transcribes speech

### 2. Processing Flow
1. User uploads WAV file via `/diarization` endpoint
2. File is temporarily saved to `temp/` directory
3. Diarization pipeline identifies speaker segments
4. Consecutive segments from the same speaker are merged
5. Each segment is:
   - Extracted and saved to `splits/` directory
   - Transcribed using Audio Flamingo model
   - Streamed back to client as JSON
6. Temporary files are cleaned up

### 3. Speaker Identification
- Speakers are labeled as `SPEAKER_00`, `SPEAKER_01`, etc.
- The model doesn't identify who the speakers are, only that they're different people
- Timestamps are provided in seconds from the start of the audio

## Docker Configuration

### Dockerfile Highlights
- **Base Image**: Python 3.12 slim (linux/amd64 for compatibility)
- **System Dependencies**: FFmpeg, git, libsndfile1
- **User**: Non-root user (appuser) for security
- **Caching**: Hugging Face models cached in Docker volume
- **Port**: Exposes port 8000

### Docker Compose
- **Service Name**: speech-diarization-api
- **Port Mapping**: 8000:8000
- **Volume**: Persistent cache for Hugging Face models
- **Platform**: Configured for ARM64 (Apple Silicon)

### Stopping the Service
```bash
docker compose down
```

### Viewing Logs
```bash
docker compose logs -f
```

### Rebuilding After Changes
```bash
docker compose up --build
```

## Troubleshooting

### Models Not Loading
- Ensure you've accepted terms for both PyAnnote models on Hugging Face
- Verify your `hf_token` in `.env` is correct and has "Read" permissions
- Check Docker logs: `docker compose logs -f`

### Out of Memory Errors
- The models require significant RAM (6-8GB recommended)
- Close other applications to free up memory
- Consider using a machine with more RAM

### Port Already in Use
If port 8000 is already in use, modify `compose.yaml`:
```yaml
ports:
  - "8080:8000"  # Use port 8080 instead
```

### Slow First Startup
- First run downloads ~2GB of models
- Subsequent runs use cached models from Docker volume
- Be patient during initial model download

### Audio File Errors
- Only WAV files are supported
- Ensure audio is not corrupted
- Try converting your audio to WAV format first

## Production Considerations

### PyAnnote AI
For production use, consider [PyAnnote AI](https://www.pyannote.ai/) which offers:
- Faster inference times
- Better accuracy
- Commercial support
- Managed infrastructure

### Performance Optimization
- Use GPU-enabled Docker images for faster processing
- Implement request queuing for concurrent requests
- Add Redis for caching results
- Use cloud storage for audio segments

### Security
- Add authentication/authorization
- Implement rate limiting
- Validate file sizes and types
- Use HTTPS in production
- Rotate Hugging Face tokens regularly

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Credits

- **PyAnnote Audio**: Speaker diarization models
- **NVIDIA**: Audio Flamingo transcription model
- **Hugging Face**: Model hosting and transformers library

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Docker logs: `docker compose logs -f`
3. Ensure all prerequisites are met
4. Verify Hugging Face token and model access

---

**Note**: This application is designed for development and testing. For production deployment, consider the recommendations in the "Production Considerations" section.
