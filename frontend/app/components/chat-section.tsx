"use client";

import { useChat } from "ai/react";
import { useState } from "react";
import DisclaimerMessage from "./disclaimer-message";
import { ChatInput, ChatMessages } from "./ui/chat";
import { useClientConfig } from "./ui/chat/hooks/use-config";

export default function ChatSection() {
  const { backend } = useClientConfig();
  const [requestData, setRequestData] = useState<any>();
  const [isAcmChecked, setIsAcmChecked] = useState(false);
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
      "Content-Type": "application/json",
    },
    onError: (error: unknown) => {
      if (!(error instanceof Error)) throw error;
      const message = JSON.parse(error.message);
      alert(message.detail);
    },
  });

  const customHandleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    const role = isAcmChecked ? "ACM" : "missionary";
    handleSubmit(e, {
      body: {
        data: {
          question: input,
          role: role,
        },
      },
    });
  };

  return (
    <div className="w-full h-full flex flex-col space-y-2">
      {/* Message Area */}
      <div className="flex-grow overflow-y-auto flex flex-col justify-end bg-white rounded-lg shadow-xl">
        {messages.length === 0 && !isLoading ? (
          <DisclaimerMessage />
        ) : (
          <ChatMessages
            messages={messages}
            isLoading={isLoading}
            reload={reload}
            stop={stop}
            append={append}
          />
        )}
      </div>

      {/* ACM Checkbox */}
      <div className="flex items-center gap-2 text-xs border">
        <input
          id="acm-checkbox"
          type="checkbox"
          checked={isAcmChecked}
          onChange={(e) => setIsAcmChecked(e.target.checked)}
          className="w-4 h-4 border-2 border-black accent-black cursor-pointer"
        />
        <label htmlFor="acm-checkbox" className="font-medium select-none cursor-pointer">
          Answers for ACMs Only
        </label>
      </div>

      {/* Input Area */}
      <ChatInput
        input={input}
        handleSubmit={customHandleSubmit}
        handleInputChange={handleInputChange}
        isLoading={isLoading}
        messages={messages}
        append={append}
        setInput={setInput}
        requestParams={{ params: requestData }}
        setRequestData={setRequestData}
      />
    </div>
  );
}
