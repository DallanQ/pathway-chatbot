import { ExternalLink } from "lucide-react";

export default function Header() {
  const hints = "https://missionaries.prod.byu-pathway.psdops.com/How-to-use-the-Missionary-Assistant"

  return (
    <header className="w-full h-[60px] bg-[#FFC328] flex items-center justify-between px-6 shadow-none">
      <div className="flex items-center h-full">
        <img 
          src="/pathway-horizontal-logo.png" 
          alt="BYU Pathway Logo" 
          width={140}
          height={40}
        />
      </div>
      <div className="flex-1 flex justify-center items-center h-full">
        <span className="font-nunito text-lg font-semibold text-[#454540]">Missionary Assistant</span>
      </div>
      <div className="flex items-center h-full">      
        <a href={hints} target="_blank" className="text-base flex items-center gap-1 text-black hover:text-blue-700 font-semibold">Hints <ExternalLink size={16}/></a>
      </div>
    </header>
  );
}
