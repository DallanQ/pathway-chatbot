# API Documentation

The backend provides a RESTful API for the frontend to interact with the chatbot.

## Base URL

The API is served under the `/api` prefix.

## Endpoints

### Chat

- **`POST /api/chat`**

  This is the main endpoint for streaming chat responses.

  - **Request Body:**
    ```json
    {
      "messages": [
        {
          "role": "user",
          "content": "Hello"
        }
      ],
      "data": {
        "role": "missionary"
      }
    }
    ```
  - **Response:** A streaming response with the chatbot's messages.

- **`POST /api/chat/request`**

  This endpoint is for non-streaming chat responses.

  - **Request Body:** Same as the streaming endpoint.
  - **Response:**
    ```json
    {
      "result": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      },
      "nodes": []
    }
    ```

- **`POST /api/chat/thumbs_request`**

  This endpoint is for submitting user feedback (thumbs up/down) on a chat response.

  - **Request Body:**
    ```json
    {
      "trace_id": "some-trace-id",
      "value": "thumbs-up"
    }
    ```
  - **Response:**
    ```json
    {
      "feedback": "thumbs-up"
    }
    ```

### Chat Configuration

- **`GET /api/chat/config`**

  This endpoint retrieves the chat configuration, such as starter questions.

  - **Response:**
    ```json
    {
      "starter_questions": [
        "What is BYU-Pathway?",
        "How do I apply?",
        "What are the tuition costs?"
      ]
    }
    ```

- **`GET /api/chat/config/llamacloud`**

  If LlamaCloud is configured, this endpoint retrieves the LlamaCloud configuration.

### File Upload

- **`POST /api/chat/upload`**

  This endpoint is for uploading files to be used in the chat.

  - **Request Body:**
    ```json
    {
      "base64": "...",
      "filename": "document.pdf",
      "params": {}
    }
    ```
  - **Response:** A list of document IDs.
    ```json
    [
      "doc-id-1",
      "doc-id-2"
    ]
    ```
