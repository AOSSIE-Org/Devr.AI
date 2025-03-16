# Devr.AI Backend

This folder contains the backend code for Devr.AI application.

## Setup Instructions

### 1. Database Setup

To set up the vector database in Supabase:

1. Navigate to the Supabase SQL Editor
2. Run the SQL queries from the `app/services/rag/vector_db.sql` file to:
    - Create the necessary extensions
    - Create the embeddings table
    - Set up the required functions for vector similarity search

### 2. Environment Configuration

1. Create a `.env` file in the root directory based on the provided `.env.example`:
    ```
    cp .env.example .env
    ```
2. Update the values in the `.env` file with your actual credentials and configurations

### 3. Running the Application

To run the application:

```bash
poetry run python main.py
```

### 4. Running Tests

To run the tests:

```bash
PYTHONPATH=$(pwd) poetry run pytest tests/
```

## Development

Additional development instructions and documentation will be added as the project evolves.
