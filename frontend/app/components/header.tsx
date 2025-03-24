import { ExternalLink } from "lucide-react";

export default function Header() {

  const hints = "https://missionaries.prod.byu-pathway.psdops.com/How-to-use-the-Missionary-Assistant"

  return (
    <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm lg:flex">
      <div className="hidden md:block"></div>

      <div className="bottom-0 left-0 mb-4 h-auto w-full from-white via-white dark:from-black dark:via-black flex justify-center lg:static lg:w-auto bg-none lg:mb-0 lg:pl-6">
        <p className="font-nunito text-xl font-bold gap-2 text-center md:p-0">
          <span className="flex gap-4 text-center">Missionary Assistant </span>
        </p>
      </div>

      <a href={hints} target="_blank" className="text-sm flex items-center justify-self-end gap-1 text-blue-600 visited:text-purple-600">Hints <span><ExternalLink size={16}/></span></a>
    </div>
  );
}
