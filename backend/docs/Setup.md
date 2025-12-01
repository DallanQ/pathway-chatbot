# Backend Setup

This guide provides instructions on how to set up and run the backend of the Pathway Chatbot locally for development.

## Prerequisites

- Python 3.11 or higher
- [Poetry](https://python-poetry.org/) for dependency management

## Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd pathway-chatbot/backend
    ```

2.  **Install dependencies:**

    Use Poetry to install the dependencies listed in `pyproject.toml`:

    ```bash
    poetry install
    ```

3.  **Set up environment variables:**

    Create a `.env` file in the `backend` directory by copying the example file:

    ```bash
    cp .env.example .env
    ```

    Update the `.env` file with your specific configuration, such as API keys for LlamaIndex, Langfuse, etc.

## Running the Application

To run the backend server in development mode, use the following command:
First, setup the environment with poetry: https://python-poetry.org/

> **_Note:_** This step is not needed if you are using the dev-container.

```
poetry install
poetry shell
```

Then check the parameters that have been pre-configured in the `.env` file in this directory. (E.g. you might need to configure an `OPENAI_API_KEY` if you're using OpenAI as model provider).

Second, run the development server:

```
python main.py
The application will be available at `http://localhost:8000`.