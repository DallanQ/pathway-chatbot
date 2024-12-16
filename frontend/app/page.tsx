import Header from "@/app/components/header";
import ChatSection from "./components/chat-section";
import { ExternalLink } from "lucide-react";

export default function Home() {

  const hints = "https://missionaries.prod.byu-pathway.psdops.com/How-to-use-the-Missionary-Assistant"

  return (
    <main className="h-dvh w-screen flex justify-center items-center background-gradient">
      <div className="space-y-2 lg:space-y-4 w-[90%] lg:w-[60rem]">
        <Header />
        <div className="h-[80dvh] flex pb-8">
          <ChatSection />
        </div>
        <p className="mt-5 text-sm flex gap-4 justify-between">
          <span>Powered by BYU-Pathway Software Development Students</span><a href={hints} target="_blank" className="flex gap-1 text-blue-600 visited:text-purple-600">Hints <span><ExternalLink size={16}/></span></a>
        </p>
      </div>
    </main>
  );
}
