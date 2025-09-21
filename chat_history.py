import json
from typing import List, Optional
from sqlalchemy.orm import Session
from database import get_db, ChatSession, ChatMessage, create_tables
from schemas import ProfileContext

class ChatHistoryManager:
    def __init__(self):
        # Ensure tables exist
        create_tables()

    def get_or_create_session(self, session_id: str) -> ChatSession:
        """Get existing session or create new one"""
        db = next(get_db())
        try:
            session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
            if not session:
                session = ChatSession(session_id=session_id)
                db.add(session)
                db.commit()
                db.refresh(session)
            return session
        finally:
            db.close()

    def save_message(
        self,
        session_id: str,
        message_type: str,
        content: str,
        profile_context: Optional[ProfileContext] = None
    ):
        """Save message to database"""
        db = next(get_db())
        try:
            # Get or create session
            session = self.get_or_create_session(session_id)

            # Serialize profile context
            context_json = None
            if profile_context:
                context_json = profile_context.model_dump_json()

            # Create message
            message = ChatMessage(
                session_id=session.id,
                message_type=message_type,
                content=content,
                profile_context=context_json
            )

            db.add(message)
            db.commit()
        finally:
            db.close()

    def get_chat_history(self, session_id: str) -> List[dict]:
        """Get chat history for session"""
        db = next(get_db())
        try:
            session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
            if not session:
                return []

            messages = db.query(ChatMessage).filter(
                ChatMessage.session_id == session.id
            ).order_by(ChatMessage.created_at).all()

            history = []
            for msg in messages:
                history.append({
                    "type": msg.message_type,
                    "content": msg.content,
                    "timestamp": msg.created_at.isoformat()
                })

            return history
        finally:
            db.close()

    def format_history_for_agent(self, session_id: str, current_message: str) -> str:
        """Format history for agent prompt"""
        history = self.get_chat_history(session_id)

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