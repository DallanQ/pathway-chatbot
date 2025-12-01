# Frontend Setup

This guide provides instructions on how to set up and run the frontend of the Pathway Chatbot locally for development. For more information, please refer to the main [README.md](../README.md) file.

## Prerequisites

- [Node.js](https://nodejs.org/) (version 20.x or higher)
- [npm](https://www.npmjs.com/) (usually comes with Node.js)

## Installation

1.  **Navigate to the frontend directory:**

    ```bash
    cd pathway-chatbot/frontend
    ```

2.  **Install dependencies:**

    As mentioned in the main `README.md`, you can use npm to install the dependencies:

    ```bash
    npm install
    ```

3.  **Set up environment variables:**

    Create a `.env.local` file in the `frontend` directory by copying the example file:

    ```bash
    cp .env.example .env.local
    ```

    Update the `.env.local` file with the URL of the backend API. For example:

    ```
    NEXT_PUBLIC_CHAT_API_URL=http://localhost:8000
    ```

## Running the Application

To run the frontend server in development mode, use the following command:

```bash
npm run dev
```

The application will be available at `http://localhost:3000`.

