import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Video } from "@/types";
import axios from "axios";
import { Film, Loader2, PlayCircle, Upload } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { VideoPlayerModal } from "./VideoPlayerModal";

interface VideoPanelProps {
  videos: Video[];
  setVideos: React.Dispatch<React.SetStateAction<Video[]>>;
}

export function VideoPanel({ videos, setVideos }: VideoPanelProps) {
  const [uploadedVideo, setUploadedVideo] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedVideo, setSelectedVideo] = useState<Video | null>(null);
  const [taskId, setTaskId] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setUploadedVideo(event.target.files[0]);
    }
  };

  const startProcessing = async () => {
    if (!uploadedVideo) return;

    setIsProcessing(true);

    try {
      const formData = new FormData();
      formData.append("file", uploadedVideo); // key "file" matches backend UploadFile param

      // Use your actual backend URL here
      const response = await axios.post<{ taskId: string }>(
        "http://localhost:8080/process-video",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );

      setTaskId(response.data.taskId);
    } catch (error) {
      console.error("Error starting processing:", error);
      setIsProcessing(false);
    }
  };

  // Polling effect to check task status
  useEffect(() => {
    if (!taskId) return;

    const interval = setInterval(async () => {
      try {
        const statusResponse = await axios.get<{
          status: "pending" | "in_progress" | "completed" | "failed" | string;
          videoUrl?: string;
          thumbnailUrl?: string;
          title?: string;
        }>(`http://localhost:8080/task-status/${taskId}`);

        const status = statusResponse.data.status.toLowerCase();

        if (status === "completed") {
          const newVideo: Video = {
            id: videos.length + 1,
            title: statusResponse.data.title || `Processed Video ${videos.length + 1}`,
            url: statusResponse.data.videoUrl || "",
            thumbnail:
              statusResponse.data.thumbnailUrl ||
              "https://images.unsplash.com/photo-1605810230434-7631ac76ec81?w=800",
          };
          setVideos((prev) => [newVideo, ...prev]);
          setIsProcessing(false);
          setUploadedVideo(null);
          setTaskId(null);
          clearInterval(interval);
        } else if (status === "failed" || status === "not_found") {
          console.error("Video processing failed or task not found.");
          setIsProcessing(false);
          setTaskId(null);
          clearInterval(interval);
        }
        // else if status is pending or in_progress, keep polling
      } catch (error) {
        console.error("Error checking task status:", error);
        setIsProcessing(false);
        setTaskId(null);
        clearInterval(interval);
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(interval);
  }, [taskId, setVideos, videos.length]);

  return (
    <>
      <Card className="h-full flex flex-col bg-transparent border-none shadow-none">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Film /> Video Hub
          </CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4 flex-grow">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            className="hidden"
            accept="video/mp4"
          />
          <Button onClick={() => fileInputRef.current?.click()} disabled={isProcessing}>
            <Upload className="mr-2 h-4 w-4" /> Upload Video
          </Button>

          {uploadedVideo && (
            <div className="p-4 rounded-md bg-background/50 backdrop-blur-sm text-sm flex justify-between items-center">
              <span>{uploadedVideo.name}</span>
              <Button onClick={startProcessing} disabled={isProcessing}>
                {isProcessing && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Process
              </Button>
            </div>
          )}

          <div className="flex-grow overflow-y-auto pr-2">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2 gap-4">
              {videos.map((video) => (
                <div
                  key={video.id}
                  className="group relative aspect-video cursor-pointer overflow-hidden rounded-lg border-2 border-transparent hover:border-primary transition-all duration-300"
                  onClick={() => setSelectedVideo(video)}
                >
                  <img
                    src={video.thumbnail}
                    alt={video.title}
                    className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-black/50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <PlayCircle className="w-12 h-12 text-white" />
                  </div>
                  <p className="absolute bottom-0 left-0 right-0 p-2 bg-gradient-to-t from-black/80 to-transparent text-white text-xs truncate">
                    {video.title}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      <VideoPlayerModal
        isOpen={!!selectedVideo}
        onClose={() => setSelectedVideo(null)}
        videoUrl={selectedVideo?.url || null}
        title={selectedVideo?.title || ""}
      />
    </>
  );
}
