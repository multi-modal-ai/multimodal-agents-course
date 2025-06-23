
import { useRef } from 'react';
import { Play, Upload, X, Loader2, Pause } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface UploadedVideo {
  id: string;
  url: string;
  file: File;
  timestamp: Date;
}

interface VideoSidebarProps {
  uploadedVideos: UploadedVideo[];
  activeVideo: UploadedVideo | null;
  isProcessingVideo: boolean;
  uploadProgress: number;
  onVideoUpload: (file: File) => void;
  onSelectVideo: (video: UploadedVideo) => void;
  onRemoveVideo: (videoId: string) => void;
}

const VideoSidebar = ({
  uploadedVideos,
  activeVideo,
  isProcessingVideo,
  uploadProgress,
  onVideoUpload,
  onSelectVideo,
  onRemoveVideo
}: VideoSidebarProps) => {
  const videoInputRef = useRef<HTMLInputElement>(null);

  const handleVideoUpload = () => {
    console.log('🎬 VideoSidebar handleVideoUpload clicked - videoInputRef:', videoInputRef.current);
    if (videoInputRef.current) {
      console.log('🎬 VideoSidebar - triggering file input click');
      videoInputRef.current.click();
    } else {
      console.error('🎬 VideoSidebar - videoInputRef is null!');
    }
  };

  const handleVideoFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log('🎬 VideoSidebar - handleVideoFileUpload triggered');
    console.log('🎬 VideoSidebar - files:', e.target.files);
    const file = e.target.files?.[0];
    if (file) {
      console.log('🎬 VideoSidebar - Video file selected:', file.name, 'size:', file.size);
      console.log('🎬 VideoSidebar - About to call onVideoUpload prop');
      onVideoUpload(file);
    } else {
      console.log('🎬 VideoSidebar - No file selected');
    }
    // Reset the input so the same file can be selected again
    e.target.value = '';
  };

  const handleVideoClick = (video: UploadedVideo, videoElement: HTMLVideoElement) => {
    // Always select the video as active when clicked
    onSelectVideo(video);
    
    if (videoElement.paused) {
      // Pause all other videos first
      uploadedVideos.forEach((v) => {
        const otherVideo = document.getElementById(`video-${v.id}`) as HTMLVideoElement;
        if (otherVideo && otherVideo !== videoElement && !otherVideo.paused) {
          otherVideo.pause();
        }
      });
      videoElement.play();
    } else {
      videoElement.pause();
    }
  };

  console.log('🎬 VideoSidebar render - isProcessingVideo:', isProcessingVideo);
  console.log('🎬 VideoSidebar render - uploadedVideos count:', uploadedVideos.length);

  return (
    <div className="fixed right-0 top-0 w-96 h-screen border-l border-red-900 bg-black flex flex-col z-20">
      <div className="p-4 border-b border-red-900">
        <h3 className="text-2xl font-bold text-red-500 mb-2 text-center">VIDEO LIBRARY</h3>
        <Button
          onClick={handleVideoUpload}
          className="w-full bg-red-600 hover:bg-red-700 text-white text-xs"
          size="sm"
          disabled={isProcessingVideo}
        >
          {isProcessingVideo ? (
            <div className="flex items-center space-x-2">
              <Loader2 className="w-3 h-3 animate-spin" />
              <span>Processing...</span>
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <Upload className="w-3 h-3" />
              <span>Upload Video</span>
            </div>
          )}
        </Button>
        
        {/* Processing Animation */}
        {isProcessingVideo && (
          <div className="mt-4 p-4 bg-red-950 border border-red-800 rounded">
            <div className="flex flex-col items-center space-y-3">
              {/* Large Spinning Loader */}
              <Loader2 className="w-12 h-12 text-red-500 animate-spin" />
              
              {/* Processing Text */}
              <div className="text-center">
                <div className="text-sm text-red-400 font-bold">PROCESSING</div>
                <div className="text-xs text-red-300 mt-1">Please wait...</div>
              </div>
              
              {/* Animated Dots */}
              <div className="flex justify-center space-x-1">
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" style={{ animationDelay: '0.3s' }}></div>
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" style={{ animationDelay: '0.6s' }}></div>
              </div>
            </div>
          </div>
        )}
      </div>
      
      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {uploadedVideos.map((video) => {
          const isActive = activeVideo?.id === video.id;
          return (
            <div
              key={video.id}
              className={`relative group rounded border ${
                isActive 
                  ? 'border-red-500 bg-red-950' 
                  : 'border-gray-700 bg-gray-800 hover:border-red-700'
              }`}
            >
              <div className="aspect-video relative overflow-hidden rounded-t">
                <video 
                  id={`video-${video.id}`}
                  src={video.url} 
                  className={`w-full h-full object-cover cursor-pointer transition-all duration-300 ${
                    isActive ? '' : 'grayscale hover:grayscale-0'
                  }`}
                  onClick={(e) => handleVideoClick(video, e.currentTarget)}
                  onPlay={() => console.log(`🎬 Video ${video.id} started playing`)}
                  onPause={() => console.log(`🎬 Video ${video.id} paused`)}
                />
                <div 
                  className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-30 cursor-pointer opacity-0 group-hover:opacity-100 transition-opacity"
                  onClick={(e) => {
                    e.stopPropagation();
                    const videoElement = document.getElementById(`video-${video.id}`) as HTMLVideoElement;
                    if (videoElement) {
                      handleVideoClick(video, videoElement);
                    }
                  }}
                >
                  <div className="bg-red-600 rounded-full p-2">
                    <Play className="w-6 h-6 text-white fill-white" />
                  </div>
                </div>
              </div>
              <div className="p-2">
                <p className="text-xs text-gray-300 truncate">{video.file.name}</p>
                <p className="text-xs text-gray-500">{video.timestamp.toLocaleTimeString()}</p>
              </div>
              <Button
                onClick={(e) => {
                  e.stopPropagation();
                  onRemoveVideo(video.id);
                }}
                size="icon"
                className="absolute top-1 right-1 w-6 h-6 bg-red-600 hover:bg-red-700 text-white opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <X className="w-3 h-3" />
              </Button>
            </div>
          );
        })}
      </div>
      
      {/* Hidden file input - with more debugging */}
      <input
        ref={videoInputRef}
        type="file"
        accept="video/*"
        onChange={handleVideoFileUpload}
        style={{ display: 'none' }}
        onClick={() => console.log('🎬 VideoSidebar - file input clicked')}
      />
    </div>
  );
};

export default VideoSidebar;
