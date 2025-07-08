// Transcription
export type WhisperModelType =
  | "tiny"
  | "base"
  | "small"
  | "medium"
  | "large"
  | "turbo";

export type TranscriptionRequest = {
  videoUrl: string;
  language?: string | null;
  model?: WhisperModelType;
};

export type TranscriptSegment = {
  id: string;
  start: number;
  end: number;
  text: string;
};

export type TranscriptionResponse = {
  id: string;
  audioUrl: string;
  language: string;
  text: string;
  segments: TranscriptSegment[];
};
