from typing import Optional
import chainlit as cl
from .schemas import ProfileContext


class ProfileContextSaver:
    """Minimal service to save ProfileContext to Chainlit's thread metadata"""

    def __init__(self):
        self.data_layer = None

    async def _get_data_layer(self):
        """Get the same data layer instance that Chainlit uses"""
        if self.data_layer is None:
            from database.data_layer import get_data_layer

            self.data_layer = await get_data_layer()
        return self.data_layer

    async def save_profile_context(self, profile_context: ProfileContext):
        """Save ProfileContext to current thread metadata"""
        try:
            session_id = cl.context.session.id
            data_layer = await self._get_data_layer()

            # Update thread metadata with ProfileContext
            await data_layer.update_thread(
                thread_id=session_id,
                metadata={"profile_context": profile_context.model_dump()},
            )
        except Exception:
            # Fail silently if no session context or other errors
            pass

    async def get_profile_context(self, session_id: str) -> Optional[ProfileContext]:
        """Get ProfileContext from thread metadata"""
        try:
            data_layer = await self._get_data_layer()
            thread = await data_layer.get_thread(session_id)

            if thread and thread.get("metadata", {}).get("profile_context"):
                profile_data = thread["metadata"]["profile_context"]
                return ProfileContext(**profile_data)

            return None
        except Exception:
            return None
