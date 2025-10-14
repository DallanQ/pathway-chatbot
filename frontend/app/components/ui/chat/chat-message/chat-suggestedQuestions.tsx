import { useState } from "react";
import { CornerDownRight } from "lucide-react";
import { ChatHandler, SuggestedQuestionsData } from "..";

export function SuggestedQuestions({
  questions,
  append,
}: {
  questions: SuggestedQuestionsData;
  append: Pick<ChatHandler, "append">["append"];
}) {
  const [showQuestions, setShowQuestions] = useState(questions.length > 0);

  return (
    showQuestions &&
    append !== undefined && (
      <div className="flex flex-col space-y-2 ml-3 mt-6">
        {questions.map((question, index) => (
          <a
            key={index}
            onClick={() => {
              append({ role: "user", content: question });
              setShowQuestions(false);
            }}
            className="flex items-center italic gap-2 text-sm text-[#F9F8F6] hover:text-[#FCFCFC] cursor-pointer group"
          >
            <CornerDownRight className="h-4 w-4 text-[#B5B5B5] group-hover:text-[#FCFCFC] transition-colors flex-shrink-0" />
            <span>{question}</span>
          </a>
        ))}
      </div>
    )
  );
}
