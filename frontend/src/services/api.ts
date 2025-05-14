import axios from "axios";

import type {
  TranscriptionRequest,
  TranscriptionResponse,
  WhisperModelType,
} from "../types/api.types";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:9091";

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const transcribeVideo = async (
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
      "/transcribe-video",
      requestBody
    );
    return response.data;
  } catch (error) {
    console.error("Error during transcription:", error);
    throw error;
  }
};
