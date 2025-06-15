
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Textarea } from "@/components/ui/textarea";
import { Message, Video } from "@/types";
import { Bot, Image as ImageIcon, Send, User } from "lucide-react";
import { useEffect, useRef, useState } from "react";

interface ChatPanelProps {
  onNewVideo: (video: Video) => void;
}

export function ChatPanel({ onNewVideo }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    { id: 1, text: "Hello! Upload a video to get started, or ask me anything.", sender: "bot" },
  ]);
  const [input, setInput] = useState("");
  const imageInputRef = useRef<HTMLInputElement>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  const handleSendMessage = () => {
    if (!input.trim()) return;

    const newUserMessage: Message = { id: Date.now(), text: input, sender: "user" };
    setMessages((prev) => [...prev, newUserMessage]);
    const currentInput = input;
    setInput("");

    setTimeout(() => {
      const shouldReturnVideo = Math.random() > 0.4;
      if (shouldReturnVideo) {
          const newVideo: Video = {
              id: Date.now(),
              title: `AI Result for: "${currentInput}"`,
              url: 'https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4',
              thumbnail: `https://source.unsplash.com/random/400x225?sig=${Date.now()}`
          };
          onNewVideo(newVideo);

          const botResponse: Message = { id: Date.now() + 1, text: `I've generated a video based on your query. You can see it in the Video Hub.`, sender: "bot" };
          setMessages((prev) => [...prev, botResponse]);
      } else {
          const botResponse: Message = { id: Date.now() + 1, text: `I've received your message: "${currentInput}". I am a mock AI. In a real app, I'd provide a helpful answer.`, sender: "bot" };
          setMessages((prev) => [...prev, botResponse]);
      }
    }, 1500);
  };
  
  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      const imageUrl = URL.createObjectURL(file);
      const userMessage: Message = { id: Date.now(), text: `Uploaded image: ${file.name}`, sender: "user", image: imageUrl };
      setMessages(prev => [...prev, userMessage]);
      
      // Simulate API call for similarity search
       setTimeout(() => {
            const botResponse: Message = { id: Date.now() + 1, text: "Here is a video that I found based on your image.", sender: "bot" };
            const newVideo: Video = {
                id: Date.now() + 2,
                title: `Similar to: ${file.name}`,
                url: 'https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4',
                thumbnail: `https://source.unsplash.com/random/400x225?sig=${Date.now()}`
            };
            onNewVideo(newVideo);
            setMessages((prev) => [...prev, botResponse]);
        }, 1500);
    }
  };

  useEffect(() => {
    if (scrollAreaRef.current) {
        const viewport = scrollAreaRef.current.querySelector('div[data-radix-scroll-area-viewport]');
        if (viewport) {
            viewport.scrollTop = viewport.scrollHeight;
        }
    }
  }, [messages]);

  return (
    <Card className="h-full flex flex-col bg-transparent border-none shadow-none">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bot /> KubRick
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col flex-grow gap-4">
        <ScrollArea className="flex-grow pr-4 -mr-4" ref={scrollAreaRef}>
          <div className="space-y-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex items-end gap-3 ${
                  msg.sender === "user" ? "flex-row-reverse" : "flex-row"
                }`}
              >
                <Avatar className="w-8 h-8 flex-shrink-0">
                  <AvatarFallback className={msg.sender === 'user' ? 'bg-primary text-primary-foreground' : 'bg-secondary'}>
                      {msg.sender === 'user' ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5 text-primary" />}
                  </AvatarFallback>
                </Avatar>
                <div
                  className={`max-w-sm p-3 ${
                    msg.sender === "user"
                      ? "bg-primary text-primary-foreground rounded-b-xl rounded-tl-xl"
                      : "bg-secondary rounded-b-xl rounded-tr-xl"
                  }`}
                >
                  <p className="text-sm">{msg.text}</p>
                   {msg.image && <img src={msg.image} alt="uploaded content" className="mt-2 rounded-md max-w-[200px]"/>}
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
        <div className="relative">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
            placeholder="Ask about the video..."
            className="pr-24 bg-background/50 backdrop-blur-sm focus:ring-ring"
          />
          <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
            <input type="file" ref={imageInputRef} onChange={handleImageUpload} className="hidden" accept="image/*" />
            <Button variant="ghost" size="icon" onClick={() => imageInputRef.current?.click()}>
              <ImageIcon className="h-5 w-5" />
            </Button>
            <Button size="icon" onClick={handleSendMessage}>
              <Send className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
