
import { useState } from "react";
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from "@/components/ui/resizable";
import { VideoPanel } from "@/components/VideoPanel";
import { ChatPanel } from "@/components/ChatPanel";
import { Video } from "@/types";

const Index = () => {
  const [videos, setVideos] = useState<Video[]>([]);

  const handleNewVideo = (video: Video) => {
    setVideos(prev => [video, ...prev]);
  };

  return (
    <div className="h-screen w-screen bg-transparent text-foreground p-4 flex flex-col gap-4">
      <header className="text-center py-4">
        <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl text-primary">Video Analysis AI</h1>
        <p className="text-muted-foreground mt-2">Upload a video, process it, and start asking questions.</p>
      </header>
      <main className="flex-grow">
        <ResizablePanelGroup direction="horizontal" className="h-full max-w-full rounded-lg border">
          <ResizablePanel defaultSize={50}>
            <div className="h-full p-2">
              <VideoPanel videos={videos} setVideos={setVideos} />
            </div>
          </ResizablePanel>
          <ResizableHandle withHandle />
          <ResizablePanel defaultSize={50}>
             <div className="h-full p-2">
              <ChatPanel onNewVideo={handleNewVideo} />
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
      </main>
    </div>
  );
};

export default Index;
