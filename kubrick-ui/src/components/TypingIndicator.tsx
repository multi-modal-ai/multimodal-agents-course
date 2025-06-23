
const TypingIndicator = () => {
  return (
    <div className="flex justify-start animate-fade-in">
      <div className="max-w-[70%] p-4 rounded-lg bg-red-950 border border-red-800 text-red-100">
        <div className="text-xs mb-2 text-red-400">HAL 9000</div>
        <div className="flex items-center space-x-2">
          <div className="flex space-x-1">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-bounce"></div>
            <div className="w-2 h-2 bg-red-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
            <div className="w-2 h-2 bg-red-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
          </div>
          <span className="text-sm">Processing...</span>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;
