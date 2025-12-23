# Component Documentation

This document provides an overview of the major React components used in the frontend of the Pathway Chatbot.

## `ChatSection`

The `ChatSection` component is the main component that orchestrates the chat interface. It is responsible for:

- Managing the chat state using the `useChat` hook from the Vercel AI SDK.
- Handling user input and submitting it to the backend.
- Displaying the chat messages.
- Showing a greeting and disclaimer message before the chat starts.

### Props

This component does not accept any props.

## `ChatInput`

The `ChatInput` component provides the input field for the user to type their messages. It also includes:

- A file uploader for attaching documents to the chat.
- A button to submit the message.
- A toggle for "ACMs Only" mode.

### Props

- `isLoading`: A boolean that indicates whether a response is being generated.
- `input`: The current value of the input field.
- `handleSubmit`: A function to handle form submission.
- `handleInputChange`: A function to handle changes to the input field.
- `messages`: The array of chat messages.
- `setInput`: A function to set the input value.
- `append`: A function to append a new message to the chat.
- `stop`: A function to stop the generation of a response.
- `isAcmChecked`: A boolean that indicates whether the "ACMs Only" mode is enabled.
- `setIsAcmChecked`: A function to toggle the "ACMs Only" mode.

## `ChatMessages`

The `ChatMessages` component is responsible for displaying the list of chat messages. It also handles:

- Displaying a loading indicator while waiting for a response.
- Showing starter questions if the chat has not yet started.
- Providing a button to reload the last response.

### Props

- `messages`: The array of chat messages to display.
- `isLoading`: A boolean that indicates whether a response is being generated.
- `reload`: A function to reload the last response.
- `stop`: A function to stop the generation of a response.
- `append`: A function to append a new message to the chat.
- `setMessages`: A function to update the array of chat messages.
