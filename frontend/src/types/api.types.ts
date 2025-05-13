export type WhisperModelType =
  | "tiny"
  | "base"
  | "small"
  | "medium"
  | "large"
  | "turbo";

export interface TranscriptionRequest {
  videoUrl: string;
  language?: string;
  model?: WhisperModelType;
}

export interface TranscriptSegment {
  id: number;
  start: number;
  end: number;
  text: string;
}

export interface TranscriptionResponse {
  id: string;
  audioUrl: string;
  language: string;
  text: string;
  segments: TranscriptSegment[];
}
