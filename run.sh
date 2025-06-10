#!/bin/bash

# Check if GPU is available
if nvidia-smi &> /dev/null; then
    echo "GPU detected - using GPU profile"
    docker compose --profile gpu up
else
    echo "No GPU detected - using CPU profile"
    docker compose --profile cpu up
fi