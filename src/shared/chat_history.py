from typing import List, Optional
from datetime import datetime
from uuid import uuid4

from ..database.data_layer import get_data_layer
from .schemas import ProfileContext


class ChatHistoryManager:
    """Simplified chat history manager using Chainlit data layer"""

    def __init__(self):
        self.data_layer = None

    async def _get_data_layer(self):
        """Get or create data layer instance"""
        if self.data_layer is None:
            self.data_layer = await get_data_layer()
        return self.data_layer

    async def save_message(
        self,
        session_id: str,
        message_type: str,
        content: str,
        profile_context: Optional[ProfileContext] = None,
    ):
        """Save message using Chainlit data layer"""
        data_layer = await self._get_data_layer()

        # Get or create thread (Chainlit session)
        thread = await data_layer.get_thread(session_id)
        if not thread:
            # Create new thread
            thread_data = {
                "id": session_id,
                "name": "HR Profile Session",
                "createdAt": datetime.utcnow().isoformat(),
                "userIdentifier": "hr_user",
                "tags": ["hr", "profile"],
                "metadata": {},
            }

            thread = await data_layer.create_thread(
                thread_data, profile_context.model_dump() if profile_context else None
            )
        elif profile_context:
            # Update thread with latest profile context
            await data_layer.update_thread(
                session_id, profile_context=profile_context.model_dump()
            )

        # Create step (message)
        step_data = {
            "id": str(uuid4()),
            "name": f"{message_type}_message",
            "type": "user_message" if message_type == "user" else "assistant_message",
            "threadId": session_id,
            "streaming": False,
            "input": content if message_type == "user" else None,
            "output": content if message_type == "assistant" else None,
            "createdAt": datetime.utcnow().isoformat(),
            "metadata": {
                "message_type": message_type,
                "profile_context": profile_context.model_dump()
                if profile_context
                else None,
            },
        }

        await data_layer.create_step(step_data)

    async def get_chat_history(self, session_id: str) -> List[dict]:
        """Get chat history from Chainlit data layer"""
        data_layer = await self._get_data_layer()
        steps = await data_layer.get_thread_steps(session_id)

        history = []
        for step in steps:
            # Convert step to message format
            if step["type"] == "user_message" and step["input"]:
                history.append(
                    {
                        "type": "user",
                        "content": step["input"],
                        "timestamp": step["createdAt"],
                    }
                )
            elif step["type"] == "assistant_message" and step["output"]:
                history.append(
                    {
                        "type": "assistant",
                        "content": step["output"],
                        "timestamp": step["createdAt"],
                    }
                )

        return history

    async def format_history_for_agent(
        self, session_id: str, current_message: str
    ) -> str:
        """Format history for agent prompt"""
        history = await self.get_chat_history(session_id)

        if not history:
            return current_message

        # Format history
        history_text = "<history_start>\n"
        for msg in history:
            role = "User" if msg["type"] == "user" else "Assistant"
            history_text += f"{role}: {msg['content']}\n"
        history_text += "<history_end>\n\n"

        # Add current message
        history_text += f"<current_message>\n{current_message}\n</current_message>"

        return history_text
