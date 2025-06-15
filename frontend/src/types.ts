
export interface Video {
  id: number;
  title: string;
  url: string;
  thumbnail: string;
}

export interface Message {
  id: number;
  text: string;
  sender: "user" | "bot";
  image?: string;
}
