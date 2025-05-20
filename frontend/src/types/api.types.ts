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

export type QueryResult = {
  segmentId: string;
  startTime: number;
  endTime: number;
  text: string;
  transcriptId: string;
};

export type QuestionRequest = {
  question: string;
  transcriptId: string;
  topK?: number;
};

export type QuestionResponse = {
  question: string;
  transcriptId: string;
  results: QueryResult[];
};
