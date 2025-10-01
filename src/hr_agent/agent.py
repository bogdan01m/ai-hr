from pydantic_ai import Agent
from dotenv import load_dotenv

from ..shared.schemas import ProfileContext
from ..shared.prompt import SYSTEM_PROMPT
from .tools import (
    update_position_info,
    update_hard_skills,
    update_soft_skills,
    update_work_conditions,
    get_profile_status,
    save_profile_to_sheets,
)

load_dotenv()

# Create the HR agent
agent = Agent(
    "openai:gpt-4o-mini",
    system_prompt=SYSTEM_PROMPT,
    deps_type=ProfileContext,
    instrument=True,
    retries=5,
)

# Register tools
agent.tool(update_position_info)
agent.tool(update_hard_skills)
agent.tool(update_soft_skills)
agent.tool(update_work_conditions)
agent.tool(get_profile_status)
agent.tool(save_profile_to_sheets)
