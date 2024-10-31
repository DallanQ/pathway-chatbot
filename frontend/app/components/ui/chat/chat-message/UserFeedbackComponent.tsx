import Langfuse from "langfuse";
import { Button } from "../../button";
import { ThumbsDown, ThumbsUp } from "lucide-react";
import { useState } from "react";

export function UserFeedbackComponent(props: { traceId: string }) {
    // console.log("Public Key:", process.env.NEXT_PUBLIC_LANGFUSE_PUBLIC_KEY);
    // console.log("Private Key:", process.env.NEXT_PUBLIC_LANGFUSE_PRIVATE_KEY);
    // console.log("API URL:", process.env.NEXT_PUBLIC_LANGFUSE_API_URL);

    const langfuse = new Langfuse({
        publicKey: process.env.NEXT_PUBLIC_LANGFUSE_PUBLIC_KEY,
        secretKey: process.env.NEXT_PUBLIC_LANGFUSE_PRIVATE_KEY,
        baseUrl: process.env.NEXT_PUBLIC_LANGFUSE_API_URL
    });

    const handleUserFeedback = async (value: string) => {
        // Fetch the trace
        const trace = await langfuse.fetchTrace(props.traceId);

        if (trace.data?.scores?.length) {
            const scoreId = trace.data?.scores[0].id;
            await langfuse.score({
                traceId: props.traceId,
                id: scoreId,
                name: "user_feedback",
                value: value
            });
        }
        else {
            await langfuse.score({
                traceId: props.traceId,
                name: "user_feedback",
                dataType: "CATEGORICAL",
                value,
            })

        }
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
                    handleUserFeedback(!ThumbsUpActive ? "Good" : "");
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
                    handleUserFeedback(!ThumbsDowmActive ? "Bad" : "");
                }}
            >
                <ThumbsDown fill={ThumbsDowmActive ? "#111" : "none"} className="h-4 w-4" strokeWidth={ThumbsDowmActive ? 0 : 2} />
            </Button>
        </>
    );
}
