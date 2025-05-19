import React, { useState } from "react";
import { queryTranscript } from "../services/api";
import type { QueryResult } from "../types/api.types";

interface QuestionAnsweringProps {
  transcriptId: string;
  onSeekToTime?: (time: number) => void;
}

const QuestionAnswering: React.FC<QuestionAnsweringProps> = ({
  transcriptId,
  onSeekToTime,
}) => {
  const [question, setQuestion] = useState("");
  const [results, setResults] = useState<QueryResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setIsLoading(true);
    setError(null);

    console.log("Question:", question);
    console.log("Transcript ID:", transcriptId);
    try {
      const response = await queryTranscript(question, transcriptId);
      setResults(response.results);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds < 10 ? "0" : ""}${remainingSeconds}`;
  };

  const handleResultClick = (time: number) => {
    if (onSeekToTime) {
      onSeekToTime(time);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mt-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">
        Ask Questions About the Video
      </h3>

      <form onSubmit={handleSubmit} className="mb-6">
        <div className="flex gap-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="What is discussed in this video?"
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !question.trim()}
            className={`px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${
              isLoading
                ? "bg-gray-400"
                : "bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            }`}
          >
            {isLoading ? "Searching..." : "Search"}
          </button>
        </div>
      </form>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {results.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-gray-700">
            Found {results.length} relevant segments:
          </h4>
          {results.map((result, index) => (
            <div
              key={`${result.segmentId}-${index}`}
              className="p-3 bg-gray-50 rounded-md hover:bg-gray-100 cursor-pointer transition-colors"
              onClick={() => handleResultClick(result.startTime)}
            >
              <div className="flex justify-between items-start mb-1">
                <span className="text-sm font-medium text-indigo-600">
                  {formatTime(result.startTime)} - {formatTime(result.endTime)}
                </span>
                <span className="text-xs text-gray-500">
                  Click to jump to this time
                </span>
              </div>
              <p className="text-sm text-gray-800">{result.text}</p>
            </div>
          ))}
        </div>
      )}

      {results.length === 0 && !isLoading && !error && question && (
        <p className="text-sm text-gray-500">
          No relevant segments found for your question.
        </p>
      )}
    </div>
  );
};

export default QuestionAnswering;
