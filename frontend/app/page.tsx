import Header from "@/app/components/header";
import ChatSection from "./components/chat-section";
import Image from "next/image";

export default function Home() {
  return (
    <main className="h-dvh w-screen flex justify-center items-center background-gradient">
      <div className="space-y-2 lg:space-y-4 w-[90%] lg:w-[60rem]">
        <Header />
        <div className="h-[75dvh] flex pb-8">
          <ChatSection />
        </div>
        <div className="mt-5 pb-3 text-sm flex gap-4 justify-between items-start">
          <p>Powered by BYU-Pathway Software Development Students</p>
        </div>
      </div>
    </main>
  );
}
