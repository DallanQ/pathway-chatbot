import Image from "next/image";
import { HelpCircle } from "lucide-react";
import { ThemeSwitcher } from "./theme-switcher";

export default function Header() {
  const hints = "https://missionaries.prod.byu-pathway.psdops.com/How-to-use-the-Missionary-Assistant"

  return (
    <header className="w-full bg-[#FFC328] px-4 sm:px-6 py-3 flex-shrink-0">
      <div className="flex items-center justify-between w-full relative">
        {/* Logo */}
        <div className="flex items-center z-10">
          <a href="/" className="cursor-pointer">
            <Image
              src="/pathway-horizontal-logo.png"
              alt="BYU Pathway Logo"
              width={140}
              height={18}
              className="h-[16px] sm:h-[18px] w-auto"
            />
          </a>
        </div>
        
        {/* Title - centered */}
        <div className="absolute left-1/2 transform -translate-x-1/2">
          <h1 className="font-semibold text-base sm:text-[18px] text-[#454540] whitespace-nowrap">
            Missionary Assistant
          </h1>
        </div>
        
        {/* Right side - Theme switcher and Help */}
        <div className="flex items-center gap-1 sm:gap-2 z-10">
          <ThemeSwitcher />
          <a 
            href={hints} 
            target="_blank" 
            rel="noopener noreferrer"
            className="hidden sm:flex items-center gap-1 px-4 py-2 rounded-full border border-black/50 text-[#646362] hover:bg-black/5 transition-colors"
          >
            <HelpCircle className="h-4 w-4" />
            <span className="text-sm font-semibold">Help</span>
          </a>
          {/* Mobile Help - icon only */}
          <a 
            href={hints} 
            target="_blank" 
            rel="noopener noreferrer"
            className="sm:hidden p-2 rounded-full border border-black/50 text-[#646362] hover:bg-black/5 transition-colors"
            aria-label="Help"
          >
            <svg width="16" height="16" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M10 0C4.477 0 0 4.477 0 10s4.477 10 10 10 10-4.477 10-10S15.523 0 10 0zm0 18c-4.411 0-8-3.589-8-8s3.589-8 8-8 8 3.589 8 8-3.589 8-8 8zm0-14a4 4 0 00-4 4h2a2 2 0 114 0c0 2-3 1.75-3 5h2c0-2.25 3-2.5 3-5a4 4 0 00-4-4zm-1 10h2v2H9v-2z" fill="currentColor"/>
            </svg>
          </a>
        </div>
      </div>
    </header>
  );
}
