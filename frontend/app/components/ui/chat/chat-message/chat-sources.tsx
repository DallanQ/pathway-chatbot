import { Check, Copy, FileText, ChevronDown } from "lucide-react";
import Image from "next/image";
import { useMemo, useState } from "react";
import { Button } from "../../button";
import { FileIcon } from "../../document-preview";
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "../../hover-card";
import { cn } from "../../lib/utils";
import { useCopyToClipboard } from "../hooks/use-copy-to-clipboard";
import { DocumentFileType, SourceData, SourceNode } from "../index";
import PdfDialog from "../widgets/PdfDialog";

type Document = {
  url: string;
  sources: SourceNode[];
};

export function ChatSources({ data }: { data: SourceData }) {
  const [isExpanded, setIsExpanded] = useState(false);
  
  const documents: Document[] = useMemo(() => {
    // group nodes by document (a document must have a URL)
    // Information source
    const nodesByUrl: Record<string, SourceNode[]> = {};
    
    data.nodes.forEach((node) => {
      const key = node.url;
      nodesByUrl[key] ??= [];
      nodesByUrl[key].push(node);
    });

    // convert to array of documents
    return Object.entries(nodesByUrl).map(([url, sources]) => ({
      url,
      sources,
    }));
  }, [data.nodes]);

  if (documents.length === 0) return null;

  const sortedSources = documents
  .flatMap(document => document.sources)
  .sort((a, b) => {
      const getNumber = (url: string) => parseInt(url.match(/^\d+/)?.[0] || '0', 10);
      return getNumber(a.citation_node_id) - getNumber(b.citation_node_id);
  });

  return (
    <div className="mt-4">
      {/* Reference badges with favicons - clickable to expand/collapse */}
      <button 
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center gap-2 bg-[rgba(219,219,219,0.08)] border border-[rgba(219,219,219,0.04)] rounded-full px-3 py-2 hover:bg-[rgba(219,219,219,0.12)] transition-colors"
      >
        {/* Favicon icons */}
        <div className="flex items-center -space-x-2">
          {sortedSources.slice(0, 3).map((node: SourceNode, index: number) => {
            const domain = new URL(node.url).hostname;
            return (
              <div 
                key={index}
                className="w-4 h-4 rounded-full bg-[#36383a] border border-[#161618] overflow-hidden flex items-center justify-center"
              >
                <Image
                  src={`https://www.google.com/s2/favicons?domain=${domain}&sz=16`}
                  alt={domain}
                  width={16}
                  height={16}
                  className="w-full h-full object-cover"
                />
              </div>
            );
          })}
        </div>
        <span className="text-[#FCFCFC] text-[13.781px] leading-[21px] tracking-[-0.1px]">
          {sortedSources.length} references
        </span>
        <ChevronDown 
          className={cn(
            "w-4 h-4 text-[#B5B5B5] transition-transform duration-300",
            isExpanded && "rotate-180"
          )}
        />
      </button>
      
      {/* Expandable list with smooth animation */}
      <div 
        className={cn(
          "overflow-hidden transition-all duration-300 ease-in-out",
          isExpanded ? "max-h-[500px] opacity-100 mt-2" : "max-h-0 opacity-0"
        )}
      >
        <div className="space-y-1 pt-2">
          {sortedSources.map((node: SourceNode, index: number) => (
            <a
              key={index}
              href={node.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-start gap-2 text-sm text-[#F9F8F6] py-1 group"
            >
              <span className="text-[#E18158] font-medium whitespace-nowrap flex-shrink-0">^{index + 1}</span>
              <span className="break-all hover:underline">{node.url}</span>
            </a>
          ))}
        </div>
      </div>
    </div>
  );
  
}

export function SourceInfo({
  node,
  index,
}: {
  node?: SourceNode;
  index: number;
}) {
  if (!node) return <SourceNumberButton index={index} />;
  return (
    <HoverCard>
      <HoverCardTrigger
        className="cursor-default"
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
        }}
      >
        <SourceNumberButton
          index={index}
          className="hover:text-white hover:bg-primary"
        />
      </HoverCardTrigger>
      <HoverCardContent className="w-[400px]">
        <NodeInfo nodeInfo={node} />
      </HoverCardContent>
    </HoverCard>
  );
}

export function SourceNumberButton({
  index,
  className,
}: {
  index: number;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center justify-center px-2 rounded-full bg-[#242628] text-[#E18158] text-[8px] leading-[13px] font-medium align-super",
        className,
      )}
    >
      ^{index + 1}
    </span>
  );
}

// Information source

function DocumentInfo({ document }: { document: Document }) {
  if (!document.sources.length) return null;
  const { url, sources } = document;
  const fileName = sources[0].metadata.file_name as string | undefined;
  const fileExt = fileName?.split(".").pop();
  const fileImage = fileExt ? FileIcon[fileExt as DocumentFileType] : null;

  console.log("DocumentInfo")
  const DocumentDetail = (
    <div
      key={url}
      className="h-28 w-48 flex flex-col justify-between p-4 border rounded-md shadow-md cursor-pointer"
    >
      <p
        title={fileName}
        className={cn(
          fileName ? "truncate" : "text-blue-900 break-words",
          "text-left",
        )}
      >
        {fileName ?? url}
      </p>
      <div className="flex justify-between items-center">
        <div className="space-x-2 flex">
          {sources.map((node: SourceNode, index: number) => {
            return (
              <div key={node.id}>
                <SourceInfo node={node} index={index} />
              </div>
            );
          })}
        </div>
        {fileImage ? (
          <div className="relative h-8 w-8 shrink-0 overflow-hidden rounded-md">
            <Image
              className="h-full w-auto"
              priority
              src={fileImage}
              alt="Icon"
            />
          </div>
        ) : (
          <FileText className="text-gray-500" />
        )}
      </div>
    </div>
  );

  if (url.endsWith(".pdf")) {
    // open internal pdf dialog for pdf files when click document card
    return <PdfDialog documentId={url} url={url} trigger={DocumentDetail} />;
  }
  // open external link when click document card for other file types
  return <div onClick={() => window.open(url, "_blank")}>{DocumentDetail}</div>;
}

function NodeInfo({ nodeInfo }: { nodeInfo: SourceNode }) {
  const { isCopied, copyToClipboard } = useCopyToClipboard({ timeout: 1000 });

  const pageNumber =
    // XXX: page_label is used in Python, but page_number is used by Typescript
    (nodeInfo.metadata?.page_number as number) ??
    (nodeInfo.metadata?.page_label as number) ??
    null;

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <span className="font-semibold">
          {pageNumber ? `On page ${pageNumber}:` : "Node content:"}
        </span>
        {nodeInfo.text && (
          <Button
            onClick={(e) => {
              e.stopPropagation();
              copyToClipboard(nodeInfo.text);
            }}
            size="icon"
            variant="ghost"
            className="h-12 w-12 shrink-0"
          >
            {isCopied ? (
              <Check className="h-4 w-4" />
            ) : (
              <Copy className="h-4 w-4" />
            )}
          </Button>
        )}
      </div>

      {nodeInfo.text && (
        <pre className="max-h-[200px] overflow-auto whitespace-pre-line">
          &ldquo;{nodeInfo.text}&rdquo;
        </pre>
      )}
    </div>
  );
}
