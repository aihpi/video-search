import React, { useState } from "react";
import type {
  WhisperModelType,
  TranscriptionResponse,
} from "../types/api.types";
import { transcribeVideo } from "../services/api";

interface TranscriptionFormProps {
  onTranscriptionComplete: (result: TranscriptionResponse) => void;
  onError: (error: Error) => void;
}

const TranscriptionForm: React.FC<TranscriptionFormProps> = ({
  onTranscriptionComplete,
  onError,
}) => {
  const [videoUrl, setVideoUrl] = useState("");
  const [language, setLanguage] = useState("");
  const [model, setModel] = useState<WhisperModelType>("tiny");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const response = await transcribeVideo(videoUrl, language, model);
      onTranscriptionComplete(response);
    } catch (error) {
      console.error("Error during transcription:", error);
      onError(
        error instanceof Error ? error : new Error("An unknown error occurred")
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-4 p-6 bg-white rounded-lg shadow-md"
    >
      <div>
        <label
          htmlFor="videoUrl"
          className="block text-sm font-medium text-gray-700"
        >
          Video URL
        </label>
        <input
          type="url"
          id="videoUrl"
          value={videoUrl}
          onChange={(e) => setVideoUrl(e.target.value)}
          placeholder="https://www.youtube.com/watch?v=..."
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          required
        />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label
            htmlFor="language"
            className="block text-sm font-medium text-gray-700"
          >
            Language
          </label>
          <select
            id="language"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="de">German</option>
            <option value="en">English</option>
            <option value="fr">French</option>
            <option value="es">Spanish</option>
          </select>
        </div>
        <div>
          <label
            htmlFor="model"
            className="block text-sm font-medium text-gray-700"
          >
            Whisper Model
          </label>
          <select
            id="model"
            value={model}
            onChange={(e) => {
              const selectedModel = e.target.value as WhisperModelType;
              if (selectedModel) {
                setModel(selectedModel);
              }
            }}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="tiny">Tiny (Fastest)</option>
            <option value="base">Base</option>
            <option value="small">Small</option>
            <option value="medium">Medium</option>
            <option value="large">Large (Most Accurate)</option>
            <option value="turbo">Turbo</option>
          </select>
        </div>
      </div>
      <div>
        <button
          type="submit"
          disabled={isLoading}
          className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-gray-700 ${
            isLoading ? "bg-indigo-400" : "bg-indigo-600 hover:bg-indigo-700"
          } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500`}
        >
          {isLoading ? (
            <>
              <svg
                className="animate-spin -ml-1 mr-3 h-5 w-5 text-gray-700"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Processing...
            </>
          ) : (
            "Transcribe Video"
          )}
        </button>
      </div>
    </form>
  );
};

export default TranscriptionForm;
