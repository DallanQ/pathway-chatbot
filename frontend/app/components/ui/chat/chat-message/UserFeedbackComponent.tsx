import { LangfuseWeb } from "langfuse";
import { Button } from "../../button";
import { ThumbsDown, ThumbsUp } from "lucide-react";
import { useState } from "react";

export function UserFeedbackComponent(props: { traceId: string }) {

    const langfuseWeb = new LangfuseWeb({
        publicKey: process.env.NEXT_PUBLIC_LANGFUSE_PUBLIC_KEY,
    });

    const handleUserFeedback = async (value: number) => {

        console.log("traceId: ", props.traceId);

        await langfuseWeb.score({
            traceId: props.traceId,
            name: "user_feedback",
            value,
        })
    };
    const [ThumbsUpActive, setThumbsUpActive] = useState(false);
    const [ThumbsDowmActive, setThumbsDownActive] = useState(false);

    return (
        <>
            <Button
                size="icon"
                variant="ghost"
                className="h-8 w-8 opacity-0 group-hover:opacity-100"
                onClick={() => {
                    setThumbsUpActive(!ThumbsUpActive);
                    setThumbsDownActive(false);
                    handleUserFeedback(1);
                }}
            >
                <ThumbsUp fill={ThumbsUpActive ? "#111" : "none"} className="h-4 w-4" strokeWidth={ThumbsUpActive ? 0 : 2} />
            </Button>
            <Button
                size="icon"
                variant="ghost"
                className="h-8 w-8 opacity-0 group-hover:opacity-100"
                onClick={() => {
                    setThumbsDownActive(!ThumbsDowmActive);
                    setThumbsUpActive(false);
                    handleUserFeedback(0);
                }}
            >
                <ThumbsDown fill={ThumbsDowmActive ? "#111" : "none"} className="h-4 w-4" strokeWidth={ThumbsDowmActive ? 0 : 2} />
            </Button>
        </>
    );
}

// <>
//   <Button
//     size="icon"
//     variant="ghost"
//     className="h-8 w-8 opacity-0 group-hover:opacity-100"
//     onClick={() => {
//       setThumbsUpActive(!ThumbsUpActive);
//       setThumbsDownActive(false);
//     }}
//   >
//     <ThumbsUp fill={ThumbsUpActive ? "#111": "none"} className="h-4 w-4" strokeWidth={ThumbsUpActive ? 0 : 2} />
//   </Button>
//   <Button
//     size="icon"
//     variant="ghost"
//     className="h-8 w-8 opacity-0 group-hover:opacity-100"
//     onClick={() => {
//       setThumbsDownActive(!ThumbsDowmActive);
//       setThumbsUpActive(false);
//     }}
//   >
//     <ThumbsDown fill={ThumbsDowmActive ? "#111": "none"} className="h-4 w-4" strokeWidth={ThumbsDowmActive ? 0 : 2} />
//   </Button>
// </>