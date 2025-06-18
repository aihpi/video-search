export type LlmInfo = {
  modelId: string;
  displayName: string;
  requiresGpu: boolean;
  hfModelId: string;
  loaded: boolean;
};

export type LlmListResponse = {
  models: LlmInfo[];
  activeModelId: string | null;
  hasGpu: boolean;
};

export type LlmSelectResponse = {
  success: boolean;
  modelId: string | null;
};
