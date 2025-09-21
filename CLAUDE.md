# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI HR Assistant - a Chainlit-based conversational AI application that helps HR professionals create structured candidate profiles for job positions. The system uses PydanticAI agents with OpenAI GPT-4o-mini to guide users through collecting position requirements, hard skills, soft skills, and work conditions.

## Development Commands

### Setup and Running
```bash
# Start PostgreSQL database
docker-compose up -d

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY and LOGFIRE_TOKEN

# Run the application
chainlit run app.py
# or
uv run chainlit run app.py
```

### Database
The PostgreSQL database runs in Docker and is accessed via SQLAlchemy. Tables are auto-created on first run.

## Architecture

### Core Components

**app.py** - Main Chainlit application entry point
- Handles chat lifecycle (@cl.on_chat_start, @cl.on_message)
- Manages user sessions with ProfileContext and ChatHistoryManager
- Integrates logging and database operations

**hr_agent.py** - PydanticAI agent with tools for profile management
- Agent configured with SYSTEM_PROMPT and ProfileContext dependencies
- Tools: update_position_info, update_hard_skills, update_soft_skills, update_work_conditions, get_profile_status
- Each tool logs profile updates and returns current stage status

**schemas.py** - Pydantic models defining the candidate profile structure
- ProfileContext: Main context object with CandidateProfile and stage tracking
- CandidateProfile: Composed of PositionInfo, HardSkills, SoftSkills, WorkConditions
- Stage validation methods determine completion of each profile section

**database.py** - SQLAlchemy models and session management
- ChatSession and ChatMessage models for conversation persistence
- Custom database URL to avoid conflicts with Chainlit's built-in persistence
- Auto-creates tables on first connection

**chat_history.py** - Conversation history management
- ChatHistoryManager handles message storage and retrieval
- Formats message history for agent context in specific XML format
- Integrates with database models for persistence

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
The agent system prompt (prompt.py) instructs the AI to:
- Use tools for all data persistence operations
- Adapt questions based on position type (technical vs non-technical roles)
- Never repeat the welcome message (already shown by Chainlit)
- Follow structured conversation flow through profile stages

### Database Schema
Message history preserves both the raw conversation and profile context snapshots, enabling full session reconstruction and analytics on profile creation patterns.