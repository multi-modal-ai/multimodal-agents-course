
const ChatHeader = () => {
  return (
    <div className="border-b border-red-900 bg-black p-4">
      <div className="max-w-4xl mx-auto flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-red-500">KUBRICK AI</h1>
          <p className="text-sm text-gray-400 mt-1">HAL 9000 COMPUTER SYSTEM</p>
        </div>
        <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
      </div>
    </div>
  );
};

export default ChatHeader;
