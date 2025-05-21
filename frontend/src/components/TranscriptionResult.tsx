import React, { useState } from "react";
import type {
  TranscriptionResponse,
  QueryResult,
  TranscriptSegment,
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
  const [segmentResults, setSegmentResults] = useState<QueryResult[]>(
    transcriptionResponse.segments.map((segment) => {
      return {
        startTime: segment.start,
        endTime: segment.end,
        text: segment.text,
        segmentId: segment.id,
        transcriptId: transcriptionResponse.id,
        relevanceScore: null,
      } as QueryResult;
    })
  );
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeSegment, setActiveSegment] = useState<string | null>(null);

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds < 10 ? "0" : ""}${remainingSeconds}`;
  };

  const segmentsToQueryResults = (segments: TranscriptSegment[]) => {
    return segments.map((segment) => {
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

  const handleQueryTranscript = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setIsLoading(true);
    setError(null);

    console.log("Question:", question);
    try {
      const response = await queryTranscript(
        question,
        transcriptionResponse.id
      );
      console.log("Query response:", response);
      setSegmentResults(response.results);
      setActiveSegment(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
      setSegmentResults([]);
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
    setSegmentResults(segmentsToQueryResults(transcriptionResponse.segments));
    setActiveSegment(null);
    setError(null);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
      <div className="flex items-center flex-col">
        <h2 className="text-xl font-semibold text-gray-800 text-center flex-1 mb-4">
          Transcription
        </h2>
        <form onSubmit={handleQueryTranscript} className="mb-6 w-full">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="What is discussed in this video?"
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
          {segmentResults.length > 0 &&
            segmentResults.map((result: QueryResult) => (
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

          {segmentResults.length === 0 && !isLoading && !error && question && (
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
