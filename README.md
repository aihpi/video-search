# Video Search Demonstrator

A machine learning workshop demo showcasing progressively sophisticated methods for searching through video content. This project demonstrates the evolution from simple text search to advanced AI-powered video understanding.

## Overview

This application allows users to:

- Transcribe YouTube videos and uploaded video files using OpenAI Whisper
- Search through video content using multiple search paradigms
- Navigate directly to relevant video segments with click-to-seek functionality
- Use LLMs to synthesize answers from video content

## Search Methods (Progressive Sophistication)

### 1. ✅ Keyword Search

- **Description**: Simple text matching within transcript segments
- **Use Case**: Finding exact phrases or specific terms mentioned in the video

### 2. ✅ Semantic Search

- **Description**: Vector similarity search using multilingual sentence embeddings
- **Technology**: Uses `paraphrase-multilingual-MiniLM-L12-v2` embeddings stored in ChromaDB
- **Use Case**: Finding conceptually related content even when exact words don't match

### 3. ✅ LLM Synthesis


- **Description**: Uses Large Language Models to synthesize coherent answers from semantic search results
- **Technology**: Supports Ollama (local) or vLLM (production) backends
- **Use Case**: Getting comprehensive answers that combine information from multiple video segments



## Tech Stack

### Backend

- **FastAPI**: REST API framework
- **OpenAI Whisper**: Speech-to-text transcription
- **ChromaDB**: Vector database for embeddings
- **Sentence Transformers**: Multilingual embeddings
- **yt-dlp**: YouTube video downloading
- **FFmpeg**: Audio extraction
- **Ollama/vLLM**: LLM inference backends

### Frontend

- **React + TypeScript**: UI framework
- **Vite**: Build tool
- **Tailwind CSS**: Styling
- **Vitest**: Testing framework

## Getting Started

### Option 1: Docker Setup (Recommended)

#### Prerequisites for Docker
- **Docker** and **Docker Compose** installed
- **NVIDIA Container Toolkit** (for GPU support, optional)

#### Running with Docker

1. Clone the repository:
```bash
git clone <repository-url>
cd video-search
```

2. Run the application:
```bash
./run.sh
```

This script will:
- Detect if you have a GPU and use the appropriate profile
- Start all services (backend, frontend, Ollama)
- Pull the required LLM model (qwen3:8b) on first run
- Open the application at http://localhost:5173

To stop all services, press `Ctrl+C`.

### Option 2: Local Setup (Without Docker)

### Prerequisites

#### Required Software
- **Python 3.10+** (3.12 recommended)
- **FFmpeg** (for audio extraction)
- **Ollama** (for LLM functionality)
- **Node.js 18+** and npm
- **Git** (for cloning the repository)

#### Installation Verification

Verify all prerequisites are installed:

```bash
# Check Python version
python --version  # Should show 3.10 or higher

# Check Node.js and npm
node --version   # Should show v18 or higher
npm --version

# Check FFmpeg
ffmpeg -version  # Should show FFmpeg version info

# Check Git
git --version

# Check Ollama (after installation)
ollama --version
```

### Installing Prerequisites

#### macOS
```bash
# Using Homebrew
brew install python@3.12 node ffmpeg
brew install --cask ollama

# Start Ollama
ollama serve
```

#### Ubuntu/Debian
```bash
# Update package list
sudo apt update

# Install Python and pip
sudo apt install python3.12 python3-pip

# Install Node.js (via NodeSource)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs

# Install FFmpeg
sudo apt install ffmpeg

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
```

#### Windows (using WSL2)
1. Install WSL2 following [Microsoft's guide](https://docs.microsoft.com/en-us/windows/wsl/install)
2. Open WSL2 terminal and follow Ubuntu instructions above

### Project Setup

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd video-search
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the backend server (IMPORTANT: Use this exact command)
python -m app.main
```

The backend will start on **http://localhost:9091**

#### 3. Frontend Setup

Open a new terminal window:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will start on **http://localhost:5173**

### 4. Environment Configuration (Optional)

The application works with sensible defaults. You only need a `.env` file if you want to customize the configuration.

**Default Configuration (no .env needed):**
- LLM Backend: Ollama on http://localhost:11434
- Default Model: qwen3:8b
- Embedding Model: paraphrase-multilingual-MiniLM-L12-v2
- Database: ./chroma_db

**To customize configuration:**

```bash
cd backend
cp .env.example .env
# Edit .env with your preferred settings
```

Example `.env` for customization:
```bash
# Use a different LLM model
LLM_MODEL=llama3.2:3b

# Or use vLLM instead of Ollama
LLM_BACKEND=vllm
VLLM_BASE_URL=http://localhost:8000/v1
```

### 5. Download LLM Model

Before using LLM synthesis, download a model with Ollama:

```bash
# Pull the default model
ollama pull qwen3:8b

# Or choose a smaller model for limited resources
ollama pull llama3.2:3b
```

## API Endpoints

### Transcription
- `POST /transcribe/video-url`: Transcribe a YouTube video from URL
- `POST /transcribe/video-file`: Transcribe an uploaded video file
- `GET /transcribe/audio/{filename}`: Get extracted audio file

### Search
- `POST /search/keyword`: Keyword search in transcripts
- `POST /search/semantic`: Semantic similarity search
- `POST /search/llm`: LLM-synthesized answers from search results

### LLM Management
- `GET /llms/models`: List available LLM models
- `POST /llms/select`: Select active LLM model

## Current Issues and TODOs

- Highlight search keywords in keyword search results
- Fix tokenizer parallelism warnings by setting `TOKENIZERS_PARALLELISM=false`
- Implement VLM search functionality
- Add progress indicators for long-running operations
- Fix tests

## Workshop Usage

This demonstrator is designed for ML workshops to showcase:

1. The progression from simple to sophisticated search methods
2. How different AI technologies can be combined for better results
3. Practical implementation of embeddings, vector databases, and LLMs
4. The importance of user experience (click-to-seek functionality)

Each search method builds upon the previous ones, demonstrating increasing levels of AI sophistication while maintaining practical usability.
