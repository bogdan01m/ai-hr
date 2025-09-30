from datetime import datetime
from typing import Optional, List, Dict
from uuid import UUID, uuid4
from dotenv import load_dotenv

from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from chainlit.data.base import ThreadDict
from chainlit.user import UserDict
from chainlit.step import StepDict
from sqlalchemy import select

from .config import AsyncSessionLocal, create_tables, get_database_url
from .models import User, Thread, Step

# Load environment variables
load_dotenv()


class CustomSQLAlchemyDataLayer(SQLAlchemyDataLayer):
    """Custom Chainlit data layer with profile context integration"""

    def __init__(self, conninfo: str):
        super().__init__(conninfo=conninfo)
        self.session_factory = AsyncSessionLocal

    async def create_user(self, user: UserDict) -> Optional[UserDict]:
        """Create a new user"""
        async with self.session_factory() as session:
            try:
                db_user = User(
                    id=UUID(user["id"]) if user.get("id") else uuid4(),
                    identifier=user["identifier"],
                    metadata_=user.get("metadata", {}),
                    createdAt=user.get("createdAt") or datetime.utcnow().isoformat(),
                )
                session.add(db_user)
                await session.commit()
                await session.refresh(db_user)

                return {
                    "id": str(db_user.id),
                    "identifier": db_user.identifier,
                    "metadata": db_user.metadata_,
                    "createdAt": db_user.createdAt,
                }
            except Exception:
                await session.rollback()
                raise

    async def get_user(self, identifier: str) -> Optional[UserDict]:
        """Get user by identifier"""
        async with self.session_factory() as session:
            try:
                result = await session.execute(
                    select(User).filter(User.identifier == identifier)
                )
                user = result.scalar_one_or_none()

                if user:
                    return {
                        "id": str(user.id),
                        "identifier": user.identifier,
                        "metadata": user.metadata_,
                        "createdAt": user.createdAt,
                    }
                return None
            except Exception:
                return None

    async def create_thread(
        self, thread: ThreadDict, profile_context: Optional[Dict] = None
    ) -> ThreadDict:
        """Create a new thread with optional profile context"""
        async with self.session_factory() as session:
            try:
                # Include profile context in metadata if provided
                metadata = thread.get("metadata", {})
                if profile_context:
                    metadata["profile_context"] = profile_context

                db_thread = Thread(
                    id=UUID(thread["id"]) if thread.get("id") else uuid4(),
                    createdAt=thread.get("createdAt") or datetime.utcnow().isoformat(),
                    name=thread.get("name"),
                    userId=UUID(thread["userId"]) if thread.get("userId") else None,
                    userIdentifier=thread.get("userIdentifier"),
                    tags=thread.get("tags", []),
                    metadata_=metadata,
                )
                session.add(db_thread)
                await session.commit()
                await session.refresh(db_thread)

                return {
                    "id": str(db_thread.id),
                    "createdAt": db_thread.createdAt,
                    "name": db_thread.name,
                    "userId": str(db_thread.userId) if db_thread.userId else None,
                    "userIdentifier": db_thread.userIdentifier,
                    "tags": db_thread.tags or [],
                    "metadata": db_thread.metadata_ or {},
                }
            except Exception:
                await session.rollback()
                raise

    async def get_thread(self, thread_id: str) -> Optional[ThreadDict]:
        """Get thread by ID"""
        async with self.session_factory() as session:
            try:
                result = await session.execute(
                    select(Thread).filter(Thread.id == UUID(thread_id))
                )
                thread = result.scalar_one_or_none()

                if thread:
                    return {
                        "id": str(thread.id),
                        "createdAt": thread.createdAt,
                        "name": thread.name,
                        "userId": str(thread.userId) if thread.userId else None,
                        "userIdentifier": thread.userIdentifier,
                        "tags": thread.tags or [],
                        "metadata": thread.metadata_ or {},
                    }
                return None
            except Exception:
                return None

    async def update_thread(
        self,
        thread_id: str,
        name: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
        profile_context: Optional[Dict] = None,
    ):
        """Update thread with optional profile context"""
        async with self.session_factory() as session:
            try:
                result = await session.execute(
                    select(Thread).filter(Thread.id == UUID(thread_id))
                )
                thread = result.scalar_one_or_none()

                if thread:
                    if name is not None:
                        thread.name = name
                    if user_id is not None:
                        thread.userId = UUID(user_id)
                    if metadata is not None:
                        thread.metadata_ = metadata
                    if tags is not None:
                        thread.tags = tags

                    # Update profile context in metadata
                    if profile_context is not None:
                        current_metadata = thread.metadata_ or {}
                        current_metadata["profile_context"] = profile_context
                        thread.metadata_ = current_metadata

                    await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def create_step(self, step_dict: StepDict) -> StepDict:
        """Create a new step (message)"""
        async with self.session_factory() as session:
            try:
                db_step = Step(
                    id=UUID(step_dict["id"]) if step_dict.get("id") else uuid4(),
                    name=step_dict["name"],
                    type=step_dict["type"],
                    threadId=UUID(step_dict["threadId"]),
                    parentId=UUID(step_dict["parentId"])
                    if step_dict.get("parentId")
                    else None,
                    streaming=step_dict.get("streaming", False),
                    waitForAnswer=step_dict.get("waitForAnswer"),
                    isError=step_dict.get("isError"),
                    metadata_=step_dict.get("metadata", {}),
                    tags=step_dict.get("tags", []),
                    input=step_dict.get("input"),
                    output=step_dict.get("output"),
                    createdAt=step_dict.get("createdAt")
                    or datetime.utcnow().isoformat(),
                    start=step_dict.get("start"),
                    end=step_dict.get("end"),
                    generation=step_dict.get("generation"),
                    showInput=step_dict.get("showInput"),
                    language=step_dict.get("language"),
                    indent=step_dict.get("indent"),
                    defaultOpen=step_dict.get("defaultOpen"),
                )
                session.add(db_step)
                await session.commit()
                await session.refresh(db_step)

                return {
                    "id": str(db_step.id),
                    "name": db_step.name,
                    "type": db_step.type,
                    "threadId": str(db_step.threadId),
                    "parentId": str(db_step.parentId) if db_step.parentId else None,
                    "streaming": db_step.streaming,
                    "waitForAnswer": db_step.waitForAnswer,
                    "isError": db_step.isError,
                    "metadata": db_step.metadata_ or {},
                    "tags": db_step.tags or [],
                    "input": db_step.input,
                    "output": db_step.output,
                    "createdAt": db_step.createdAt,
                    "start": db_step.start,
                    "end": db_step.end,
                    "generation": db_step.generation,
                    "showInput": db_step.showInput,
                    "language": db_step.language,
                    "indent": db_step.indent,
                    "defaultOpen": db_step.defaultOpen,
                }
            except Exception:
                await session.rollback()
                raise

    async def get_profile_context_from_thread(self, thread_id: str) -> Optional[Dict]:
        """Get profile context from thread metadata"""
        thread = await self.get_thread(thread_id)
        if thread and thread.get("metadata", {}).get("profile_context"):
            return thread["metadata"]["profile_context"]
        return None

    async def save_step_with_profile_context(
        self, step_dict: StepDict, profile_context: Optional[Dict] = None
    ) -> StepDict:
        """Save step and update thread with profile context"""
        # Save the step
        saved_step = await self.create_step(step_dict)

        # Update thread with profile context if provided
        if profile_context:
            await self.update_thread(
                thread_id=step_dict["threadId"], profile_context=profile_context
            )

        return saved_step

    async def get_thread_steps(self, thread_id: str) -> List[Dict]:
        """Get all steps (messages) for a thread ordered by creation time"""
        async with self.session_factory() as session:
            try:
                result = await session.execute(
                    select(Step)
                    .filter(Step.threadId == UUID(thread_id))
                    .order_by(Step.createdAt)
                )
                steps = result.scalars().all()

                return [
                    {
                        "id": str(step.id),
                        "name": step.name,
                        "type": step.type,
                        "input": step.input,
                        "output": step.output,
                        "createdAt": step.createdAt,
                        "metadata": step.metadata_ or {},
                    }
                    for step in steps
                ]
            except Exception:
                return []


def get_data_layer_sync():
    """Get the custom data layer instance synchronously"""
    import asyncio

    # Create tables synchronously if needed
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(create_tables())
    finally:
        loop.close()

    # Use the same database URL function as config
    conninfo = get_database_url()

    return CustomSQLAlchemyDataLayer(conninfo=conninfo)


async def get_data_layer():
    """Get the custom data layer instance"""
    await create_tables()

    # Use the same database URL function as config
    conninfo = get_database_url()

    return CustomSQLAlchemyDataLayer(conninfo=conninfo)
