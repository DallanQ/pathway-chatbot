import { JSONValue } from "ai";
import { isValidUrl } from "../lib/utils";
import ChatInput from "./chat-input";
import ChatMessages from "./chat-messages";

export { type ChatHandler } from "./chat.interface";
export { ChatInput, ChatMessages };

export enum MessageAnnotationType {
  IMAGE = "image",
  DOCUMENT_FILE = "document_file",
  SOURCES = "sources",
  EVENTS = "events",
  TOOLS = "tools",
  SUGGESTED_QUESTIONS = "suggested_questions",
  LANGFUSE_TRACE_ID = 'langfuse_trace_id',
}

export type ImageData = {
  url: string;
};

export type DocumentFileType = "csv" | "pdf" | "txt" | "docx";

export type DocumentFileContent = {
  type: "ref" | "text";
  value: string[] | string;
};

export type DocumentFile = {
  id: string;
  filename: string;
  filesize: number;
  filetype: DocumentFileType;
  content: DocumentFileContent;
};

export type DocumentFileData = {
  files: DocumentFile[];
};

export type SourceNode = {
  id: string;
  citation_node_id: string;
  metadata: Record<string, unknown>;
  score?: number;
  text: string;
  url: string;
};

export type SourceData = {
  nodes: SourceNode[];
};

export type EventData = {
  title: string;
  isCollapsed: boolean;
};

export type ToolData = {
  toolCall: {
    id: string;
    name: string;
    input: {
      [key: string]: JSONValue;
    };
  };
  toolOutput: {
    output: JSONValue;
    isError: boolean;
  };
};

export type SuggestedQuestionsData = string[];

export type AnnotationData =
  | ImageData
  | DocumentFileData
  | SourceData
  | EventData
  | ToolData
  | SuggestedQuestionsData;

export type MessageAnnotation = {
  type: MessageAnnotationType;
  data: AnnotationData;
  trace_id?: string;
};

const NODE_SCORE_THRESHOLD = 0.25;

export function getLangfuseTraceId(
  annotations: MessageAnnotation[],
  type: MessageAnnotationType
): any {
  return annotations.find((annotation) => annotation.type === type);
}

export function getAnnotationData<T extends AnnotationData>(
  annotations: MessageAnnotation[],
  type: MessageAnnotationType,
): T[] {
  return annotations.filter((a) => a.type === type).map((a) => a.data as T);
}

export function getSourceAnnotationData(
  annotations: MessageAnnotation[],
): SourceData[] {
  const data = getAnnotationData<SourceData>(
    annotations,
    MessageAnnotationType.SOURCES,
  );
  if (data.length > 0) {
    const sourceData = data[0] as SourceData;
    if (sourceData.nodes) {
      sourceData.nodes = preprocessSourceNodes(sourceData.nodes);
    }
  }
  return data;
}

function preprocessSourceNodes(nodes: SourceNode[]): SourceNode[] {
  // Filter source nodes has lower score
  nodes = nodes
    // .filter((node) => (node.score ?? 1) > NODE_SCORE_THRESHOLD)
    .filter((node) => isValidUrl(node.url))
    .sort((a, b) => (b.score ?? 1) - (a.score ?? 1))
    .map((node) => {
      // remove trailing slash for node url if exists
      node.url = node.url.replace(/\/$/, "");
      return node;
    });
  return nodes;
}
