# Video Search Demonstrator

A machine learning workshop demo showcasing progressively sophisticated methods for searching through video content. This project demonstrates the evolution from simple text search to advanced AI-powered video understanding.

## Overview

This application allows users to:

- Transcribe YouTube videos using OpenAI Whisper
- Search through video content using multiple search paradigms
- Navigate directly to relevant video segments with click-to-seek functionality

## Search Methods (Progressive Sophistication)

### 1. ✅ Keyword Search

- **Status**: Implemented
- **Description**: Simple text matching within transcript segments
- **Use Case**: Finding exact phrases or specific terms mentioned in the video

### 2. ✅ Semantic Search

- **Status**: Implemented
- **Description**: Vector similarity search using multilingual sentence embeddings
- **Technology**: Uses `paraphrase-multilingual-MiniLM-L12-v2` embeddings stored in ChromaDB
- **Use Case**: Finding conceptually related content even when exact words don't match

### 3. ⚠️ LLM Synthesis

- **Status**: Infrastructure ready, implementation pending
- **Description**: Uses Large Language Models to synthesize coherent answers from semantic search results
- **Use Case**: Getting comprehensive answers that combine information from multiple video segments

### 4. 🔜 Vision-Language Model (VLM) Search

- **Status**: Planned
- **Description**: Search through visual content of videos using VLMs
- **Use Case**: Finding specific visual elements, scenes, or objects in videos

### 5. 🔜 Advanced Search Methods

Additional sophisticated approaches to explore:

- **Multi-modal Re-ranking**: Use cross-encoders to improve search result relevance
- **Cross-lingual Search**: Query in one language, find results in another

## Tech Stack

### Backend

- **FastAPI**: REST API framework
- **OpenAI Whisper**: Speech-to-text transcription
- **ChromaDB**: Vector database for embeddings
- **Sentence Transformers**: Multilingual embeddings
- **yt-dlp**: YouTube video downloading
- **FFmpeg**: Audio extraction

### Frontend

- **React + TypeScript**: UI framework
- **Vite**: Build tool
- **Tailwind CSS**: Styling
- **Vitest**: Testing framework

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 16+
- FFmpeg installed on your system

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

Create a `.env` file in the backend directory:

```
EMBEDDING_MODEL_NAME=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
CHROMA_DB_DIR=chroma_db
COLLECTION_NAME=transcript_embeddings
```

## API Endpoints

- `POST /transcribe-video`: Transcribe a YouTube video
- `POST /query-transcript`: Search through transcribed content
- `GET /models`: List available LLM models (for synthesis)
- `POST /select-model`: Select an LLM model
- `POST /llm-answer`: Generate synthesized answers (coming soon)

## Current Issues and TODOs

- Highlight search keywords in keyword search results
- Propagate errors from search result component to app error component
- Support file upload in addition to Video URL
- Fix tokenizer parallelism warnings by setting `TOKENIZERS_PARALLELISM=false`
- Complete LLM synthesis implementation
- Implement VLM search functionality
- Add progress indicators for long-running operations
- Implement result caching for repeated queries

## Workshop Usage

This demonstrator is designed for ML workshops to showcase:

1. The progression from simple to sophisticated search methods
2. How different AI technologies can be combined for better results
3. Practical implementation of embeddings, vector databases, and LLMs
4. The importance of user experience (click-to-seek functionality)

Each search method builds upon the previous ones, demonstrating increasing levels of AI sophistication while maintaining practical usability.

## Contributing

Feel free to extend this demonstrator with additional search methods or improvements to existing ones. The modular architecture makes it easy to add new search strategies.
