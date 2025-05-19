import React, { useEffect, useRef, useImperativeHandle, forwardRef } from "react";

interface YouTubePlayerProps {
  videoId: string;
  width?: string | number;
  height?: string | number;
}

export interface YouTubePlayerHandle {
  seekTo: (seconds: number) => void;
}

declare global {
  interface Window {
    YT: any;
    onYouTubeIframeAPIReady?: () => void;
  }
}

const YouTubePlayer = forwardRef<YouTubePlayerHandle, YouTubePlayerProps>(
  ({ videoId, width = "100%", height = "315" }, ref) => {
    const playerRef = useRef<any>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    useImperativeHandle(ref, () => ({
      seekTo: (seconds: number) => {
        if (playerRef.current && playerRef.current.seekTo) {
          playerRef.current.seekTo(seconds, true);
        }
      },
    }));

    useEffect(() => {
      // Load YouTube iframe API
      if (!window.YT) {
        const tag = document.createElement("script");
        tag.src = "https://www.youtube.com/iframe_api";
        const firstScriptTag = document.getElementsByTagName("script")[0];
        firstScriptTag.parentNode?.insertBefore(tag, firstScriptTag);

        window.onYouTubeIframeAPIReady = () => {
          createPlayer();
        };
      } else {
        createPlayer();
      }

      function createPlayer() {
        if (containerRef.current && window.YT) {
          playerRef.current = new window.YT.Player(containerRef.current, {
            height: height,
            width: width,
            videoId: videoId,
            playerVars: {
              'playsinline': 1
            },
          });
        }
      }

      return () => {
        if (playerRef.current && playerRef.current.destroy) {
          playerRef.current.destroy();
        }
      };
    }, [videoId, width, height]);

    return <div ref={containerRef} className="video-responsive" />;
  }
);

YouTubePlayer.displayName = "YouTubePlayer";

export default YouTubePlayer;
