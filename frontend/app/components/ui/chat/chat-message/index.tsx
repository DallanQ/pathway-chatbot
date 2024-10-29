import { Check, Copy, ThumbsDown, ThumbsUp } from "lucide-react";
import { Message } from "ai";
import { Fragment, useEffect, useRef, useState } from "react";
import { Button } from "../../button";
import { useCopyToClipboard } from "../hooks/use-copy-to-clipboard";
import {
  ChatHandler,
  DocumentFileData,
  EventData,
  ImageData,
  MessageAnnotation,
  MessageAnnotationType,
  SuggestedQuestionsData,
  ToolData,
  getAnnotationData,
  getLangfuseTraceId,
  getSourceAnnotationData,
} from "../index";
import ChatAvatar from "./chat-avatar";
import { ChatEvents } from "./chat-events";
import { ChatFiles } from "./chat-files";
import { ChatImage } from "./chat-image";
import { ChatSources } from "./chat-sources";
import { SuggestedQuestions } from "./chat-suggestedQuestions";
import ChatTools from "./chat-tools";
import Markdown from "./markdown";
import { UserFeedbackComponent } from "./UserFeedbackComponent";

type ContentDisplayConfig = {
  order: number;
  component: JSX.Element | null;
};

function ChatMessageContent({
  message,
  isLoading,
  append,
  traceIdRef
}: {
  message: Message;
  isLoading: boolean;
  append: Pick<ChatHandler, "append">["append"];
  traceIdRef: React.MutableRefObject<string | null>;
}) {
  const annotations = message.annotations as MessageAnnotation[] | undefined;
  if (!annotations?.length) return <Markdown content={message.content} />;

  const imageData = getAnnotationData<ImageData>(
    annotations,
    MessageAnnotationType.IMAGE,
  );
  const contentFileData = getAnnotationData<DocumentFileData>(
    annotations,
    MessageAnnotationType.DOCUMENT_FILE,
  );
  const eventData = getAnnotationData<EventData>(
    annotations,
    MessageAnnotationType.EVENTS,
  );

  const sourceData = getSourceAnnotationData(annotations);

  const toolData = getAnnotationData<ToolData>(
    annotations,
    MessageAnnotationType.TOOLS,
  );
  const suggestedQuestionsData = getAnnotationData<SuggestedQuestionsData>(
    annotations,
    MessageAnnotationType.SUGGESTED_QUESTIONS,
  );

  const trace_id = getLangfuseTraceId(
    annotations,
    MessageAnnotationType.LANGFUSE_TRACE_ID,
  );

  useEffect(() => {
    console.log("trace_id: ", trace_id?.data);

    if (trace_id?.data) {
      traceIdRef.current = trace_id.data;
    }
  }, [message, traceIdRef]);

  const contents: ContentDisplayConfig[] = [
    {
      order: 1,
      component: imageData[0] ? <ChatImage data={imageData[0]} /> : null,
    },
    {
      order: -3,
      component:
        eventData.length > 0 ? (
          <ChatEvents isLoading={isLoading} data={eventData} />
        ) : null,
    },
    {
      order: 2,
      component: contentFileData[0] ? (
        <ChatFiles data={contentFileData[0]} />
      ) : null,
    },
    {
      order: -1,
      component: toolData[0] ? <ChatTools data={toolData[0]} /> : null,
    },
    {
      order: 0,
      component: <Markdown content={message.content} sources={sourceData[0]} />,
    },
    {
      order: 3,
      component: sourceData[0]
        && (!message.content.includes("Sorry, I'm not able to answer this question. Could you rephrase it?")
          && !message.content.includes("Sorry, I don't know."))
        ? <ChatSources data={sourceData[0]} />
        : null,
    },
    {
      order: 4,
      component: suggestedQuestionsData[0]
        && (!message.content.includes("Sorry, I'm not able to answer this question. Could you rephrase it?")
          && !message.content.includes("Sorry, I don't know."))
        ? (
          <SuggestedQuestions
            questions={suggestedQuestionsData[0]}
            append={append}
          />

        ) : null,
    },
    {
      order: 5,
      component: sourceData[0] ? <p>If I was unable to give you the information you needed, try searching the Missionary Services Site Index for your topic.  <a href="https://missionaries.prod.byu-pathway.psdops.com/missionary-services-site-index" target="_blank"
        rel="noopener noreferrer"
        className="text-blue-600 hover:underline">Site Index</a></p> : null,
    }
  ];

  return (
    <div className="flex-1 gap-4 flex flex-col">
      {contents
        .sort((a, b) => a.order - b.order)
        .map((content, index) => (
          <Fragment key={index}>{content.component}</Fragment>
        ))}
      <div>
      </div>
    </div>
  );
}

export default function ChatMessage({
  chatMessage,
  isLoading,
  append,
}: {
  chatMessage: Message;
  isLoading: boolean;
  append: Pick<ChatHandler, "append">["append"];
}) {

  const { isCopied, copyToClipboard } = useCopyToClipboard({ timeout: 2000 });
  const traceIdRef = useRef<string | null>(null);

  return (
    <div className="flex items-start gap-4 pr-5 pt-5">
      <ChatAvatar role={chatMessage.role} />
      <div className="group flex flex-1 justify-between gap-2">
        <ChatMessageContent
          message={chatMessage}
          isLoading={isLoading}
          append={append}
          traceIdRef={traceIdRef}
        />
        <div>
          <Button
            onClick={() => copyToClipboard(chatMessage.content)}
            size="icon"
            variant="ghost"
            className="h-8 w-8 opacity-0 group-hover:opacity-100"
          >
            {isCopied ? (
              <Check className="h-4 w-4" />
            ) : (
              <Copy className="h-4 w-4" />
            )}
          </Button>
          {
            chatMessage.role !== "user" && traceIdRef.current && (
              <UserFeedbackComponent traceId={traceIdRef.current} />
            )
          }
        </div>
      </div>
    </div>
  );
}