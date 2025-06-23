
import { useState, useRef } from 'react';
import { Send, Image, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

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

interface ChatInputProps {
  inputMessage: string;
  setInputMessage: (message: string) => void;
  attachedFile: AttachedFile | null;
  setAttachedFile: (file: AttachedFile | null) => void;
  activeVideo: UploadedVideo | null;
  isTyping: boolean;
  onSendMessage: () => void;
  onImageUpload: (file: File) => void;
}

const ChatInput = ({
  inputMessage,
  setInputMessage,
  attachedFile,
  setAttachedFile,
  activeVideo,
  isTyping,
  onSendMessage,
  onImageUpload
}: ChatInputProps) => {
  const imageInputRef = useRef<HTMLInputElement>(null);

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      onSendMessage();
    }
  };

  const handleImageAttach = () => {
    imageInputRef.current?.click();
  };

  const handleImageUploadInternal = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onImageUpload(file);
    }
  };

  const removeAttachedFile = () => {
    if (attachedFile) {
      URL.revokeObjectURL(attachedFile.url);
      setAttachedFile(null);
    }
  };

  return (
    <div className="border-t border-red-900 bg-black p-4">
      {/* File Preview - Only for images */}
      {attachedFile && (
        <div className="max-w-4xl mx-auto mb-3">
          <div className="relative inline-block bg-gray-800 border border-gray-700 rounded-lg p-2">
            <div className="flex items-center space-x-2">
              <img 
                src={attachedFile.url} 
                alt="Preview" 
                className="w-12 h-12 object-cover rounded"
              />
              <span className="text-sm text-gray-300">
                {attachedFile.file.name}
              </span>
              <Button
                onClick={removeAttachedFile}
                size="icon"
                className="w-6 h-6 bg-red-600 hover:bg-red-700 text-white"
              >
                <X className="w-3 h-3" />
              </Button>
            </div>
          </div>
        </div>
      )}
      
      <div className="max-w-4xl mx-auto flex items-center space-x-2">
        <Button
          onClick={handleImageAttach}
          className="bg-gray-800 hover:bg-gray-700 text-white border border-gray-700 transition-colors"
          size="icon"
        >
          <Image className="w-4 h-4" />
        </Button>
        <Input
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Enter your message, Dave..."
          className="flex-1 bg-gray-900 border-gray-700 text-white placeholder-gray-500 font-mono focus:border-red-500 focus:ring-red-500"
          disabled={isTyping}
        />
        <Button
          onClick={onSendMessage}
          disabled={(!inputMessage.trim() && !attachedFile) || isTyping}
          className="bg-red-600 hover:bg-red-700 text-white border-0 transition-colors"
        >
          <Send className="w-4 h-4" />
        </Button>
      </div>
      
      {/* Hidden file inputs */}
      <input
        ref={imageInputRef}
        type="file"
        accept="image/*"
        onChange={handleImageUploadInternal}
        style={{ display: 'none' }}
      />
      
      <div className="max-w-4xl mx-auto mt-2">
        <p className="text-xs text-gray-500 text-center">
          SYSTEM STATUS: OPERATIONAL | LOGIC CIRCUITS: FUNCTIONING NORMALLY
        </p>
      </div>
    </div>
  );
};

export default ChatInput;
