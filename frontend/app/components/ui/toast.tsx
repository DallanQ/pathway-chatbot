"use client";

import { useEffect, useState } from "react";
import { Check } from "lucide-react";

interface ToastProps {
  message: string;
  show: boolean;
  onClose: () => void;
}

export function Toast({ message, show, onClose }: ToastProps) {
  useEffect(() => {
    if (show) {
      const timer = setTimeout(() => {
        onClose();
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [show, onClose]);

  if (!show) return null;

  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 md:left-auto md:right-6 md:translate-x-0 z-50 animate-in slide-in-from-bottom-5 duration-300">
      <div className="flex items-center gap-2 bg-[#242628] dark:bg-[#2a2c2e] border border-[rgba(252,252,252,0.1)] rounded-lg px-4 py-3 shadow-lg whitespace-nowrap">
        <Check className="h-4 w-4 text-green-500 flex-shrink-0" />
        <p className="text-sm text-[#FCFCFC] whitespace-nowrap">{message}</p>
      </div>
    </div>
  );
}

export function useToast() {
  const [show, setShow] = useState(false);
  const [message, setMessage] = useState("");

  const showToast = (msg: string) => {
    setMessage(msg);
    setShow(true);
  };

  const hideToast = () => {
    setShow(false);
  };

  return { show, message, showToast, hideToast };
}
