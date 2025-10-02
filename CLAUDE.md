# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI HR Assistant - a Chainlit-based conversational AI application that helps HR professionals create structured candidate profiles for job positions. The system uses PydanticAI agents with OpenAI GPT-4o-mini to guide users through collecting position requirements, hard skills, soft skills, and work conditions.

## Development Commands

### Setup and Running

#### Option 1: Full Docker Setup (Recommended)
```bash
# Configure environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY, LOGFIRE_TOKEN, and other required variables
# Note: DATABASE_URL will be automatically set for Docker containers

# Place your Google credentials file as google-credentials.json in the project root

# Build and start all services (PostgreSQL + Chainlit)
docker-compose up --build

# The application will be available at http://localhost:8000
```

#### Option 2: Local Development
```bash
# Start PostgreSQL database
docker-compose up -d postgres

# Install dependencies (requires Python >=3.12)
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY, LOGFIRE_TOKEN, and DATABASE_URL

# Run the application
chainlit run app.py
# or
uv run chainlit run app.py
```

### Dependencies
Project uses UV for dependency management with the following key dependencies:
- chainlit >=2.8.0 (UI framework)
- pydantic-ai-slim[openai] >=1.0.10 (AI agent framework)
- sqlalchemy >=2.0.43 + asyncpg/psycopg2-binary (database)
- logfire >=4.8.0 (observability)
- gspread >=6.2.1 (Google Sheets integration)
### Code Quality
Project includes automated code quality tools:
```bash
# Install pre-commit hooks
pre-commit install

# Run pre-commit manually
pre-commit run --all-files
```

**Pre-commit hooks:**
- trailing-whitespace, end-of-file-fixer, check-yaml
- check-added-large-files, check-merge-conflict
- ruff (Python linting and formatting with auto-fix)

**CI/CD Pipeline (.github/workflows/ci.yml):**
- Runs on push to main/develop branches and pull requests
- Code quality checks with ruff
- Python 3.12+ compatibility testing

## Architecture

The project uses a simplified architecture built on Chainlit's built-in persistence with minimal custom components.

### Core Components

**app.py** - Main Chainlit application entry point
- Handles chat lifecycle (@cl.on_chat_start, @cl.on_message, @cl.on_chat_resume)
- Manages user sessions with ProfileContext restoration
- Uses Chainlit's built-in SQLAlchemy data layer for persistence
- Integrates logging and observability

**src/hr_agent/** - PydanticAI agent package
- `agent.py`: Main agent configuration with OpenAI GPT-4o-mini and tool registration
- `tools.py`: Agent tools for profile management (update_position_info, update_hard_skills, update_soft_skills, update_work_conditions, get_profile_status, save_profile_to_sheets)
- Each tool logs profile updates and returns current stage status

**src/shared/** - Shared components package
- `schemas.py`: Pydantic models defining candidate profile structure (ProfileContext, CandidateProfile with PositionInfo, HardSkills, SoftSkills, WorkConditions)
- `chat_history.py`: Simplified ChatHistoryManager for history formatting only
- `profile_saver.py`: Minimal ProfileContextSaver for thread metadata persistence
- `database_url.py`: Database URL configuration utility
- `prompt.py`: System prompt configuration for the AI agent
- `logger_config.py`: Logfire integration and logging utilities
- `google_sheets.py`: GoogleSheetsManager for saving completed profiles to Google Sheets

### Key Design Patterns

**Single Source of Truth**: Uses Chainlit's built-in SQLAlchemy data layer for all persistence:
1. Message history automatically saved and restored in UI
2. ProfileContext saved in thread metadata for cross-session persistence
3. Chat history extracted from ThreadDict on session resume

**Agent Context Flow**: Each user message includes full conversation history formatted for the agent, enabling context-aware responses.

**Stage-based Profile Building**: ProfileContext tracks completion stages (position → hard_skills → soft_skills → work_conditions → complete) with validation methods.

**Session Restoration**: On chat resume, the system:
1. Extracts message history from ThreadDict["steps"]
2. Restores ProfileContext from thread metadata
3. Maintains full context continuity across sessions

## Configuration Notes

### Environment Variables
- DATABASE_URL configures PostgreSQL connection for Chainlit's data layer
- Logfire integration is optional but configured for observability
- Google Sheets integration requires GOOGLE_SPREADSHEET_ID and GOOGLE_CREDENTIALS_PATH environment variables

### Agent Behavior
The agent system prompt (src/shared/prompt.py) instructs the AI to:
- Use tools for all data persistence operations
- Adapt questions based on position type (technical vs non-technical roles)
- Never repeat the welcome message (already shown by Chainlit)
- Follow structured conversation flow through profile stages

### Data Persistence
The application uses Chainlit's built-in SQLAlchemy data layer with:
- Automatic message history persistence in UI
- ProfileContext stored in thread metadata for session restoration
- Thread-based persistence enabling seamless chat resume functionality
- No custom database models or duplicate persistence logic required
