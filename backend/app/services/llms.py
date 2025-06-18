import gc
import logging
import os
import re
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from typing import List, Optional
from dotenv import load_dotenv

from ..models.llms import LlmAnswer, LlmInfo
from ..models.search import QueryResult


load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class LLMService:
    _instance = None
    _models = {}
    _active_model_id = None
    _active_model = None
    _active_tokenizer = None
    _device = "cuda" if torch.cuda.is_available() else "cpu"
    _hf_token = None

    def __new__(cls):
        if cls._instance == None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self._has_gpu = torch.cuda.is_available()

        self._hf_token = os.getenv("HUGGINGFACE_HUB_TOKEN")
        self._register_available_models()

        default_model_id = os.getenv("DEFAULT_LLM", "tinyllama")
        if default_model_id in self._models:
            self._active_model_id = default_model_id
        elif len(self._models) > 0:
            self._active_model_id = next(iter(self._models.keys()))

        self.load_model(self._active_model_id)

    def _register_available_models(self):
        # Small models that can work on CPU
        self._register_model(
            model_id="tinyllama",
            display_name="TinyLlama (1.1B)",
            hf_model_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            requires_gpu=False,
        )

        self._register_model(
            model_id="qwen-2.5",
            display_name="Qwen 2.5 (0.5B)",
            hf_model_id="Qwen/Qwen2.5-0.5B-Instruct",
            requires_gpu=False,
        )
        self._register_model(
            model_id="phi-2",
            display_name="Phi-2 (2.7B)",
            hf_model_id="microsoft/phi-2",
            requires_gpu=False,
        )

        # Gated models- only register if HuggingFace token is available
        if self._hf_token:
            self._register_model(
                model_id="gemma-2b",
                display_name="Gemma 2 (2B)",
                hf_model_id="google/gemma-2-2b-it",
                requires_gpu=False,
            )

        self._register_model(
            model_id="stablelm-2",
            display_name="StableLM 2 (1.6B)",
            hf_model_id="stabilityai/stablelm-2-1_6b-chat",
            requires_gpu=False,
        )

        self._register_model(
            model_id="smollm2",
            display_name="SmolLM2 (1.7B)",
            hf_model_id="HuggingFaceTB/SmolLM2-1.7B-Instruct",
            requires_gpu=False,
        )

        # Larger models (require GPU)
        if self._has_gpu:
            self._register_model(
                model_id="mistral-7b",
                display_name="Mistral 7B Instruct",
                hf_model_id="mistralai/Mistral-7B-Instruct-v0.2",
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

    def load_model(self, model_id: str) -> bool:
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
                model_info["hf_model_id"], trust_remote_code=True, token=self._hf_token
            )

            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token

            model = AutoModelForCausalLM.from_pretrained(
                model_info["hf_model_id"],
                trust_remote_code=True,
                token=self._hf_token,
                **model_kwargs,
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
        """Remove the current model from memory."""
        if self._active_model_id:
            logger.info(f"Unloading model {self._active_model_id}")

            model_info = self._models[self._active_model_id]

            if model_info["model"]:
                del model_info["model"]

            if model_info["tokenizer"]:
                del model_info["tokenizer"]

            model_info["loaded"] = False
            model_info["model"] = None
            model_info["tokenizer"] = None

            self._active_model = None
            self._active_tokenizer = None
            self._active_model_id = None

            gc.collect()
            if self._has_gpu:
                torch.cuda.empty_cache()

    def generate_answer(
        self, question: str, segments: List[QueryResult], max_new_tokens: int = 512
    ) -> LlmAnswer:
        """Generate a structured answer using the active model."""
        if not self._active_model or not self._active_tokenizer:
            raise ValueError("No model loaded")

        prompt = self._create_prompt(question, segments)

        inputs = self._active_tokenizer(
            prompt, return_tensors="pt", truncation=True, max_length=2048
        )

        if (
            self._device == "cuda"
            and "device_map" not in self._models[self._active_model_id]
        ):
            inputs = inputs.to(self._device)

        with torch.no_grad():
            outputs = self._active_model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
            )

        response = self._active_tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[1] :], skip_special_tokens=True
        )

        # Convert output into structured answer
        answer = self._parse_response(response, question)

        return answer

    def _create_prompt(self, question: str, segments: List[QueryResult]) -> str:
        context = ""
        for segment in segments:
            timestamp_str = f"{segment.start_time:.1f} - {segment.end_time:.1f}"
            context += f"{timestamp_str} {segment.text}\n\n"

        prompt = f"""You are analyzing a video transcript to answer a question.
Based on the transcript segments below, provide a comprehensive answer.

Transcript segments:
{context}

Question: {question}

You MUST format your response EXACTLY as follows:

SUMMARY:
[Write 2-3 sentences summarizing the answer]

COMPLETENESS:
[State one of: "COMPLETE" if the transcript fully answers the question, "PARTIAL" if only some aspects are covered, or "NOT FOUND" if the transcript doesn't contain relevant information]

Answer:"""

        return prompt

    def _parse_response(self, response: str, question: str) -> LlmAnswer:
        summary = ""
        not_addressed = False

        response = response.strip()
        logger.info(f"Parsing response: {response}")

        # Extract SUMMARY section
        summary_match = re.search(
            r"SUMMARY:\s*\n(.*?)(?=COMPLETENESS:|$)",
            response,
            re.DOTALL | re.IGNORECASE,
        )
        if summary_match:
            summary = summary_match.group(1).strip()
            # Remove any bullet points or extra formatting
            summary = " ".join(summary.split())  # Normalize whitespace

        # Extract COMPLETENESS section
        completeness_match = re.search(
            r"COMPLETENESS:\s*\n(.*?)(?:\n|$)", response, re.DOTALL | re.IGNORECASE
        )
        if completeness_match:
            completeness_str = completeness_match.group(1).strip().upper()
            if "NOT FOUND" in completeness_str or "NOT_FOUND" in completeness_str:
                not_addressed = True
            else:
                not_addressed = False

        # Fallbacks if parsing fails
        if not summary:
            # Try to extract first paragraph as summary
            first_para = response.split("\n\n")[0].strip()
            if first_para and not first_para.startswith(("SUMMARY:", "COMPLETENESS:")):
                summary = first_para
            else:
                summary = f"Analysis of the video transcript regarding: {question}"

        return LlmAnswer(
            summary=summary,
            not_addressed=not_addressed,
            model_id=self._active_model_id,
        )

    def get_available_models(self) -> List[LlmInfo]:
        """Get list of available models with their current status."""
        models = []
        for model_id, model_data in self._models.items():
            models.append(
                LlmInfo(
                    model_id=model_id,
                    display_name=model_data["name"],
                    hf_model_id=model_data["hf_model_id"],
                    requires_gpu=model_data["requires_gpu"],
                    loaded=model_data["loaded"],
                )
            )
        return models

    def get_active_model_id(self) -> Optional[str]:
        """Get the currently active model ID."""
        return self._active_model_id

    def select_model(self, model_id: str) -> bool:
        """Select and load a model."""
        return self.load_model(model_id)

    def has_gpu(self) -> bool:
        """Check if GPU is available."""
        return self._has_gpu


llm_service = LLMService()
