import axios from "axios";

import type {
  TranscriptionRequest,
  TranscriptionResponse,
  WhisperModelType,
} from "../types/api.types";

const API_URL = "http://localhost:9091";

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const transcribeVideo = async (
  videoUrl: string,
  language?: string,
  model?: WhisperModelType
): Promise<TranscriptionResponse> => {
  const requestBody: TranscriptionRequest = {
    videoUrl,
    language,
    model,
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
