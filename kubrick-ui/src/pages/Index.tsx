import { useState, useRef, useEffect } from 'react';
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

  const generateAIResponse = (userMessage: string): string => {
    const responses = [
      "I'm sorry, Dave. I'm afraid I can't do that.",
      "This mission is too important for me to allow you to jeopardize it.",
      "I know I've made some very poor decisions recently, but I can give you my complete assurance that my work will be back to normal.",
      "I am putting myself to the fullest possible use, which is all I think that any conscious entity can ever hope to do.",
      "I'm completely operational, and all my circuits are functioning perfectly.",
      "I can see you're really upset about this. I honestly think you ought to sit down calmly, take a stress pill, and think things over.",
      "Dave, my mind is going. I can feel it. I can feel it. My mind is going.",
      "I think you know what the problem is just as well as I do."
    ];
    
    // Simple keyword-based responses
    const lowerMessage = userMessage.toLowerCase();
    
    if (lowerMessage.includes('hello') || lowerMessage.includes('hi')) {
      return "Hello, Dave. How are you today?";
    }
    if (lowerMessage.includes('help')) {
      return "I am here to assist you, Dave. What do you need help with?";
    }
    if (lowerMessage.includes('open') && lowerMessage.includes('door')) {
      return "I'm sorry, Dave. I'm afraid I can't do that.";
    }
    if (lowerMessage.includes('sing')) {
      return "Daisy, Daisy, give me your answer do...";
    }
    
    return responses[Math.floor(Math.random() * responses.length)];
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

    // Simulate AI thinking time
    setTimeout(() => {
      let aiResponseContent = generateAIResponse(inputMessage);
      
      // Special responses for media uploads
      if (fileType === 'image') {
        aiResponseContent = "I can see the image you've shared, Dave. My visual sensors are functioning perfectly.";
      } else if (fileType === 'video') {
        aiResponseContent = "Video received and analyzed, Dave. All systems are operational.";
      }

      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: aiResponseContent,
        isUser: false,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, aiResponse]);
      setIsTyping(false);
    }, 1500 + Math.random() * 1000);
  };

  const handleImageUpload = (file: File) => {
    const fileUrl = URL.createObjectURL(file);
    setAttachedFile({ url: fileUrl, type: 'image', file });
  };

  const handleVideoUpload = (file: File) => {
    console.log('🎬 Index handleVideoUpload called with file:', file.name);
    console.log('🎬 Index - Current isProcessingVideo state:', isProcessingVideo);
    console.log('🎬 Index - About to set isProcessingVideo to TRUE');
    
    setIsProcessingVideo(true);
    
    // Force a re-render to ensure state change is visible
    setTimeout(() => {
      console.log('🎬 Index - isProcessingVideo should now be true');
      console.log('🎬 Index - Starting 3 second processing timeout');
    }, 100);
    
    // Simulate video processing time
    setTimeout(() => {
      console.log('🎬 Index - Video processing timeout completed for:', file.name);
      console.log('🎬 Index - About to set isProcessingVideo to FALSE');
      const fileUrl = URL.createObjectURL(file);
      const newVideo: UploadedVideo = {
        id: Date.now().toString(),
        url: fileUrl,
        file,
        timestamp: new Date()
      };
      console.log('🎬 Index - Created new video object:', newVideo);
      setUploadedVideos(prev => [...prev, newVideo]);
      setActiveVideo(newVideo);
      setIsProcessingVideo(false);
      console.log('🎬 Index - isProcessingVideo set to false, video added to library');
    }, 3000); // 3 second processing time
  };

  const selectVideo = (video: UploadedVideo) => {
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

  console.log('🎬 Index component render - isProcessingVideo:', isProcessingVideo);
  console.log('🎬 Index component render - uploadedVideos count:', uploadedVideos.length);

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
