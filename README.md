Install requirements for frontend:

```bash
# install lib required for pyaudio
apt update && apt install -y portaudio19-dev && apt-get clean && rm -rf /var/lib/apt/lists/*

# update pip to support for whl.metadata -> less downloading
pip install --no-cache-dir -U "pip>=24"

# install pytorch, but without the nvidia-libs that are only necessary for gpu
#pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Retrieve nvidia-libs for using GPU
LD_LIBRARY_PATH="/usr/local/lib/python3.10/site-packages/nvidia/cublas/lib:/usr/local/lib/python3.10/site-packages/nvidia/cudnn/lib"

# install the requirements for running the whisper-live server
pip install --no-cache-dir -r frontend/requirements.txt
```

Preload model (if desired)
```bash
MODEL_NAME=turbo
python preload_model.py --model-name "${MODEL_NAME}"
```

Initialise the server
```bash
DEBIAN_FRONTEND=noninteractive
python run_server.py
```