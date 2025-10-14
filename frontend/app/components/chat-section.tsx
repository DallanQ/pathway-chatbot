"use client";

import { useChat } from "ai/react";
import { useState, useEffect } from "react";
import DisclaimerMessage from "./disclaimer-message";
import Greeting from "./greeting";
import { ChatInput, ChatMessages } from "./ui/chat";
import { useClientConfig } from "./ui/chat/hooks/use-config";

export default function ChatSection() {
  const { backend } = useClientConfig();
  const [requestData, setRequestData] = useState<any>();
  const [isAcmChecked, setIsAcmChecked] = useState(false);
  const [hasStartedChat, setHasStartedChat] = useState(false);
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
    const data = {
      question: input,
      role: role,
    };
    setRequestData(data);
    
    // Mark chat as started on first message
    if (!hasStartedChat) {
      setHasStartedChat(true);
    }
    
    handleSubmit(e, {
      body: {
        data: data,
      },
    });
  };

  // Check if there are any messages
  const hasMessages = messages.length > 0;

  return (
    <div className="w-full h-full flex flex-col relative">
      {/* Empty state - centered */}
      {!hasStartedChat && !hasMessages && (
        <div className="flex-1 flex items-center justify-center px-4">
          <div className="w-full max-w-[672px] flex flex-col items-center gap-8">
            <Greeting />
            <DisclaimerMessage />
          </div>
        </div>
      )}

      {/* Chat messages - takes remaining space */}
      {(hasStartedChat || hasMessages) && (
        <div className="flex-1 overflow-y-auto px-4 md:px-16 lg:px-24 pt-8">
          <div className="max-w-[640px] mx-auto">
            <ChatMessages
              messages={messages}
              isLoading={isLoading}
              reload={reload}
              stop={stop}
              append={append}
            />
          </div>
        </div>
      )}

      {/* Input area - positioned based on chat state */}
      <div 
        className={`w-full px-4 sm:px-6 md:px-16 lg:px-24 pb-2 transition-all duration-500 ease-in-out ${
          !hasStartedChat && !hasMessages ? 'static' : 'sticky bottom-0'
        }`}
      >
        <div className="max-w-[672px] mx-auto space-y-2">
          {/* Input with ACM Toggle inside */}
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
            isAcmMode={isAcmChecked}
            isAcmChecked={isAcmChecked}
            setIsAcmChecked={setIsAcmChecked}
          />
          
          {/* Disclaimer under input */}
          <div className="px-2">
            <p className="text-[9px] sm:text-[10px] leading-[12px] sm:leading-[14px] text-red-500 dark:text-red-400">
              <span className="font-bold">IMPORTANT:</span> <span className="font-medium opacity-80 font-[11px]">This website is intended for missionaries assigned to BYU-Pathway only — not for student use. Please direct students to the Companion app in their portal. We ask that you do not share or promote this site on social media. Thank you for respecting this guideline.</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
