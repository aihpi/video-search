import React, {
  useState,
  useEffect,
  useRef,
  useImperativeHandle,
  forwardRef,
} from "react";
import type {
  WhisperModelType,
  TranscriptionResponse,
} from "../types/transcription.types";
import { transcribeVideo } from "../services/api";
import YouTubePlayer, { type YouTubePlayerHandle } from "./YouTubePlayer";
import { LoadingIndicatorButton } from "./LoadingIndicatorButton";

interface TranscriptionFormProps {
  onTranscriptionComplete: (result: TranscriptionResponse) => void;
  onError: (error: Error | null) => void;
}

export interface TranscriptionFormHandle {
  seekToTime: (seconds: number) => void;
}

const TranscriptionForm = forwardRef<
  TranscriptionFormHandle,
  TranscriptionFormProps
>(({ onTranscriptionComplete, onError }, ref) => {
  const [videoUrl, setVideoUrl] = useState("");
  const [videoId, setVideoId] = useState<string | null>(null);
  const [language, setLanguage] = useState<string>("");
  const [model, setModel] = useState<WhisperModelType>("small");
  const [isLoading, setIsLoading] = useState(false);
  const youtubePlayerRef = useRef<YouTubePlayerHandle>(null);

  useImperativeHandle(ref, () => ({
    seekToTime: (seconds: number) => {
      if (youtubePlayerRef.current) {
        youtubePlayerRef.current.seekTo(seconds);
      }
    },
  }));

  // Extract YouTube video ID from various URL formats
  const extractVideoId = (url: string): string | null => {
    const patterns = [
      /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&?/]+)/i,
      /youtube\.com\/watch\?.*v=([^&]+)/i,
    ];

    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match && match[1]) {
        return match[1];
      }
    }

    return null;
  };

  // Show the YouTube player when a valid URL is entered
  useEffect(() => {
    let id = null;
    if (videoUrl.includes("youtube.com") || videoUrl.includes("youtu.be")) {
      id = extractVideoId(videoUrl);
      setVideoId(id);
    } else {
      setVideoId(id);
    }

    if (!id && videoUrl) {
      onError(new Error("Invalid YouTube URL"));
    } else {
      onError(null);
    }
  }, [videoUrl, onError]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const response = await transcribeVideo(videoUrl, model, language);
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

      {/* Video player container with fixed height */}
      <div
        className="mt-4 bg-gray-50 rounded-md"
        style={{
          minHeight: videoUrl ? "315px" : "0px",
          transition: "min-height 0.3s ease-in-out",
        }}
      >
        {videoId ? (
          <div className="p-4">
            <YouTubePlayer ref={youtubePlayerRef} videoId={videoId} />
          </div>
        ) : videoUrl ? (
          <div className="p-4 flex items-center justify-center h-full">
            <p className="text-gray-400">
              Enter a valid YouTube URL to see the video player
            </p>
          </div>
        ) : null}
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
            <option value="">(Auto)</option>
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
      <LoadingIndicatorButton
        isLoading={isLoading}
        buttonText="Transcribe Video"
      />
    </form>
  );
});

TranscriptionForm.displayName = "TranscriptionForm";

export default TranscriptionForm;
