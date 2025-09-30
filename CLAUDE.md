# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI HR Assistant - a Chainlit-based conversational AI application that helps HR professionals create structured candidate profiles for job positions. The system uses PydanticAI agents with OpenAI GPT-4o-mini to guide users through collecting position requirements, hard skills, soft skills, and work conditions.

## Development Commands

### Setup and Running
```bash
# Start PostgreSQL database
docker-compose up -d

# Install dependencies (requires Python >=3.12)
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY and LOGFIRE_TOKEN
# Note: DATABASE_URL is intentionally commented out in .env.example

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

### Database
The PostgreSQL database runs in Docker and is accessed via SQLAlchemy. Tables are auto-created on first run.

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

The project is organized into modular packages under `src/` for better code organization and maintainability.

### Core Components

**app.py** - Main Chainlit application entry point
- Handles chat lifecycle (@cl.on_chat_start, @cl.on_message)
- Manages user sessions with ProfileContext and ChatHistoryManager
- Integrates logging and database operations
- Imports from modular `src/` packages

**src/hr_agent/** - PydanticAI agent package
- `agent.py`: Main agent configuration with OpenAI GPT-4o-mini and tool registration
- `tools.py`: Agent tools for profile management (update_position_info, update_hard_skills, update_soft_skills, update_work_conditions, get_profile_status)
- Each tool logs profile updates and returns current stage status

**src/shared/** - Shared components package
- `schemas.py`: Pydantic models defining candidate profile structure (ProfileContext, CandidateProfile with PositionInfo, HardSkills, SoftSkills, WorkConditions)
- `chat_history.py`: ChatHistoryManager for message storage/retrieval with XML formatting
- `prompt.py`: System prompt configuration for the AI agent
- `logger_config.py`: Logfire integration and logging utilities
- work_format field in WorkConditions accepts flexible string values (not limited to enum)

**src/database/** - Database layer package
- `config.py`: Database configuration, async engine, and session management
- `models.py`: SQLAlchemy models for ChatSession and ChatMessage
- `data_layer.py`: Chainlit data layer integration (optional)
- Custom database URL handling to avoid conflicts with Chainlit's built-in persistence
- Auto-creates tables on first connection

### Key Design Patterns

**Dual Persistence**: The system maintains two separate data layers:
1. Chainlit session state for ProfileContext (in-memory during session)
2. PostgreSQL for permanent message history and profile snapshots

**Agent Context Flow**: Each user message includes full conversation history formatted for the agent, enabling context-aware responses.

**Stage-based Profile Building**: ProfileContext tracks completion stages (position → hard_skills → soft_skills → work_conditions → complete) with validation methods.

## Configuration Notes

### Environment Variables
- DATABASE_URL is intentionally commented out in .env to prevent Chainlit from using the same database
- Chainlit data persistence is disabled in .chainlit/config.toml
- Logfire integration is optional but configured for observability

### Agent Behavior
The agent system prompt (src/shared/prompt.py) instructs the AI to:
- Use tools for all data persistence operations
- Adapt questions based on position type (technical vs non-technical roles)
- Never repeat the welcome message (already shown by Chainlit)
- Follow structured conversation flow through profile stages

### Database Schema
Message history preserves both the raw conversation and profile context snapshots, enabling full session reconstruction and analytics on profile creation patterns.
