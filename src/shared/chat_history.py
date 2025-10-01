from typing import List, Optional
import chainlit as cl
from .schemas import ProfileContext
from .profile_saver import ProfileContextSaver


class ChatHistoryManager:
    """Simplified chat history manager using only Chainlit built-in persistence"""

    def __init__(self):
        self.profile_saver = ProfileContextSaver()

    async def update_profile_context(self, profile_context: ProfileContext):
        """Update ProfileContext in Chainlit's thread metadata"""
        # Update user session for immediate access
        cl.user_session.set("profile_context", profile_context)

        # Save to thread metadata for persistence
        await self.profile_saver.save_profile_context(profile_context)

    async def get_chat_history(self, session_id: Optional[str] = None) -> List[dict]:
        """Get chat history from user session (restored by on_chat_resume)"""
        try:
            return cl.user_session.get("message_history", [])
        except Exception:
            # If no user session context, return empty history
            return []

    async def format_history_for_agent(
        self,
        session_id: str,
        current_message: str,
        profile_context: Optional[ProfileContext] = None,
    ) -> str:
        """Format history for agent prompt, including PDF context if available"""
        history = await self.get_chat_history(session_id)

        formatted_message = ""

        # Add company PDF context if available
        if profile_context and profile_context.company_info_pdf:
            formatted_message += f"<company_context>\n{profile_context.company_info_pdf}\n</company_context>\n\n"

        # Add chat history if exists
        if history:
            formatted_message += "<history_start>\n"
            for msg in history:
                role = "User" if msg["type"] == "user" else "Assistant"
                formatted_message += f"{role}: {msg['content']}\n"
            formatted_message += "<history_end>\n\n"

        # Add current message
        formatted_message += f"<current_message>\n{current_message}\n</current_message>"

        return formatted_message
