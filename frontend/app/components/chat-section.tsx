"use client";

import { useChat } from "ai/react";
import { useState } from "react";
import { ChatInput, ChatMessages } from "./ui/chat";
import { useClientConfig } from "./ui/chat/hooks/use-config";
import DisclaimerMessage from "./disclaimer-message";

export default function ChatSection() {
  const { backend } = useClientConfig();
  const [requestData, setRequestData] = useState<any>();
  const {
    messages,
    input,
    isLoading,
    handleSubmit,
    handleInputChange,
    reload,
    stop,
    append,
    setInput,
  } = useChat({
    body: { data: requestData },
    api: `${backend}/api/chat`,
    headers: {
      "Content-Type": "application/json", // using JSON because of vercel/ai 2.2.26
    },
    onError: (error: unknown) => {
      if (!(error instanceof Error)) throw error;
      const message = JSON.parse(error.message);
      alert(message.detail);
    },
  });

  return (
    <div className="w-full h-full flex flex-col bg-white p-4 lg:p-6 rounded-b-lg">
      
      <div className="flex-grow flex flex-col">
        {messages.length === 0 && !isLoading ? (
          // If chat is empty, show disclaimer
          <div className="flex-grow flex flex-col justify-end">
            <DisclaimerMessage />
          </div>
        ) : (
          // Otherwise, show the chat messages.
          <ChatMessages
            messages={messages}
            isLoading={isLoading}
            reload={reload}
            stop={stop}
            append={append}
          />
        )}
      </div>

      <div className="mt-4">
        <ChatInput
          input={input}
          handleSubmit={handleSubmit}
          handleInputChange={handleInputChange}
          isLoading={isLoading}
          messages={messages}
          append={append}
          setInput={setInput}
          requestParams={{ params: requestData }}
          setRequestData={setRequestData}
        />
      </div>
    </div>
  );
}