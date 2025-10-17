"use client";

import { useEffect, useState } from "react";

// Array of friendly, casual greetings to randomly display to users
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

// LocalStorage key to persist greeting state across sessions
const STORAGE_KEY = "chatbot_greeting_data";
// Version number to invalidate old greeting data when logic changes
const GREETING_VERSION = "3";

export default function Greeting() {
  const [greeting, setGreeting] = useState<string>("");
  // Track if component has mounted to prevent hydration mismatch
  const [mounted, setMounted] = useState(false);

  // Returns appropriate greeting based on current time of day
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

  // Check if today is Saturday or Sunday
  const isWeekend = () => {
    const day = new Date().getDay();
    return day === 0 || day === 6; // 0 = Sunday, 6 = Saturday
  };

  useEffect(() => {
    setMounted(true);

    // Determines if enough time has passed to show a new greeting
    // Uses a random interval between 30 minutes and 2 hours to keep greetings fresh
    const shouldUpdateGreeting = (lastUpdated: number): boolean => {
      const now = Date.now();
      const timeDiff = now - lastUpdated;
      const minInterval = 30 * 60 * 1000; // 30 minutes
      const maxInterval = 120 * 60 * 1000; // 2 hours
      const randomInterval = Math.random() * (maxInterval - minInterval) + minInterval;
      return timeDiff > randomInterval;
    };

    // Main logic to select and display the appropriate greeting
    const selectGreeting = () => {
      try {
        const stored = localStorage.getItem(STORAGE_KEY);
        const now = Date.now();
        const currentTimeGreeting = getTimeBasedGreeting();

        if (stored) {
          const data = JSON.parse(stored);
          
          // Clear old data if version has changed
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
          // Subsequent visits - vary the greeting
          // 70% chance of weekend greeting if it's Saturday/Sunday
          if (isWeekend() && Math.random() < 0.7) {
            newGreeting = "Happy Weekend!";
          } else {
            // 50/50 split between time-based and casual greetings
            const useTimeGreeting = Math.random() < 0.5;
            if (useTimeGreeting) {
              newGreeting = currentTimeGreeting;
            } else {
              // Pick a random casual greeting from WARM_TEXTS array
              const randomIndex = Math.floor(Math.random() * WARM_TEXTS.length);
              newGreeting = WARM_TEXTS[randomIndex];
            }
          }
        }

        // Save the selected greeting to localStorage with timestamp
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
        // Fallback to time-based greeting if localStorage fails
        setGreeting(getTimeBasedGreeting());
      }
    };

    selectGreeting();
  }, []);

  // Prevent hydration mismatch by not rendering greeting until component mounts on client-side
  // This ensures server-rendered HTML matches client-rendered HTML
  if (!mounted) {
    return (
      <div className="flex items-center justify-center px-4">
        <h1 className="font-georgia text-3xl sm:text-4xl md:text-[40px] text-[#3D3D3A] dark:text-[#C2C0B6] text-center leading-tight md:leading-[60px] invisible">
          Loading...
        </h1>
      </div>
    );
  }

  // Display the selected greeting with responsive typography
  return (
    <div className="flex items-center justify-center px-4">
      <h1 className="font-georgia text-3xl sm:text-4xl md:text-[40px] text-[#3D3D3A] dark:text-[#C2C0B6] text-center leading-tight md:leading-[60px]">
        {greeting}
      </h1>
    </div>
  );
}