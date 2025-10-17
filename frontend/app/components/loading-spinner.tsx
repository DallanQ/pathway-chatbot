"use client";

import { useEffect, useState } from "react";

export default function LoadingSpinner() {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-[#FAF9F5] dark:bg-[#262624] z-50">
      <div className="flex flex-col items-center gap-4">
        <div className="relative">
          <div className="w-12 h-12 border-4 border-[#3D3D3A]/20 dark:border-[#C2C0B6]/20 border-t-[#3D3D3A] dark:border-t-[#C2C0B6] rounded-full animate-spin"></div>
        </div>
        <p className="text-sm text-[#3D3D3A]/60 dark:text-[#C2C0B6]/60 font-medium">
          Loading...
        </p>
      </div>
    </div>
  );
}

export function AppLoader({ children }: { children: React.ReactNode }) {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Wait for theme to be applied and components to be ready
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 800); // Minimum loading time to ensure smooth transition

    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return <>{children}</>;
}