import { ExternalLink } from "lucide-react";

export default function Header() {

  const hints = "https://missionaries.prod.byu-pathway.psdops.com/How-to-use-the-Missionary-Assistant"

  return (
    <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm lg:flex">
      {/* <p className="fixed left-0 top-0 flex w-full justify-center border-b border-gray-300 bg-gradient-to-b from-zinc-200 pb-6 pt-8 backdrop-blur-2xl dark:border-neutral-800 dark:bg-zinc-800/30 dark:from-inherit lg:static lg:w-auto  lg:rounded-xl lg:border lg:bg-gray-200 lg:p-4 lg:dark:bg-zinc-800/30">
        Get started by editing&nbsp;
        <code className="font-mono font-bold">app/page.tsx</code>
      </p> */}
      <div className="bottom-0 left-0 mb-4 h-auto w-full from-white via-white dark:from-black dark:via-black lg:static lg:w-auto bg-none lg:mb-0">
        <p
          className="font-nunito text-xl font-bold gap-2 pY-7 md:p-0"
        >
          <span className="flex gap-4">Missionary Assistant </span>
          {/* <Image
            className="rounded-xl"
            src="/llama.png"
            alt="Llama Logo"
            width={40}
            height={40}
            priority
          /> */}
        </p>
      </div>
      <a href={hints} target="_blank" className="text-sm flex items-center gap-1 text-blue-600 visited:text-purple-600">Hints <span><ExternalLink size={16}/></span></a>
    </div>
  );
}
