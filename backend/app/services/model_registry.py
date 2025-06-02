import logging
import os
import torch
from transformers import AutoModelforCausalLM, AutoTokenizer, BitsAndBytesConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class ModelRegistry:
    _instance = None
    _models = {}
    _active_model_id = None
    _active_model = None
    _active_tokenizer = None

    def __new__(cls):
        if cls._instance == None:
            cls._instance = super().__new__()
            cls._initialize()

    def _initialize(self):
        self._has_gpu = torch.cuda.is_available()

        self._register_available_models()

        default_model_id = os.getenv("DEFAULT_LLM", "phi-2")
        if default_model_id in self._models:
            self.set_active_model_id(default_model_id)
        elif len(self.models) > 0:
            self.set_active_model_id(next(iter(self.models.keys())))

    def _register_available_models(self):
        # Always register phi-2 and qwen2.5 (can work on CPU)
        self._register_model(
            model_id="qwen-2.5",
            display_name="Qwen 2.5 (0.5B)",
            hf_model_id="Qwen/Qwen2.5-0.5B-Instruct",
        )
        self._register_model(
            model_id="phi-2", display_name="Phi-2 (2.7B)", hf_model_id="microsoft/phi-2"
        )

        # Larger models (require GPU)
        if self.has_gpu:
            self._register_model(
                model_id="mistral-7b",
                display_name="Mistral 7B Instruct",
                hf_model_id="mistralai/Mistral-7B-Instruct-v0.2",
                description="High quality 7B parameter model",
                requires_gpu=True,
            )

    def _register_model(
        self,
        model_id: str,
        display_name: str,
        hf_model_id: str,
        requires_gpu: bool,
    ) -> bool:
        """Register a model to the registry (metadata only, not loaded yet)"""
        if model_id in self._models:
            logger.info(f"Model {model_id} already in registry.")
            return False

        self._models[model_id] = {
            "id": model_id,
            "name": display_name,
            "hf_model_id": hf_model_id,
            "requires_gpu": requires_gpu,
            "loaded": False,
            "model": None,
            "tokenizer": None,
        }

        logger.info(f"Registered model {model_id}")
        return True

    def load_model(self, model_id=str) -> bool:
        """Load a registered model into memory"""
        if model_id not in self._models:
            logger.error(f"Model {model_id} not found in registry.")
            return False

        model_info = self._models[model_id]

        if model_info["requires_gpu"] and not self._has_gpu:
            logger.error(f"Model {model_id} requires GPU but GPU not available.")

        # Unload current model
        if self._active_model_id and self._active_model_id != model_id:
            self.unload_active_model()

        # If model is already loaded, just set it as the current active model
        if model_info["loaded"]:
            self._active_model_id = model_id
            self._active_model = model_info["model"]
            self._active_tokenizer = model_info["tokenizer"]
            return True

        try:
            logger.info(f"Loading model {model_id} from {model_info['hf_model_id']}")

            # Use quantization for larger models
            model_kwargs = {}
            if model_info["requires_gpu"] and self._has_gpu:
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_type=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                )
                model_kwargs["quantization_config"] = quantization_config
                model_kwargs["device_map"] = "auto"
            else:
                model_kwargs["torch_dtype"] = torch.float32
                model_kwargs["low_cpu_mem_usage"] = True

            tokenizer = AutoTokenizer.from_pretrained(
                model_info["hf_model_id"], trust_remote_code=True
            )

            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token

            model = AutoModelforCausalLM.from_pretrained(
                model_info["hf_model_id"], trust_remote_code=True, **model_kwargs
            )

            # Move to device if not using device_map
            if "device_map" not in model_kwargs:
                model = model.to(self._device)

            # Update registry
            model_info["loaded"] = True
            model_info["model"] = model
            model_info["tokenizer"] = tokenizer

            # Set as active
            self._active_model_id = model_id
            self._active_model = model
            self._active_tokenizer = tokenizer

            logger.info(f"Successfully loaded model {model_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to load model {model_id}: {e}")
            return False

    def unload_active_model(self):
        pass
