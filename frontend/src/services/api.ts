import axios from "axios";

import type {
  TranscriptionRequest,
  TranscriptionResponse,
  WhisperModelType,
} from "../types/transcription.types";
import type {
  QuestionRequest,
  QuestionResponse,
  SearchType,
} from "../types/search.types";

import type {
  LlmInfo,
  LlmListResponse,
  LlmSelectResponse,
} from "../types/llms.types";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:9091";

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const transcribeVideoUrl = async (
  videoUrl: string,
  model?: WhisperModelType,
  language?: string
): Promise<TranscriptionResponse> => {
  // Convert empty string to null for language
  // This ensures FastAPI/Pydantic properly recognizes it as Optional[str]
  const requestBody: TranscriptionRequest = {
    videoUrl,
    model,
    language: language === "" ? null : language,
  };

  try {
    const response = await apiClient.post<TranscriptionResponse>(
      "/transcribe/video-url",
      requestBody
    );
    return response.data;
  } catch (error) {
    console.error("Error during transcription:", error);
    throw error;
  }
};

export const transcribeVideoFile = async (
  videoFile: File,
  model?: WhisperModelType,
  language?: string
): Promise<TranscriptionResponse> => {
  const formData = new FormData();
  formData.append("video_file", videoFile);

  if (model) {
    formData.append("model", model);
  }

  if (language && language !== "") {
    formData.append("language", language);
  }

  try {
    const response = await axios.post<TranscriptionResponse>(
      `${API_URL}/transcribe/video-file`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error("Error during file transcription:", error);
    throw error;
  }
};

export const queryTranscript = async (
  question: string,
  transcriptId: string,
  topK: number = 5,
  searchType: SearchType = "keyword"
): Promise<QuestionResponse> => {
  const requestBody: QuestionRequest = {
    question,
    transcriptId,
    topK,
    searchType,
  };

  try {
    const response = await apiClient.post<QuestionResponse>(
      "/search/query",
      requestBody
    );
    return response.data;
  } catch (error) {
    console.error("Error during query:", error);
    throw error;
  }
};

export const getCurrentLlmInfo = async (): Promise<LlmInfo | null> => {
  try {
    const response = await apiClient.get("/llms/current");
    return response.data;
  } catch (error) {
    console.error("Error while retrieving current LLM info:", error);
    throw error;
  }
};

export const listLlms = async (): Promise<LlmListResponse> => {
  try {
    const response = await apiClient.get("/llms");
    return response.data;
  } catch (error) {
    console.error("Error while retrieving list of available models", error);
    throw error;
  }
};

export const selectLlm = async (
  modelId: string
): Promise<LlmSelectResponse> => {
  try {
    const response = await apiClient.post("/llms/select", { modelId });
    return response.data;
  } catch (error) {
    console.error(`Error selecting model ${modelId}`, error);
    throw error;
  }
};
