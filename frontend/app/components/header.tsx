import { ExternalLink } from "lucide-react";

export default function Header() {
  const hints = "https://missionaries.prod.byu-pathway.psdops.com/How-to-use-the-Missionary-Assistant"

  return (
    <header className="w-full bg-[#FFC328] px-3 md:px-6 shadow-none md:py-3">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between h-full py-2 md:py-0">
        <div className="w-full flex flex-row items-center justify-between md:justify-between md:w-full">
          <div className="flex items-center">
            <img 
              src="/pathway-horizontal-logo.png" 
              alt="BYU Pathway Logo" 
              className="w-[100px] h-auto md:w-[140px]"
            />
          </div>
          <span className="hidden md:block font-nunito text-lg font-semibold text-[#454540] text-center flex-1">Missionary Assistant</span>
          <a href={hints} target="_blank" className="text-[#454540] font-semibold flex items-center gap-1 text-sm md:text-base hover:text-blue-700">
            <span className="hidden md:inline">Hints</span>
            <ExternalLink size={18}/>
          </a>
        </div>
        <div className="w-full flex justify-center mt-1 md:hidden">
          <span className="font-nunito text-base font-semibold text-[#454540] text-center">Missionary Assistant</span>
        </div>
      </div>
    </header>
  );
}
