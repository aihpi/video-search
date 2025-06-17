import React, { useState, useRef } from "react";
import "./App.css";
import TranscriptionForm, {
  type TranscriptionFormHandle,
} from "./components/TranscriptionForm";
import TranscriptionResult from "./components/TranscriptionResult";
import type { TranscriptionResponse } from "./types/transcription.types";

const App: React.FC = () => {
  const [transcriptionResult, setTranscriptionResult] =
    useState<TranscriptionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const transcriptionFormRef = useRef<TranscriptionFormHandle>(null);

  const handleTranscriptionComplete = (result: TranscriptionResponse) => {
    setTranscriptionResult(result);
    setError(null);
  };

  const handleError = (error: Error | null) => {
    if (!error) {
      setError(null);
      return;
    }
    setError(error.message);
    setTranscriptionResult(null);
  };

  const handleSeekToTime = (seconds: number) => {
    if (transcriptionFormRef.current) {
      transcriptionFormRef.current.seekToTime(seconds);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center justify-center mb-4">
            <img
              src="/hpi_logo.png"
              alt="HPI KISZ Logo"
              className="h-14 w-auto mr-4"
            />
            <img
              src="/bmbf_logo.png"
              alt="BMBF Logo"
              className="h-14 w-auto ml-4"
            />
          </div>
          <div className="text-center">
            <h1 className="text-3xl font-extrabold text-gray-900">
              Video Transcription Service
            </h1>
            <p className="mt-2 text-gray-600">
              Enter a YouTube URL to transcribe the video using OpenAI's Whisper
              model
            </p>
          </div>
        </div>
        <div className="h-10 mb-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
              <p className="font-medium">Error: {error}</p>
            </div>
          )}
        </div>
        <div className="space-y-6">
          <TranscriptionForm
            ref={transcriptionFormRef}
            onTranscriptionComplete={handleTranscriptionComplete}
            onError={handleError}
          />
          {transcriptionResult && (
            <TranscriptionResult
              transcriptionResponse={transcriptionResult}
              onSeekToTime={handleSeekToTime}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default App;
