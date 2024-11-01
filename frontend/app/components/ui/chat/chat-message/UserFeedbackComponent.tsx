import { Button } from "../../button";
import { ThumbsDown, ThumbsUp } from "lucide-react";
import { useState } from "react";
import { FeedbackValue, sendUserFeedback } from "./thumb_request";
import { useClientConfig } from "../hooks/use-config";

export function UserFeedbackComponent(props: { traceId: string }) {
    const { backend = "" } = useClientConfig();

    const handleUserFeedback = async (traceId: string, value: FeedbackValue) => {
        await sendUserFeedback(backend, traceId, value);
    };

    const [ThumbsUpActive, setThumbsUpActive] = useState(false);
    const [ThumbsDownActive, setThumbsDownActive] = useState(false);

    return (
        <>
            <Button
                size="icon"
                variant="ghost"
                className="h-8 w-8 opacity-0 group-hover:opacity-100"
                onClick={() => {
                    setThumbsUpActive(!ThumbsUpActive);
                    setThumbsDownActive(false);
                    handleUserFeedback(props.traceId, !ThumbsUpActive ? FeedbackValue.GOOD : FeedbackValue.EMPTY);
                }}
            >
                <ThumbsUp fill={ThumbsUpActive ? "#111" : "none"} className="h-4 w-4" strokeWidth={ThumbsUpActive ? 0 : 2} />
            </Button>
            <Button
                size="icon"
                variant="ghost"
                className="h-8 w-8 opacity-0 group-hover:opacity-100"
                onClick={() => {
                    setThumbsDownActive(!ThumbsDownActive);
                    setThumbsUpActive(false);
                    handleUserFeedback(props.traceId, !ThumbsDownActive ? FeedbackValue.BAD : FeedbackValue.EMPTY);
                }}
            >
                <ThumbsDown fill={ThumbsDownActive ? "#111" : "none"} className="h-4 w-4" strokeWidth={ThumbsDownActive ? 0 : 2} />
            </Button>
        </>
    );
}
