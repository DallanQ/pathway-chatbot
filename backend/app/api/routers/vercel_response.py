import json

from aiostream import stream
from fastapi import Request
from fastapi.responses import StreamingResponse
from llama_index.core.chat_engine.types import StreamingAgentChatResponse

from app.api.routers.events import EventCallbackHandler
from app.api.routers.models import ChatData, Message, SourceNodes
from app.api.services.suggestion import NextQuestionSuggestion
import time


class VercelStreamResponse(StreamingResponse):
    """
    Class to convert the response from the chat engine to the streaming format expected by Vercel
    """

    TEXT_PREFIX = "0:"
    DATA_PREFIX = "8:"

    @classmethod
    def convert_text(cls, token: str):
        # Escape newlines and double quotes to avoid breaking the stream
        token = json.dumps(token)
        return f"{cls.TEXT_PREFIX}{token}\n"

    @classmethod
    def convert_data(cls, data: dict):
        data_str = json.dumps(data)
        return f"{cls.DATA_PREFIX}[{data_str}]\n"

    def __init__(
        self,
        request: Request,
        event_handler: EventCallbackHandler,
        response: StreamingAgentChatResponse,
        chat_data: ChatData,
        tokens: list,
        trace_id: str | None = None,
        skip_suggestions: bool = False,
        user_language: str | None = None
    ):
        content = VercelStreamResponse.content_generator(
            request, event_handler, response, chat_data, tokens, trace_id, skip_suggestions, user_language
        )
        super().__init__(content=content)

    @classmethod
    async def content_generator(
        cls,
        request: Request,
        event_handler: EventCallbackHandler,
        response: StreamingAgentChatResponse,
        chat_data: ChatData,
        tokens: list,
        trace_id: str | None = None,
        skip_suggestions: bool = False,
        user_language: str | None = None
    ):
        # Yield the text response
        async def _chat_response_generator():
            final_response = ""
            for token in tokens:
                final_response += token
                time.sleep(0.02)
                yield VercelStreamResponse.convert_text(token)

            
            # Generate questions that user might interested to (skip for security-blocked responses)
            if not skip_suggestions:
                conversation = chat_data.messages + [
                    Message(role="assistant", content=final_response, trace_id=trace_id)
                    # Message(role="assistant", content=final_response)
                ]
                questions = await NextQuestionSuggestion.suggest_next_questions(
                    conversation
                )
                if len(questions) > 0:
                    yield VercelStreamResponse.convert_data(
                        {
                            "type": "suggested_questions",
                            "data": questions,
                            "trace_id": trace_id
                        }
                    )

            # the text_generator is the leading stream, once it's finished, also finish the event stream
            event_handler.is_done = True

            # Yield user language for frontend localization
            if user_language:
                yield cls.convert_data(
                    {
                        "type": "user_language",
                        "data": {"language": user_language},
                        "trace_id": trace_id,
                    }
                )

            # Yield the source nodes
            yield cls.convert_data(
                {
                    "type": "sources",
                    "data": {
                        "nodes": [
                            SourceNodes.from_source_node(node).model_dump()
                            for node in response.source_nodes
                        ]
                    },
                    "trace_id": trace_id,
                }
            )

        # Yield the events from the event handler
        async def _event_generator():
            async for event in event_handler.async_event_gen():
                event_response = event.to_response()
                if event_response is not None:
                    event_response["trace_id"] = trace_id
                    yield VercelStreamResponse.convert_data(event_response)

        combine = stream.merge(_chat_response_generator(), _event_generator())
        is_stream_started = False
        async with combine.stream() as streamer:
            print("streamer", dir(streamer))
            async for output in streamer:
                if not is_stream_started:
                    is_stream_started = True
                    # Stream a blank message to start the stream
                    yield VercelStreamResponse.convert_text("")

                yield output

                if await request.is_disconnected():
                    break
