import React from "react";

interface YouTubePlayerProps {
  videoId: string;
  width?: string | number;
  height?: string | number;
}

const YouTubePlayer: React.FC<YouTubePlayerProps> = ({
  videoId,
  width = "100%",
  height = "315",
}) => {
  const embedUrl = `https://www.youtube.com/embed/${videoId}`;

  return (
    <div className="video-responsive">
      <iframe
        width={width}
        height={height}
        src={embedUrl}
        title="YouTube video player"
        style={{ border: 0 }}
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowFullScreen
      ></iframe>
    </div>
  );
};

export default YouTubePlayer;
