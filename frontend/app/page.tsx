import Header from "@/app/components/header";
import ChatSection from "./components/chat-section";
import Image from "next/image";

export default function Home() {
  return (
    <main className="h-dvh w-screen flex justify-center items-center background-gradient">
      <div className="w-[90%] lg:w-[60rem]">
        <Header />
        <div className="h-[75dvh] flex pb-8">
          <ChatSection />
        </div>
        <div className="mt-5 pb-3 text-sm flex gap-4 justify-between items-start">
          <p className="text-red-500">IMPORTANT: This website is intended for missionaries assigned to BYU-Pathway and is not for student use. Encourage students to use the Companion app found in their student portal. We ask that you do not share or promote on social media.  Thank you for respecting this guideline.
          </p>
        </div>
      </div>
    </main>
  );
}
