"use client";

import { useEffect, useState } from "react";

export default function Greeting() {
  const [greeting, setGreeting] = useState("Good evening!");

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour >= 5 && hour < 12) {
      setGreeting("Good morning!");
    } else if (hour >= 12 && hour < 18) {
      setGreeting("Good afternoon!");
    } else {
      setGreeting("Good evening!");
    }
  }, []);

  return (
    <div className="flex items-center justify-center px-4">
      <h1 className="font-georgia text-3xl sm:text-4xl md:text-[40px] text-[#C2C0B6] text-center leading-tight md:leading-[60px]">
        {greeting}
      </h1>
    </div>
  );
}
