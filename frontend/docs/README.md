# Frontend Documentation

The frontend of the Pathway Chatbot is a [Next.js](https://nextjs.org/) application that provides a user-friendly interface for interacting with the chatbot.

## Architecture

The frontend is built with [React](https://react.dev/) and [TypeScript](https://www.typescriptlang.org/) and is structured as follows:

- **`app/`:** The main directory for the Next.js application.
  - **`page.tsx`:** The main entry point of the application's UI.
  - **`layout.tsx`:** The root layout for the application.
  - **`components/`:** This directory contains the reusable React components used throughout the application.
    - **`chat-section.tsx`:** The main component that orchestrates the chat interface.
    - **`ui/chat/`:** Components specifically for the chat interface, such as `ChatInput` and `ChatMessages`.
- **`public/`:** This directory contains static assets, such as images and logos.
- **`config/`:** This directory contains configuration files for the frontend.

## State Management

The frontend uses the [Vercel AI SDK](https://sdk.vercel.ai/docs) and its `useChat` hook for managing the chat state. This hook simplifies the process of sending and receiving messages from the backend, managing message history, and handling loading states.

For more details on the components, see the [Component Documentation](./Components.md).

For instructions on how to set up and run the frontend, see the [Setup Guide](./Setup.md).
