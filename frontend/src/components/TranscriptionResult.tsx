import React, { useState } from "react";
import type {
  TranscriptionResponse,
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
  const [filteredSegments, setFilteredSegments] = useState<TranscriptSegment[]>(
    transcriptionResponse.segments
  );
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeSegment, setActiveSegment] = useState<string | null>(null);

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

    console.log("Question:", question);
    console.log("Transcript ID:", transcriptionResponse.id);
    try {
      const response = await queryTranscript(
        question,
        transcriptionResponse.id
      );
      setFilteredSegments(
        transcriptionResponse.segments.filter((segment) =>
          response.results.some((result) => result.segmentId === segment.id)
        )
      );
      setActiveSegment(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
      setFilteredSegments([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResultClick = (segment: TranscriptSegment) => {
    if (onSeekToTime) {
      onSeekToTime(segment.start);
    }
    setActiveSegment(segment.id);
  };

  const handleClearSearch = () => {
    setQuestion("");
    setFilteredSegments(transcriptionResponse.segments);
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
          {filteredSegments.length > 0 &&
            filteredSegments.map((segment: TranscriptSegment) => (
              <div
                key={segment.id}
                className={`p-3 rounded-md cursor-pointer ${
                  activeSegment === segment.id
                    ? "bg-indigo-50 border border-indigo-200"
                    : "bg-white border border-gray-200"
                }`}
                onClick={() => handleResultClick(segment)}
              >
                <div className="flex justify-between text-sm text-gray-500 mb-1">
                  <span>
                    {formatTime(segment.start)} - {formatTime(segment.end)}
                  </span>
                  <span>{Math.round(segment.end - segment.start)}s</span>
                </div>
                <p className="text-gray-800">{segment.text}</p>
              </div>
            ))}

          {filteredSegments.length === 0 &&
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
