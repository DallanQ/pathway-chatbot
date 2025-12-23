# Project Architecture

The Pathway Chatbot is a full-stack web application composed of two main parts: a frontend and a backend.

## Frontend

The frontend is a [Next.js](https://nextjs.org/) application built with [React](https://react.dev/) and [TypeScript](https://www.typescriptlang.org/). It provides the user interface for the chatbot, including the chat window, message display, and input controls.

- **Framework:** Next.js
- **Language:** TypeScript
- **Styling:** [Tailwind CSS](https://tailwindcss.com/)
- **Chat Functionality:** The frontend uses the [Vercel AI SDK](https://sdk.vercel.ai/docs) to handle chat state and communication with the backend.

## Backend

The backend is a [FastAPI](https://fastapi.tiangolo.com/) application that serves as the brain of the chatbot. It exposes a RESTful API that the frontend consumes.

- **Framework:** FastAPI
- **Language:** Python
- **Core Logic:** The backend uses the [LlamaIndex](https://www.llamaindex.ai/) library to create a chat engine. This engine uses a Retrieval-Augmented Generation (RAG) model to answer user queries.
- **Observability:** The backend is instrumented with [Langfuse](https://langfuse.com/) for tracing and monitoring of the LLM application.

## Interaction

The frontend and backend communicate via a REST API. The frontend sends user messages to the backend, which then uses the chat engine to generate a response. The response is streamed back to the frontend and displayed to the user.
