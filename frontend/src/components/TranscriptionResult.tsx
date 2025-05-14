import React, { useState } from "react";
import type {
  TranscriptionResponse,
  TranscriptSegment,
} from "../types/api.types";

interface TranscriptionResultProps {
  result: TranscriptionResponse;
  onNewTranscription: () => void;
}

const TranscriptionResult: React.FC<TranscriptionResultProps> = ({
  result,
  onNewTranscription,
}) => {
  const [activeSegment, setActiveSegment] = useState<number | null>(null);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text).then(() => {
      alert("Copied to clipboard!");
    });
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds < 10 ? "0" : ""}${remainingSeconds}`;
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-800">
          Transcription Results
        </h2>
        <div className="space-x-2">
          <button
            onClick={() => copyToClipboard(result.text)}
            className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-md text-sm font-medium text-gray-700"
          >
            Copy Text
          </button>
          <button
            onClick={onNewTranscription}
            className="px-3 py-1 bg-indigo-100 hover:bg-indigo-200 rounded-md text-sm font-medium text-indigo-700"
          >
            New Transcription
          </button>
        </div>
      </div>

      {/* Audio Player */}
      <div className="bg-gray-50 p-4 rounded-md">
        <h3 className="text-sm font-medium text-gray-700 mb-2">Audio</h3>
        <audio
          controls
          className="w-full"
          src={`http://localhost:9091${result.audio_url}`}
        >
          Your browser does not support the audio element.
        </audio>
      </div>

      {/* Full Transcription */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-2">
          Complete Transcription
        </h3>
        <div className="bg-gray-50 p-4 rounded-md">
          <p className="text-gray-800 whitespace-pre-wrap">{result.text}</p>
        </div>
      </div>

      {/* Segments */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-2">Segments</h3>
        <div className="bg-gray-50 p-4 rounded-md space-y-2 max-h-96 overflow-y-auto">
          {result.segments.map((segment: TranscriptSegment) => (
            <div
              key={segment.id}
              className={`p-3 rounded-md cursor-pointer ${
                activeSegment === segment.id
                  ? "bg-indigo-50 border border-indigo-200"
                  : "bg-white border border-gray-200"
              }`}
              onClick={() => setActiveSegment(segment.id)}
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
        </div>
      </div>
    </div>
  );
};

export default TranscriptionResult;
