import { ExternalLink } from "lucide-react";
import { ThemeSwitcher } from "./theme-switcher";

export default function Header() {
  const hints = "https://missionaries.prod.byu-pathway.psdops.com/How-to-use-the-Missionary-Assistant"

  return (
    <header className="w-full bg-[#FFC328] px-4 sm:px-6 lg:px-8 shadow-none py-3">
      <div className="flex flex-col md:flex-row items-center justify-between w-full">
        <div className="flex items-center justify-between w-full md:w-auto">
          <div className="flex items-center">
            <img
              src="/pathway-horizontal-logo.png"
              alt="BYU Pathway Logo"
              className="w-[100px] h-auto md:w-[140px]"
            />
          </div>
          <div className="md:hidden flex items-center">
            <ThemeSwitcher />
            <a href={hints} target="_blank" className="text-[#454540] dark:text-black font-semibold flex items-center gap-1 text-sm hover:text-blue-700">
              <ExternalLink size={18} />
            </a>
          </div>
        </div>
        <div className="flex-1 text-center mt-2 md:mt-0 md:text-center">
          <span className="font-nunito text-base md:text-lg font-semibold text-[#454540] dark:text-black">Missionary Assistant</span>
        </div>
        <div className="hidden md:flex items-center gap-1">
            <ThemeSwitcher />
            <a href={hints} target="_blank" className="text-[#454540] dark:text-black font-semibold flex items-center gap-1 text-sm md:text-base hover:text-blue-700">
                <span className="hidden sm:inline">Help</span>
                <ExternalLink size={18} />
            </a>
        </div>
      </div>
    </header>
  );
}
