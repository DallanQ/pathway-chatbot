import Header from "@/app/components/header";
import ChatSection from "./components/chat-section";

export default function Home() {
  return (
    <main className="h-dvh w-screen flex justify-center items-center background-gradient">
      <div className="space-y-2 lg:space-y-4 w-[90%] lg:w-[60rem]">
        <Header />
        <div className="h-[80dvh] flex pb-8">
          <ChatSection />
        </div>
        <p className="mt-5 text-sm">Powered by BYU-Pathway Software Development Students</p>
      </div>
    </main>
  );
}
