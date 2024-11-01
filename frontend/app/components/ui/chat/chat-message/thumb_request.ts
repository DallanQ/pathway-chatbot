export enum FeedbackValue {
    EMPTY = '',
    GOOD = 'Good',
    BAD = 'Bad',
}

export const useSendUserFeedback = async (backend: string, traceId: string, value: FeedbackValue) => {
    const uploadAPI = `${backend}/api/chat/thumbs_request`;
    try {
        const body = {
            trace_id: traceId,
            value: value
        }

        const response = await fetch(uploadAPI, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            throw new Error("Failed to send feedback");
        }

        const data = await response.json();
        console.log("Feedback response:", data);
    } catch (error) {
        console.error("Error sending feedback:", error);
    }
}