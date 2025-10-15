import Image from "next/image";
import { HelpCircle } from "lucide-react";
import { ThemeSwitcher } from "./theme-switcher";
import { MobileSettings } from "./mobile-settings";

export default function Header() {
  const hints = "https://missionaries.prod.byu-pathway.psdops.com/How-to-use-the-Missionary-Assistant"

  return (
    <header className="w-full bg-[#FFC328] px-4 sm:px-6 pb-2 pt-0 min-[480px]:pt-2 min-[480px]:pb-2 flex-shrink-0">
      {/* Container for screens >= 480px - single row layout */}
      <div className="hidden min-[480px]:flex items-center justify-between w-full relative min-h-[40px]">
        {/* Logo */}
        <div className="flex items-center z-10">
          <a href="/" className="cursor-pointer">
            <Image
              src="/pathway-horizontal-logo.png"
              alt="BYU Pathway Logo"
              width={140}
              height={18}
              className="h-[15px] sm:h-[16px] w-auto"
            />
          </a>
        </div>
        
        {/* Title - centered */}
        <div className="absolute left-1/2 transform -translate-x-1/2">
          <h1 className="font-semibold text-[18px] md:text-xl text-[#454540] whitespace-nowrap">
            Missionary Assistant
          </h1>
        </div>
        
        {/* Right side - Theme switcher and Help (Desktop) / Settings (Mobile) */}
        <div className="flex items-center gap-1 sm:gap-2 z-10">
          {/* Desktop: Theme Switcher */}
          <div className="hidden sm:block">
            <ThemeSwitcher />
          </div>
          
          {/* Desktop: Help Button */}
          <a 
            href={hints} 
            target="_blank" 
            rel="noopener noreferrer"
            className="hidden sm:flex items-center gap-1 px-3 py-1.5 rounded-full border border-black/50 text-[#646362] hover:bg-black/5 transition-colors"
            title="Get help and learn how to use the Missionary Assistant"
          >
            <HelpCircle className="h-4 w-4" />
            <span className="text-sm font-semibold">Help</span>
          </a>
          
          {/* Mobile: Settings Gear Icon with Dialog */}
          <MobileSettings />
        </div>
      </div>

      {/* Container for screens < 480px - wrapped layout */}
      <div className="min-[480px]:hidden relative -ml-2">
        {/* Logo - top left */}
        <a href="/" className="cursor-pointer inline-block">
          <Image
            src="/pathway-horizontal-logo.png"
            alt="BYU Pathway Logo"
            width={140}
            height={18}
            className="h-[14px] w-auto"
          />
        </a>
        
        {/* Settings Icon - absolute positioned, vertically centered */}
        <div className="absolute right-0 top-1/2 -translate-y-1/2 z-50">
          <MobileSettings />
        </div>
        
        {/* Title - below logo */}
        <div className="w-full mt-1.5">
          <h1 className="font-semibold text-[18px] text-[#454540] -mt-2 text-center leading-tight">
            Missionary Assistant
          </h1>
        </div>
      </div>
    </header>
  );
}
