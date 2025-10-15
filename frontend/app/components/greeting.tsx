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
const GREETING_VERSION = "2"; // Increment this when greeting logic changes

export default function Greeting() {
  const [greeting, setGreeting] = useState("Good evening!");

  useEffect(() => {
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

    const shouldUpdateGreeting = (lastUpdated: number): boolean => {
      const now = Date.now();
      const timeDiff = now - lastUpdated;
      // Random interval between 30 minutes (1800000ms) and 2 hours (7200000ms)
      const minInterval = 30 * 60 * 1000; // 30 minutes
      const maxInterval = 120 * 60 * 1000; // 2 hours
      const randomInterval = Math.random() * (maxInterval - minInterval) + minInterval;
      return timeDiff > randomInterval;
    };

    const selectGreeting = () => {
      try {
        const stored = localStorage.getItem(STORAGE_KEY);
        const now = Date.now();

        if (stored) {
          const data = JSON.parse(stored);
          // Check version - if outdated, force refresh
          if (data.version !== GREETING_VERSION) {
            // Clear old data and continue to generate new greeting
            localStorage.removeItem(STORAGE_KEY);
          } else if (!shouldUpdateGreeting(data.lastUpdated)) {
            // Use the stored greeting if version matches and not expired
            setGreeting(data.greeting);
            return;
          }
        }

        // Time to select a new greeting
        // 60% chance for time-based greeting, 40% for warm text
        const useTimeGreeting = Math.random() < 0.6;
        
        let newGreeting: string;
        if (useTimeGreeting) {
          newGreeting = getTimeBasedGreeting();
        } else {
          // Select random warm text
          const randomIndex = Math.floor(Math.random() * WARM_TEXTS.length);
          newGreeting = WARM_TEXTS[randomIndex];
        }

        // Store the new greeting with timestamp
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
        // Fallback if localStorage is not available
        setGreeting(getTimeBasedGreeting());
      }
    };

    selectGreeting();
  }, []);

  return (
    <div className="flex items-center justify-center px-4">
      <h1 className="font-georgia text-3xl sm:text-4xl md:text-[40px] text-[#3D3D3A] dark:text-[#C2C0B6] text-center leading-tight md:leading-[60px]">
        {greeting}
      </h1>
    </div>
  );
}
