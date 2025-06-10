import React, { useState, useEffect } from "react";
import { listLlms, selectLlm, getCurrentLlmInfo } from "../services/api";
import { LoadingIndicatorButton } from "./LoadingIndicatorButton";
import type { LlmInfo, LlmListResponse } from "../types/llms.types";

interface LLMSelectorProps {
  onError: (error: Error | null) => void;
}

const LLMSelector: React.FC<LLMSelectorProps> = ({ onError }) => {
  const [llms, setLlms] = useState<LlmInfo[]>([]);
  const [currentLlm, setCurrentLlm] = useState<LlmInfo | null>(null);
  const [selectedLlmId, setSelectedLlmId] = useState<string>("");
  const [activeModelId, setActiveModelId] = useState<string | null>(null);
  const [hasGpu, setHasGpu] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingModels, setIsLoadingModels] = useState(true);

  useEffect(() => {
    loadModels();
    loadCurrentLlm();
  }, []);

  const loadModels = async () => {
    try {
      setIsLoadingModels(true);
      const response: LlmListResponse = await listLlms();
      setLlms(response.models);
      setActiveModelId(response.activeModelId);
      setHasGpu(response.hasGpu);
      setSelectedLlmId(response.activeModelId || "");
      onError(null);
    } catch (error) {
      console.error("Error loading LLM models:", error);
      onError(
        error instanceof Error ? error : new Error("Failed to load LLM models")
      );
    } finally {
      setIsLoadingModels(false);
    }
  };

  const loadCurrentLlm = async () => {
    try {
      const llmInfo = await getCurrentLlmInfo();
      setCurrentLlm(llmInfo);
    } catch (error) {
      console.error("Error loading current LLM:", error);
    }
  };

  const handleSelectModel = async () => {
    if (!selectedLlmId) return;

    try {
      setIsLoading(true);
      const response = await selectLlm(selectedLlmId);
      if (response.success) {
        setActiveModelId(selectedLlmId);
        await loadCurrentLlm();
        onError(null);
      } else {
        throw new Error("Failed to select model");
      }
    } catch (error) {
      console.error("Error selecting LLM model:", error);
      onError(
        error instanceof Error ? error : new Error("Failed to select LLM model")
      );
    } finally {
      setIsLoading(false);
    }
  };

  const getModelStatus = (llm: LlmInfo) => {
    if (llm.modelId === activeModelId)
      return { label: "Active", color: "bg-green-100 text-green-800" };
    if (llm.loaded)
      return { label: "Loaded", color: "bg-blue-100 text-blue-800" };
    return { label: "Not Loaded", color: "bg-gray-100 text-gray-800" };
  };

  const StatusBadge = ({ llm }: { llm: LlmInfo }) => {
    const status = getModelStatus(llm);
    return (
      <span
        className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${status.color}`}
      >
        {status.label}
      </span>
    );
  };

  if (isLoadingModels) {
    return (
      <div className="p-6 bg-white rounded-lg shadow-md">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          <span className="ml-2 text-gray-600">Loading LLM models...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-white rounded-lg shadow-md space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900">
          LLM Model Selection
        </h3>
        {!hasGpu && (
          <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">
            No GPU Available
          </span>
        )}
      </div>

      <div className="space-y-2">
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {llms.map((llm) => {
            const isActive = llm.modelId === activeModelId;
            const isDisabled = llm.requiresGpu && !hasGpu;

            return (
              <div
                key={llm.modelId}
                onClick={() =>
                  !isDisabled && !isActive && setSelectedLlmId(llm.modelId)
                }
                className={`flex items-center justify-between p-3 border rounded-md transition-colors ${
                  isDisabled
                    ? "border-gray-200 bg-gray-50 cursor-not-allowed opacity-60"
                    : isActive
                      ? "border-indigo-300 bg-indigo-50 cursor-default"
                      : "border-gray-200 hover:bg-gray-50 cursor-pointer"
                }`}
              >
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">
                    {llm.displayName}
                  </p>
                  <p className="text-xs text-gray-500">
                    {llm.hfModelId}
                    {llm.requiresGpu && (
                      <span className="ml-2 text-orange-600">
                        • Requires GPU
                      </span>
                    )}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <StatusBadge llm={llm} />
                  {selectedLlmId === llm.modelId && !isActive && (
                    <LoadingIndicatorButton
                      isLoading={isLoading}
                      buttonText="Activate"
                      onClick={handleSelectModel}
                      type="button"
                      className="px-3 py-1 text-xs"
                    />
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default LLMSelector;
