import Header from "@/app/components/header";
import ChatSection from "./components/chat-section";

export default function Home() {
  return (
    <main className="h-dvh w-screen flex flex-col bg-white dark:bg-[#262624]">
      <Header />
      <div className="flex-1 flex flex-col overflow-hidden">
        <ChatSection />
      </div>
    </main>
  );
}
