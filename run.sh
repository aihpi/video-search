#!/bin/bash

# Check if GPU is available
if nvidia-smi &> /dev/null; then
    PROFILE="gpu"
    OLLAMA_CONTAINER="video-search-ollama-gpu-1"
    echo "GPU detected - using GPU profile"
else
    PROFILE="cpu"
    OLLAMA_CONTAINER="video-search-ollama-cpu-1"
    echo "No GPU detected - using CPU profile"
fi

# Start services in detached mode
docker compose --profile $PROFILE up -d

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
until curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
  echo -n "."
  sleep 2
done
echo " Ready!"

# Check if qwen3:8b model exists
if ! docker exec $OLLAMA_CONTAINER ollama list | grep -q "qwen3:8b"; then
    echo "Pulling qwen3:8b model (this may take a few minutes)..."
    docker exec $OLLAMA_CONTAINER ollama pull qwen3:8b
else
    echo "Model qwen3:8b already available"
fi

echo "All services ready! Opening http://localhost:5173"
echo "Press Ctrl+C to stop all services"

# Follow logs
docker compose --profile $PROFILE logs -f