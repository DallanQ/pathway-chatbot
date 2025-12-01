# Backend Documentation

The backend of the Pathway Chatbot is a Python application built with the [FastAPI](https://fastapi.tiangolo.com/) framework. It provides the core functionality of the chatbot, including the chat engine, API, and other services.

## Architecture

The backend is structured as a modular FastAPI application. The main components are:

- **`main.py`:** The entry point of the application. It initializes the FastAPI app, includes the routers, and sets up middleware.
- **`app/api/`:** This directory contains the API routers, which define the endpoints for the application.
  - **`routers/chat.py`:** Defines the main chat endpoints for handling user messages.
  - **`routers/chat_config.py`:** Defines endpoints for retrieving chat configuration.
  - **`routers/upload.py`:** Defines endpoints for file uploads.
- **`app/engine/`:** This directory contains the core chat engine logic, built with [LlamaIndex](https://www.llamaindex.ai/).
  - **`index.py`:**  Handles the creation and configuration of the LlamaIndex chat engine.
  - **`generate.py`:**  Contains the logic for generating responses with the chat engine.
- **`app/observability/`:** This directory contains the setup for observability and monitoring, using [Langfuse](https://langfuse.com/).

## Services

The backend also includes several services:

- **Security:** The `app/security/` directory contains modules for input validation and sanitization to protect against malicious input.
- **Localization:** The `app/utils/localization.py` module handles language detection to provide localized responses.
- **Geo IP:** The `app/utils/geo_ip.py` module is used to get geographic information from the user's IP address.

For details on the API endpoints, see the [API Documentation](./API.md).

For instructions on how to set up and run the backend, see the [Setup Guide](./Setup.md).
