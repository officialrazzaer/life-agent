## Phase 1: Foundation Setup

### Step 1: Environment and Repository Setup

Begin by establishing the core infrastructure that will house your personal AI system. This foundation will support all subsequent development phases.

First, create a GitHub repository to maintain version control of your codebase. Structure the repository with the following directories:

- `/src` - For core Python code
- `/scripts` - For utility scripts
- `/config` - For configuration files
- `/docs` - For documentation
- `/tests` - For test cases

Next, set up a Python virtual environment to manage dependencies:

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install core dependencies
pip install langchain openai supabase chromadb qdrant-client python-telegram-bot pydantic python-dotenv
pip freeze > requirements.txt
```

Create a `.env` file to securely store API keys and credentials:

```
# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Vector DB (Chroma or Qdrant)
VECTOR_DB_HOST=your_vector_db_host
VECTOR_DB_PORT=your_vector_db_port
VECTOR_DB_API_KEY=your_vector_db_api_key

# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# External APIs
MONZO_API_KEY=your_monzo_api_key
COINGECKO_API_KEY=your_coingecko_api_key
```
