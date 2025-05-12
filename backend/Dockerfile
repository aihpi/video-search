FROM python:3.12-slim

# Set environment variables
# Prevent Python from writing .pyc files (bytecode cache files)
ENV PYTHONDONTWRITEBYTECODE=1 
# Prevent Python from buffering stdout and stderr (Prevents log messages from being lost if the container crashes)
ENV PYTHONUNBUFFERED=1
# Suppress interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive 

# Install system dependencies (apt-get clean not needed https://docs.docker.com/build/building/best-practices/#run)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/* 

# Set the working directory
WORKDIR /app

# Explicitly install CPU-only version of torch (dependency of openai-whisper)
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Copy only requirements.txt to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Load default model to disk while building the image
ARG DEFAULT_MODEL=tiny
RUN python -c "import whisper; whisper.load_model('${DEFAULT_MODEL}')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9091"]