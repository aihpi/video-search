export type SearchType = "keyword" | "semantic" | "llm";

export const SearchTypeNames: Record<SearchType, string> = {
  keyword: "Keyword Search",
  semantic: "Semantic Search",
  llm: "LLM Synthesis",
};

export type QuestionRequest = {
  question: string;
  transcriptId: string;
  topK?: number;
  searchType?: SearchType;
};

export type SegmentResult = {
  segmentId: string;
  startTime: number;
  endTime: number;
  text: string;
  transcriptId: string;
  relevanceScore: number | null;
};

export type LlmAnswer = {
  summary: string;
  notAddressed: boolean;
  modelId: string;
};

export type BaseSearchResponse = {
  question: string;
  transcriptId: string;
  results: SegmentResult[];
  searchType: SearchType;
};

export type KeywordSearchResponse = BaseSearchResponse & {
  searchType: "keyword";
};

export type SemanticSearchResponse = BaseSearchResponse & {
  searchType: "semantic";
};

export type LlmSearchResponse = BaseSearchResponse &
  LlmAnswer & {
    searchType: "llm";
  };

export type QuestionResponse =
  | KeywordSearchResponse
  | SemanticSearchResponse
  | LlmSearchResponse;
