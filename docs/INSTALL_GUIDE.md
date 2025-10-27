# Devr.AI Installation Guide

Follow this guide to set up Devr.AI's development environment on your local machine.
For Setup guide video tutorial go to [Devr Setup Guide](https://drive.google.com/file/d/1vlwGE5oJrbXb1gkZJv2NT2rHyt-z-RDv/view?usp=sharing)

## Prerequisites

-   [Python](https://www.python.org/) 3.9+ (version 3.10 is recommended)
-   [Node.js](https://nodejs.org/en) (latest LTS version)
-   [Git](https://git-scm.com/) (any recent version)
-   [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) (for Weaviate database)

## Quick Start

1. **Clone the repository**
```sh
git clone https://github.com/AOSSIE-Org/Devr.AI.git
cd Devr.AI
```

2. **Install Poetry** (Python package manager)
```sh
# Linux / MacOS / WSL
curl -sSL https://install.python-poetry.org | python3 -

# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

# Verify installation
poetry --version  # Should show v2.0.0 or above
```

3. **Install Python dependencies**
```sh
poetry env use python3.10
poetry lock --no-update
poetry install --with dev
```

4. **Activate the virtual environment**
```sh
# Linux / Mac / WSL
eval $(poetry env activate)

# Windows (PowerShell)
Invoke-Expression (poetry env activate)
```

5. **Set up environment variables**
```sh
# Copy the example environment file
cp env.example .env

# Edit .env with your API keys and configuration
nano .env  # or use your preferred editor
```

6. **Set up Docker container**
```sh
cd backend
docker-compose up -d # Start weaviate, falkordb, rabbitmq
```

7. **Start Docker containers**
```sh
Go to docker dekstop and start the containers
```

8. **Start the backend server**
```sh
cd backend
poetry run python main.py # Terminal 1
poetry run python start_github_mcp_server.py # Terminal 2 (Start MCP server)
flask --app api/index.py run --debug --port 5000 # Terminal 3 (Start graphDB)
```

9. **Start the frontend** (in a new terminal)
```sh
cd frontend
npm install
npm run dev
```

## Environment Variables

Create a `.env` file in the project root with the following variables:

### Required Variables
```env
# AI Services
GEMINI_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# Platform Integrations
DISCORD_BOT_TOKEN=your_discord_bot_token_here
GITHUB_TOKEN=your_github_token_here

# Database
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here

# Backend Configuration
BACKEND_URL=http://localhost:8000
```

### Optional Variables
```env
# LangSmith Tracing (for development)
LANGSMITH_TRACING=false
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=DevR_AI

# RabbitMQ (uses default if not set)
RABBITMQ_URL=amqp://localhost:5672/

# Agent Configuration
DEVREL_AGENT_MODEL=gemini-2.5-flash
GITHUB_AGENT_MODEL=gemini-2.5-flash
CLASSIFICATION_AGENT_MODEL=gemini-2.0-flash
AGENT_TIMEOUT=30
MAX_RETRIES=3
```

## API Key Setup

### 1. Google Gemini API
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file as `GEMINI_API_KEY`

### 2. Tavily Search API
1. Go to [Tavily](https://tavily.com/)
2. Sign up and get your API key
3. Add it to your `.env` file as `TAVILY_API_KEY`

### 3. Discord Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the token and add it to your `.env` file as `DISCORD_BOT_TOKEN`
5. Enable required intents: Message Content Intent, Server Members Intent

### 4. GitHub Token
1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Generate a new token with `repo` and `user` scopes
3. Add it to your `.env` file as `GITHUB_TOKEN`

### 5. Supabase Setup
1. Go to [Supabase](https://supabase.com/) and create a new project
2. Go to Settings > API
3. Copy the URL and anon key
4. Add them to your `.env` file as `SUPABASE_URL` and `SUPABASE_KEY`

## Database Setup

### Weaviate Vector Database
Weaviate is used for semantic search and embeddings storage. It runs in Docker:

```sh
cd backend
docker-compose up -d weaviate
```

The database will be available at `http://localhost:8080`

### Supabase Database
Supabase provides the PostgreSQL database for user data and authentication. The connection is configured via environment variables.

## Current Features

### Discord Integration
- **Intelligent Message Processing**: AI-powered responses to community questions
- **GitHub Account Verification**: Link Discord accounts to GitHub profiles
- **Conversation Memory**: Persistent context across sessions
- **Commands**:
  - `!verify_github` - Link your GitHub account
  - `!verification_status` - Check account linking status
  - `!reset` - Clear conversation memory
  - `!help_devrel` - Show available commands

### LangGraph Agent System
- **DevRel Agent**: Primary conversational agent for community support
- **ReAct Workflow**: Think → Act → Observe pattern for intelligent responses
- **Tool Integration**: Web search, FAQ lookup, GitHub operations
- **Conversation Summarization**: Automatic memory management

### AI Services
- **Google Gemini**: Primary LLM for reasoning and response generation
- **Tavily Search**: Real-time web search for current information
- **Text Embeddings**: Semantic search capabilities

### Data Storage
- **Supabase**: User profiles, authentication, conversation metadata
- **Weaviate**: Vector embeddings and semantic search
- **Agent Memory**: Persistent conversation context

## Development

### Running Tests
```sh
poetry run pytest
```

### Code Formatting
```sh
poetry run black .
poetry run isort .
```

### Linting
```sh
poetry run flake8
```

### Frontend Development
```sh
cd frontend
npm run dev  # Start development server
npm run build  # Build for production
npm run lint  # Run ESLint
```

## Troubleshooting

### Common Issues

1. **Poetry environment not activated**
   ```sh
   poetry shell
   ```

2. **Weaviate connection failed**
   ```sh
   # Check if Docker is running
   docker ps
   
   # Restart Weaviate
   docker-compose down
   docker-compose up -d weaviate
   ```

3. **Missing environment variables**
   - Ensure all required variables are set in `.env`
   - Check that the file is in the project root

4. **Port conflicts**
   - Backend runs on port 8000
   - Frontend runs on port 5173 (Vite default)
   - Weaviate runs on port 8080

### Logs
- Backend logs are displayed in the terminal where you run `python main.py`
- Check Docker logs for Weaviate: `docker-compose logs weaviate`

## Project Structure

```
Devr.AI/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── agents/         # LangGraph agents
│   │   ├── api/           # API routes
│   │   ├── core/          # Configuration and core logic
│   │   ├── database/      # Database connections
│   │   ├── models/        # Data models
│   │   └── services/      # Business logic
│   ├── integrations/      # Platform integrations
│   │   ├── discord/       # Discord bot
│   │   ├── github/        # GitHub integration
│   │   └── slack/         # Slack integration (planned)
│   └── main.py           # Application entry point
├── frontend/              # React frontend
├── docs/                  # Documentation
└── tests/                 # Test files
```

## Next Steps

1. **Set up your Discord server** and invite the bot
2. **Configure GitHub OAuth** for user verification
3. **Test the bot** with basic commands
4. **Explore the codebase** to understand the architecture
5. **Contribute** by implementing new features or fixing bugs

For more information, refer to the main [README.md](../README.md) file.
