import React, { useState } from "react";
import {
  type TranscriptionResponse,
  type QueryResult,
  type SearchType,
  SearchTypeNames,
} from "../types/api.types";
import { queryTranscript } from "../services/api";
import { LoadingIndicatorButton } from "./LoadingIndicatorButton";

interface TranscriptionResultProps {
  transcriptionResponse: TranscriptionResponse;
  onSeekToTime?: (seconds: number) => void;
}

const TranscriptionResult: React.FC<TranscriptionResultProps> = ({
  transcriptionResponse,
  onSeekToTime,
}) => {
  const [question, setQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeSegment, setActiveSegment] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<SearchType>("keyword");

  // State for storing results from different search methods
  const [keywordResults, setKeywordResults] = useState<QueryResult[]>([]);
  const [semanticResults, setSemanticResults] = useState<QueryResult[]>([]);

  // Track which search methods have been used so far
  const [searchesPerformed, setSearchesPerformed] = useState<{
    keyword: boolean;
    semantic: boolean;
  }>({
    keyword: false,
    semantic: false,
  });

  // Get results for the current active tab
  const getActiveTabResults = () => {
    switch (activeTab) {
      case "keyword":
        return keywordResults;
      case "semantic":
        return semanticResults;
      default:
        return [];
    }
  };

  // Get initial segments as QueryResult objects
  const getInitialQueryResults = (): QueryResult[] => {
    return transcriptionResponse.segments.map((segment) => {
      return {
        startTime: segment.start,
        endTime: segment.end,
        text: segment.text,
        segmentId: segment.id,
        transcriptId: transcriptionResponse.id,
        relevanceScore: null,
      } as QueryResult;
    });
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds < 10 ? "0" : ""}${remainingSeconds}`;
  };

  const handleQueryTranscript = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setIsLoading(true);
    setError(null);

    console.log("Question:", question, "Search type:", activeTab);
    try {
      const response = await queryTranscript(
        question,
        transcriptionResponse.id,
        5,
        activeTab
      );
      console.log("Query response:", response);

      // Store results in the appropriate state variable
      if (activeTab === "keyword") {
        setKeywordResults(response.results);
        setSearchesPerformed((prev) => ({ ...prev, keyword: true }));
      } else if (activeTab === "semantic") {
        setSemanticResults(response.results);
        setSearchesPerformed((prev) => ({ ...prev, semantic: true }));
      }

      setActiveSegment(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");

      // Clear results for the current tab on error
      if (activeTab === "keyword") {
        setKeywordResults([]);
      } else if (activeTab === "semantic") {
        setSemanticResults([]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleResultClick = (segment: QueryResult) => {
    if (onSeekToTime) {
      onSeekToTime(segment.startTime);
    }
    setActiveSegment(segment.segmentId);
  };

  const handleClearSearch = () => {
    setQuestion("");
    setKeywordResults([]);
    setSemanticResults([]);
    setSearchesPerformed({ keyword: false, semantic: false });
    setActiveSegment(null);
    setError(null);
  };

  const handleTabChange = (tab: SearchType) => {
    setActiveTab(tab);
    setActiveSegment(null);
    setError(null);
  };

  const currentResults: () => QueryResult[] = () => {
    const activeTabResults = getActiveTabResults();
    if (activeTabResults.length > 0) {
      return activeTabResults;
    }
    if (!searchesPerformed[activeTab]) {
      return getInitialQueryResults();
    }
    return [];
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
      <div className="flex items-center flex-col">
        <h2 className="text-xl font-semibold text-gray-800 text-center flex-1 mb-4">
          Transcription
        </h2>
        <form onSubmit={handleQueryTranscript} className="mb-2 w-full">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder={`Search using ${SearchTypeNames[activeTab]}`}
                className="w-full px-3 py-2 pr-8 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                disabled={isLoading}
              />

              {question && !isLoading && (
                <div
                  className="absolute inset-y-0 right-0 pr-3 flex items-center cursor-pointer"
                  onClick={() => handleClearSearch()}
                  role="button"
                  tabIndex={0}
                  aria-label="Clear search"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-4 w-4 text-gray-400 hover:text-gray-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </div>
              )}
            </div>
            <LoadingIndicatorButton
              isLoading={isLoading}
              buttonText="Search"
              disabled={isLoading || !question.trim()}
            />
          </div>
        </form>
      </div>

      {/* Segments */}
      <div>
        <div className="bg-gray-50 p-4 rounded-md space-y-2 max-h-96 overflow-y-auto">
          {/* Search Type Tabs */}
          <div className="flex border-b border-gray-200 mb-4">
            <button
              onClick={() => handleTabChange("keyword")}
              className={`px-4 py-2 text-sm font-medium ${
                activeTab === "keyword"
                  ? "text-indigo-600 border-b-2 border-indigo-600"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              {SearchTypeNames.keyword} {searchesPerformed.keyword && "✓"}
            </button>
            <button
              onClick={() => handleTabChange("semantic")}
              className={`px-4 py-2 text-sm font-medium ml-4 ${
                activeTab === "semantic"
                  ? "text-indigo-600 border-b-2 border-indigo-600"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              {SearchTypeNames.semantic} {searchesPerformed.semantic && "✓"}
            </button>
          </div>
          {currentResults().length > 0 &&
            currentResults().map((result: QueryResult) => (
              <div
                key={result.segmentId}
                className={`p-3 rounded-md cursor-pointer ${
                  activeSegment === result.segmentId
                    ? "bg-indigo-50 border border-indigo-200"
                    : "bg-white border border-gray-200"
                }`}
                onClick={() => handleResultClick(result)}
              >
                <div className="flex justify-between text-sm text-gray-500 mb-1">
                  <span>
                    {formatTime(result.startTime)} -{" "}
                    {formatTime(result.endTime)}
                  </span>
                  <span
                    className="px-2 py-1 rounded-md text-xs font-medium"
                    style={{
                      backgroundColor: result.relevanceScore
                        ? `rgba(79, 70, 229, ${result.relevanceScore / 100})`
                        : "transparent",
                    }}
                  >
                    {result.relevanceScore ? `${result.relevanceScore}%` : " "}
                  </span>
                </div>
                <p className="text-gray-800">{result.text}</p>
              </div>
            ))}

          {currentResults().length === 0 &&
            !isLoading &&
            !error &&
            question && (
              <p className="text-sm text-gray-500">
                No relevant segments found for your question.
              </p>
            )}
        </div>
      </div>
    </div>
  );
};

export default TranscriptionResult;
