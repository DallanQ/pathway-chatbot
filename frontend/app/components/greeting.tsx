"use client";

import { useEffect, useState } from "react";

const WARM_TEXTS = [
  "Welcome!",
  "Need assistance?",
  "What can I do for you?",
  "What's on your mind?",
  "Need help?",
  "Hello, how can I support?",
  "Here to help!",
  "Need a hand?",
  "How's it going?",
  "Got questions?",
  "How can I assist?",
  "How can I serve you?",
  "What's up?",
];

const STORAGE_KEY = "chatbot_greeting_data";
const GREETING_VERSION = "2";

export default function Greeting() {
  const [greeting, setGreeting] = useState<string>("");
  const [mounted, setMounted] = useState(false);

  const getTimeBasedGreeting = () => {
    const hour = new Date().getHours();
    if (hour >= 5 && hour < 12) {
      return "Good morning!";
    } else if (hour >= 12 && hour < 18) {
      return "Good afternoon!";
    } else if (hour >= 18 && hour < 24) {
      return "Good evening!";
    } else {
      return "Good night!";
    }
  };

  const isWeekend = () => {
    const day = new Date().getDay();
    return day === 0 || day === 6; // 0 = Sunday, 6 = Saturday
  };

  useEffect(() => {
    setMounted(true);

    const shouldUpdateGreeting = (lastUpdated: number): boolean => {
      const now = Date.now();
      const timeDiff = now - lastUpdated;
      const minInterval = 30 * 60 * 1000; // 30 minutes
      const maxInterval = 120 * 60 * 1000; // 2 hours
      const randomInterval = Math.random() * (maxInterval - minInterval) + minInterval;
      return timeDiff > randomInterval;
    };

    const selectGreeting = () => {
      try {
        const stored = localStorage.getItem(STORAGE_KEY);
        const now = Date.now();
        const currentTimeGreeting = getTimeBasedGreeting();

        if (stored) {
          const data = JSON.parse(stored);
          
          if (data.version !== GREETING_VERSION) {
            localStorage.removeItem(STORAGE_KEY);
          } else {
            // Always prioritize time-based greeting if it has changed
            if (data.greeting !== currentTimeGreeting) {
              // Time of day changed, update to current time greeting
              localStorage.setItem(
                STORAGE_KEY,
                JSON.stringify({
                  greeting: currentTimeGreeting,
                  lastUpdated: now,
                  version: GREETING_VERSION,
                })
              );
              setGreeting(currentTimeGreeting);
              return;
            } else if (!shouldUpdateGreeting(data.lastUpdated)) {
              // Same time greeting and not time to update, keep stored greeting
              setGreeting(data.greeting);
              return;
            }
          }
        }

        let newGreeting: string;
        if (!stored) {
          // First visit - use time greeting, but check for weekend special
          if (isWeekend() && Math.random() < 0.7) {
            newGreeting = "Happy Weekend!";
          } else {
            newGreeting = currentTimeGreeting;
          }
        } else {
          // Check for weekend special greeting first
          if (isWeekend() && Math.random() < 0.7) {
            newGreeting = "Happy Weekend!";
          } else {
            const useTimeGreeting = Math.random() < 0.5;
            if (useTimeGreeting) {
              newGreeting = currentTimeGreeting;
            } else {
              const randomIndex = Math.floor(Math.random() * WARM_TEXTS.length);
              newGreeting = WARM_TEXTS[randomIndex];
            }
          }
        }

        localStorage.setItem(
          STORAGE_KEY,
          JSON.stringify({
            greeting: newGreeting,
            lastUpdated: now,
            version: GREETING_VERSION,
          })
        );

        setGreeting(newGreeting);
      } catch (error) {
        setGreeting(getTimeBasedGreeting());
      }
    };

    selectGreeting();
  }, []);

  // Prevent hydration mismatch by not rendering until client-side
  if (!mounted) {
    return (
      <div className="flex items-center justify-center px-4">
        <h1 className="font-georgia text-3xl sm:text-4xl md:text-[40px] text-[#3D3D3A] dark:text-[#C2C0B6] text-center leading-tight md:leading-[60px] invisible">
          Loading...
        </h1>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center px-4">
      <h1 className="font-georgia text-3xl sm:text-4xl md:text-[40px] text-[#3D3D3A] dark:text-[#C2C0B6] text-center leading-tight md:leading-[60px]">
        {greeting}
      </h1>
    </div>
  );
}