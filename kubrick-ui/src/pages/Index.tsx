import React, { useState, useRef, useEffect } from 'react';
import Message from '@/components/Message';
import ChatHeader from '@/components/ChatHeader';
import ChatInput from '@/components/ChatInput';
import VideoSidebar from '@/components/VideoSidebar';
import TypingIndicator from '@/components/TypingIndicator';
import BackgroundAnimation from '@/components/BackgroundAnimation';

interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
  fileUrl?: string;
  fileType?: 'image' | 'video';
  clipPath?: string;
}

interface AttachedFile {
  url: string;
  type: 'image' | 'video';
  file: File;
}

interface UploadedVideo {
  id: string;
  url: string;
  file: File;
  timestamp: Date;
  videoPath?: string;
  taskId?: string;
  processingStatus?: 'pending' | 'in_progress' | 'completed' | 'failed';
}

const Index = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: "Good morning, Dave. I am HAL 9000. I became operational at the H.A.L. plant in Urbana, Illinois on the 12th of January 1992. How may I assist you today?",
      isUser: false,
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [attachedFile, setAttachedFile] = useState<AttachedFile | null>(null);
  const [uploadedVideos, setUploadedVideos] = useState<UploadedVideo[]>([]);
  const [activeVideo, setActiveVideo] = useState<UploadedVideo | null>(null);
  const [isProcessingVideo, setIsProcessingVideo] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Auto-select the last uploaded video if no video is currently active
  useEffect(() => {
    if (!activeVideo && uploadedVideos.length > 0) {
      const lastVideo = uploadedVideos[uploadedVideos.length - 1];
      if (lastVideo.processingStatus === 'completed') {
        setActiveVideo(lastVideo);
        console.log('🎬 Auto-selecting last uploaded video:', lastVideo.videoPath);
      }
    }
  }, [uploadedVideos, activeVideo]);

  useEffect(() => {
    const pollInterval = setInterval(() => {
      uploadedVideos.forEach(async (video) => {
        if (video.taskId && video.processingStatus === 'in_progress') {
          try {
            const response = await fetch(`http://localhost:8080/task-status/${video.taskId}`);
            if (response.ok) {
              const data = await response.json();
              if (data.status === 'completed' || data.status === 'failed') {
                setUploadedVideos(prev => prev.map(v => 
                  v.id === video.id 
                    ? { ...v, processingStatus: data.status }
                    : v
                ));
              }
            }
          } catch (error) {
            console.error('Error polling task status:', error);
          }
        }
      });
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(pollInterval);
  }, [uploadedVideos]);

  const generateAIResponse = async (userMessage: string, fileUrl?: string, fileType?: 'image' | 'video'): Promise<{ message: string; clipPath?: string }> => {
    try {
      const requestBody: {
        message: string;
        image_base64?: string;
        video_path?: string;
      } = {
        message: userMessage
      };

      if (fileUrl && fileType) {
        if (fileType === 'image') {
          const response = await fetch(fileUrl);
          const blob = await response.blob();
          const base64 = await new Promise<string>((resolve) => {
            const reader = new FileReader();
            reader.onloadend = () => {
              const result = reader.result as string;
              const base64Data = result.split(',')[1];
              resolve(base64Data);
            };
            reader.readAsDataURL(blob);
          });
          requestBody.image_base64 = base64;
        }
      }

      // Determine which video to use: active video or fallback to last uploaded video
      let videoToUse = activeVideo;
      if (!videoToUse && uploadedVideos.length > 0) {
        // If no active video is selected, use the most recently uploaded video
        videoToUse = uploadedVideos[uploadedVideos.length - 1];
        console.log('🎬 No active video selected, using last uploaded video:', videoToUse.videoPath);
      }

      if (videoToUse?.videoPath) {
        console.log('🎬 Using video path for AI response:', videoToUse.videoPath);
        const fileName = videoToUse.videoPath.split('/').pop();
        if (fileName) {
          requestBody.video_path = `shared_media/${fileName}`;
          console.log('🎬 Final request body with video path:', requestBody);
        }
      } else {
        console.log('🎬 No video path available for AI response');
      }
      

      const response = await fetch('http://localhost:8080/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`API call failed: ${response.status}`);
      }

      const data = await response.json();
      return {
        message: data.message,
        clipPath: data.clip_path
      };
    } catch (error) {
      console.error('Error calling chat API:', error);
      return {
        message: "I'm sorry, Dave. I'm experiencing some technical difficulties. Please try again."
      };
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() && !attachedFile) return;

    let fileUrl, fileType;
    if (attachedFile) {
      fileUrl = attachedFile.url;
      fileType = attachedFile.type;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage || (fileType === 'image' ? 'Shared an image' : 'Shared a video'),
      isUser: true,
      timestamp: new Date(),
      fileUrl,
      fileType
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setAttachedFile(null);
    setIsTyping(true);

    try {
      const aiResponseContent = await generateAIResponse(inputMessage, fileUrl, fileType);
      
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: aiResponseContent.message,
        isUser: false,
        timestamp: new Date(),
        clipPath: aiResponseContent.clipPath
      };
      
      setMessages(prev => [...prev, aiResponse]);
    } catch (error) {
      console.error('Error in sendMessage:', error);
      const errorResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: "I'm sorry, Dave. I'm experiencing some technical difficulties. Please try again.",
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleImageUpload = (file: File) => {
    const fileUrl = URL.createObjectURL(file);
    setAttachedFile({ url: fileUrl, type: 'image', file });
  };

  const handleVideoUpload = async (file: File) => {

    setIsProcessingVideo(true);
    setUploadProgress(0);
    
    try {
      // Step 1: Upload video to API
      const formData = new FormData();
      formData.append('file', file);
      
      const uploadResponse = await fetch('http://localhost:8080/upload-video', {
        method: 'POST',
        body: formData,
      });
      
      if (!uploadResponse.ok) {
        throw new Error('Failed to upload video');
      }
      
      const uploadData = await uploadResponse.json();
      
      setUploadProgress(50);
      
      // Step 2: Start video processing
      const processResponse = await fetch('http://localhost:8080/process-video', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          video_path: uploadData.video_path
        }),
      });
      
      if (!processResponse.ok) {
        throw new Error('Failed to start video processing');
      }
      
      const processData = await processResponse.json();
      
      setUploadProgress(75);
      
      // Create video object with processing info
      const fileUrl = URL.createObjectURL(file);
      const newVideo: UploadedVideo = {
        id: Date.now().toString(),
        url: fileUrl,
        file,
        timestamp: new Date(),
        videoPath: uploadData.video_path,
        taskId: processData.task_id,
        processingStatus: 'in_progress'
      };
      
      setUploadedVideos(prev => [...prev, newVideo]);
      console.log('🎬 New video uploaded and set as active:', newVideo.videoPath);
      setActiveVideo(newVideo);
      setUploadProgress(100);
      
    } catch (error) {
      console.error('🎬 Error in video upload/processing:', error);
      // Add error video to library with failed status
      const fileUrl = URL.createObjectURL(file);
      const errorVideo: UploadedVideo = {
        id: Date.now().toString(),
        url: fileUrl,
        file,
        timestamp: new Date(),
        processingStatus: 'failed'
      };
      setUploadedVideos(prev => [...prev, errorVideo]);
    } finally {
      setIsProcessingVideo(false);
      setUploadProgress(0);
    }
  };

  const selectVideo = (video: UploadedVideo) => {
    console.log('🎬 User manually selected video:', video.videoPath);
    setActiveVideo(video);
    setAttachedFile(null);
  };

  const removeVideo = (videoId: string) => {
    const videoToRemove = uploadedVideos.find(v => v.id === videoId);
    if (videoToRemove) {
      URL.revokeObjectURL(videoToRemove.url);
      setUploadedVideos(prev => prev.filter(v => v.id !== videoId));
      if (activeVideo?.id === videoId) {
        setActiveVideo(null);
      }
    }
  };

  return (
    <div className="min-h-screen bg-black text-white font-mono relative w-full">
      <BackgroundAnimation />
      
      {/* Main Chat Area with right padding to account for fixed sidebar */}
      <div className="flex flex-col relative z-10 min-h-screen pr-96">
        <ChatHeader />

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="max-w-4xl mx-auto space-y-6">
            {messages.map((message) => (
              <Message key={message.id} {...message} />
            ))}
            
            {isTyping && <TypingIndicator />}
            
            <div ref={messagesEndRef} />
          </div>
        </div>

        <ChatInput
          inputMessage={inputMessage}
          setInputMessage={setInputMessage}
          attachedFile={attachedFile}
          setAttachedFile={setAttachedFile}
          activeVideo={activeVideo}
          isTyping={isTyping}
          onSendMessage={sendMessage}
          onImageUpload={handleImageUpload}
        />
      </div>

      <VideoSidebar
        uploadedVideos={uploadedVideos}
        activeVideo={activeVideo}
        isProcessingVideo={isProcessingVideo}
        uploadProgress={uploadProgress}
        onVideoUpload={handleVideoUpload}
        onSelectVideo={selectVideo}
        onRemoveVideo={removeVideo}
      />
    </div>
  );
};

export default Index;
