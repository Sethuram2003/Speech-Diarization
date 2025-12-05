<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h3 align="center">Speech Diarization API</h3>

  <p align="center">
    A powerful FastAPI service for speaker diarization and transcription using state-of-the-art AI models
    <br />
    <a href="#usage"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="#usage">View Demo</a>
    ·
    <a href="https://github.com/Sethuram2003/Speech-Diarization/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/Sethuram2003/Speech-Diarization/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
        <li><a href="#features">Features</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#api-documentation">API Documentation</a></li>
    <li><a href="#example-output">Example Output</a></li>
    <li><a href="#how-it-works">How It Works</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

Speech Diarization API is a production-ready FastAPI service that automatically identifies different speakers in audio recordings, segments the audio by speaker, and transcribes each segment using cutting-edge AI models from PyAnnote and NVIDIA.

This project solves the challenge of processing multi-speaker audio files by:
* Automatically detecting and separating different speakers in conversations
* Providing accurate timestamps for each speaker segment
* Transcribing speech to text using NVIDIA's Audio Flamingo model
* Streaming results in real-time for better user experience
* Running entirely in Docker for consistent deployment across environments

Perfect for transcription services, meeting analysis, podcast processing, interview analysis, and any application requiring speaker identification and transcription.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

* [![FastAPI][FastAPI-badge]][FastAPI-url]
* [![Python][Python-badge]][Python-url]
* [![Docker][Docker-badge]][Docker-url]
* [![PyTorch][PyTorch-badge]][PyTorch-url]
* [![HuggingFace][HuggingFace-badge]][HuggingFace-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Features

- **Speaker Diarization**: Automatically identifies and separates different speakers using PyAnnote Audio 3.1
- **Speech Transcription**: Transcribes each speaker segment using NVIDIA's Audio Flamingo-3 model
- **Streaming Response**: Returns results as they're processed via Server-Sent Events (SSE)
- **Docker Support**: Fully containerized application for easy deployment on Mac
- **WAV File Support**: Accepts WAV audio files for processing
- **Segment Export**: Saves individual speaker segments as separate audio files
- **RESTful API**: Clean, well-documented API endpoints with interactive Swagger UI

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

Follow these steps to get the Speech Diarization API running on your Mac using Docker.

### Prerequisites

Before you begin, ensure you have the following installed and configured:

* **Docker Desktop for Mac**
  ```sh
  # Download from: https://docs.docker.com/desktop/install/mac-install/
  # Or install via Homebrew:
  brew install --cask docker
  ```

* **Hugging Face Account** (Free)
  - Required for accessing AI models
  - Sign up at [huggingface.co](https://huggingface.co/join)

* **System Requirements**
  - macOS 10.15 or later
  - 8GB+ RAM recommended
  - 10GB free disk space for models and Docker images

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Installation

Follow these steps carefully to set up the project:

1. **Accept Hugging Face Model Terms**
   
   You must accept the terms for these models before they can be used:
   - Visit [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0) and click "Agree and access repository"
   - Visit [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1) and click "Agree and access repository"

2. **Generate Hugging Face Access Token**
   
   - Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
   - Click "New token"
   - Name: `speech-diarization-api`
   - Permission: Select "Read"
   - Click "Generate token"
   - **Copy the token** (starts with `hf_`)

3. **Clone the repository**
   ```sh
   git clone https://github.com/Sethuram2003/Speech-Diarization.git
   cd Speech-Diarization
   ```

4. **Configure environment variables**
   ```sh
   cp .env.sample .env
   ```

5. **Add your Hugging Face token to `.env`**
   ```env
   hf_token="hf_YOUR_TOKEN_HERE"
   ```
   Replace `hf_YOUR_TOKEN_HERE` with the token you copied in step 2.

6. **Build and start the Docker container**
   ```sh
   docker compose up --build
   ```

   **Note**: The first run takes 5-10 minutes as it downloads ~2GB of AI models. Subsequent runs are much faster due to Docker volume caching.

7. **Verify the service is running**
   
   Once you see `✅ All models loaded successfully`, test the health endpoint:
   ```sh
   curl http://localhost:8000/health
   ```
   
   Expected response:
   ```json
   {"message": "Service is up and running"}
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

The API provides a simple interface for processing audio files. Here are examples in different languages:

### Using cURL

```sh
curl -X POST "http://localhost:8000/diarization" \
  -H "accept: text/event-stream" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@audio.wav"
```

### Using Python

```python
import requests

url = "http://localhost:8000/diarization"
files = {"file": open("audio.wav", "rb")}

response = requests.post(url, files=files, stream=True)

for line in response.iter_lines():
    if line:
        data = line.decode('utf-8')
        print(data)
```

### Using JavaScript/Fetch

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

### Interactive API Documentation

Access the interactive Swagger UI for testing:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- API DOCUMENTATION -->
## API Documentation

### Endpoints

#### Health Check
```http
GET /health
```

Returns the service status.

**Response:**
```json
{
  "message": "Service is up and running"
}
```

#### Audio Diarization
```http
POST /diarization
Content-Type: multipart/form-data
```

Upload a WAV audio file for speaker diarization and transcription.

**Parameters:**
- `file` (required): WAV audio file

**Response:** Server-Sent Events (SSE) stream with JSON objects

**Response Format:**
```json
{
  "segment_number": 1,
  "speaker": "SPEAKER_00",
  "start": 0.33471875,
  "end": 4.95846875,
  "transcript": "transcribed text here",
  "file_path": "splits/segment_1.wav"
}
```

**Fields:**
- `segment_number`: Sequential segment identifier
- `speaker`: Speaker label (SPEAKER_00, SPEAKER_01, etc.)
- `start`: Start time in seconds
- `end`: End time in seconds
- `transcript`: Transcribed text for this segment
- `file_path`: Path to the extracted audio segment

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- EXAMPLE OUTPUT -->
## Example Output

An example audio file (`audio.wav`) is included in the repository. When processed, it produces output like this:

```json
{"segment_number": 1, "speaker": "SPEAKER_00", "start": 0.33471875, "end": 4.95846875, "transcript": "amy it says you are trained in technology that's very good are you adept at excel", "file_path": "splits/segment_1.wav"}
{"segment_number": 2, "speaker": "SPEAKER_01", "start": 6.00471875, "end": 6.494093750000001, "transcript": "no", "file_path": "splits/segment_2.wav"}
{"segment_number": 3, "speaker": "SPEAKER_00", "start": 7.27034375, "end": 7.87784375, "transcript": "powerpoint", "file_path": "splits/segment_3.wav"}
{"segment_number": 4, "speaker": "SPEAKER_01", "start": 8.181593750000001, "end": 8.72159375, "transcript": "noun", "file_path": "splits/segment_4.wav"}
{"segment_number": 5, "speaker": "SPEAKER_00", "start": 9.632843750000003, "end": 10.172843750000002, "transcript": "publisher", "file_path": "splits/segment_5.wav"}
```

The complete conversation contains 33 segments alternating between two speakers. Each segment is saved as a separate WAV file in the `splits/` directory.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- HOW IT WORKS -->
## How It Works

### Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ Upload WAV
       ▼
┌─────────────────────────────────┐
│      FastAPI Application        │
│  ┌───────────────────────────┐  │
│  │  /diarization endpoint    │  │
│  └───────────┬───────────────┘  │
│              ▼                   │
│  ┌───────────────────────────┐  │
│  │  PyAnnote Diarization     │  │
│  │  (Speaker Detection)      │  │
│  └───────────┬───────────────┘  │
│              ▼                   │
│  ┌───────────────────────────┐  │
│  │  Audio Segmentation       │  │
│  │  (Split by Speaker)       │  │
│  └───────────┬───────────────┘  │
│              ▼                   │
│  ┌───────────────────────────┐  │
│  │  NVIDIA Audio Flamingo    │  │
│  │  (Transcription)          │  │
│  └───────────┬───────────────┘  │
│              ▼                   │
│  ┌───────────────────────────┐  │
│  │  Stream Results (SSE)     │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

### Processing Flow

1. **Model Loading (Startup)**
   - PyAnnote's speaker-diarization-3.1 pipeline loads
   - NVIDIA's Audio Flamingo-3 model loads
   - Models are cached in Docker volume for faster subsequent starts

2. **Request Processing**
   - Client uploads WAV file via `/diarization` endpoint
   - File is temporarily saved to `temp/` directory
   - Validation ensures only WAV files are accepted

3. **Speaker Diarization**
   - PyAnnote pipeline analyzes audio and identifies speaker segments
   - Consecutive segments from the same speaker are merged
   - Each segment gets timestamps and speaker labels

4. **Audio Segmentation**
   - Audio is split based on speaker segments
   - Each segment is saved to `splits/` directory as a separate WAV file

5. **Transcription**
   - Each audio segment is transcribed using Audio Flamingo model
   - Transcription uses a conversational AI approach for accuracy

6. **Streaming Response**
   - Results are streamed back to client as JSON via SSE
   - Client receives segments as they're processed
   - Temporary files are cleaned up after processing

### Project Structure

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
├── .env                                 # Environment variables (not in git)
└── .env.sample                          # Environment template
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ROADMAP -->
## Roadmap

- [x] Speaker diarization with PyAnnote
- [x] Speech transcription with NVIDIA Audio Flamingo
- [x] Docker containerization
- [x] Streaming API responses
- [x] WAV file support
- [ ] Support for additional audio formats (MP3, FLAC, OGG)
- [ ] GPU acceleration support
- [ ] Batch processing endpoint
- [ ] WebSocket support for real-time streaming
- [ ] Speaker identification (not just diarization)
- [ ] Multi-language support
- [ ] API authentication and rate limiting
- [ ] Cloud deployment guides (AWS, GCP, Azure)

See the [open issues](https://github.com/Sethuram2003/Speech-Diarization/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

Sethuram - [@Sethuram2003](https://github.com/Sethuram2003)

Project Link: [https://github.com/Sethuram2003/Speech-Diarization](https://github.com/Sethuram2003/Speech-Diarization)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

This project wouldn't be possible without these amazing resources and technologies:

* [PyAnnote Audio](https://github.com/pyannote/pyannote-audio) - Speaker diarization models
* [NVIDIA Audio Flamingo](https://huggingface.co/nvidia/audio-flamingo-3-hf) - Speech transcription model
* [Hugging Face](https://huggingface.co) - Model hosting and transformers library
* [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework for building APIs
* [Docker](https://www.docker.com/) - Containerization platform
* [PyTorch](https://pytorch.org/) - Deep learning framework
* [Best-README-Template](https://github.com/othneildrew/Best-README-Template) - README template
* [Choose an Open Source License](https://choosealicense.com) - License guidance
* [Img Shields](https://shields.io) - README badges

### Production Considerations

For production use, consider [PyAnnote AI](https://www.pyannote.ai/) which offers:
- Faster inference times
- Better accuracy
- Commercial support
- Managed infrastructure

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/Sethuram2003/Speech-Diarization.svg?style=for-the-badge
[contributors-url]: https://github.com/Sethuram2003/Speech-Diarization/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Sethuram2003/Speech-Diarization.svg?style=for-the-badge
[forks-url]: https://github.com/Sethuram2003/Speech-Diarization/network/members
[stars-shield]: https://img.shields.io/github/stars/Sethuram2003/Speech-Diarization.svg?style=for-the-badge
[stars-url]: https://github.com/Sethuram2003/Speech-Diarization/stargazers
[issues-shield]: https://img.shields.io/github/issues/Sethuram2003/Speech-Diarization.svg?style=for-the-badge
[issues-url]: https://github.com/Sethuram2003/Speech-Diarization/issues
[license-shield]: https://img.shields.io/github/license/Sethuram2003/Speech-Diarization.svg?style=for-the-badge
[license-url]: https://github.com/Sethuram2003/Speech-Diarization/blob/master/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/sethuram2003

[FastAPI-badge]: https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white
[FastAPI-url]: https://fastapi.tiangolo.com/
[Python-badge]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/
[Docker-badge]: https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com/
[PyTorch-badge]: https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white
[PyTorch-url]: https://pytorch.org/
[HuggingFace-badge]: https://img.shields.io/badge/HuggingFace-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black
[HuggingFace-url]: https://huggingface.co/
