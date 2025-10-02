from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

if TYPE_CHECKING:
    from sqlalchemy.ext.declarative import DeclarativeMeta

    Base: DeclarativeMeta
else:
    from .config import Base


class User(Base):
    """Chainlit users table"""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    identifier = Column(Text, nullable=False, unique=True)
    metadata_ = Column("metadata", JSONB, nullable=False, default={})
    createdAt = Column(Text)

    # Relationships
    threads = relationship(
        "Thread", back_populates="user", cascade="all, delete-orphan"
    )


class Thread(Base):
    """Chainlit threads table (chat sessions)"""

    __tablename__ = "threads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    createdAt = Column(Text)
    name = Column(Text)
    userId = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    userIdentifier = Column(Text)
    tags = Column(ARRAY(Text))
    metadata_ = Column("metadata", JSONB, default={})

    # Relationships
    user = relationship("User", back_populates="threads")
    steps = relationship("Step", back_populates="thread", cascade="all, delete-orphan")
    elements = relationship(
        "Element", back_populates="thread", cascade="all, delete-orphan"
    )
    feedbacks = relationship(
        "Feedback", back_populates="thread", cascade="all, delete-orphan"
    )


class Step(Base):
    """Chainlit steps table (messages)"""

    __tablename__ = "steps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
    threadId = Column(UUID(as_uuid=True), ForeignKey("threads.id"), nullable=False)
    parentId = Column(UUID(as_uuid=True))
    streaming = Column(Boolean, nullable=False, default=False)
    waitForAnswer = Column(Boolean)
    isError = Column(Boolean)
    metadata_ = Column("metadata", JSONB, default={})
    tags = Column(ARRAY(Text))
    input = Column(Text)
    output = Column(Text)
    createdAt = Column(Text)
    command = Column(Text)
    start = Column(Text)
    end = Column(Text)
    generation = Column(JSONB)
    showInput = Column(Text)
    language = Column(Text)
    indent = Column(Integer)
    defaultOpen = Column(Boolean)

    # Relationships
    thread = relationship("Thread", back_populates="steps")


class Element(Base):
    """Chainlit elements table"""

    __tablename__ = "elements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    threadId = Column(UUID(as_uuid=True), ForeignKey("threads.id"))
    type = Column(Text)
    url = Column(Text)
    chainlitKey = Column(Text)
    name = Column(Text, nullable=False)
    display = Column(Text)
    objectKey = Column(Text)
    size = Column(Text)
    page = Column(Integer)
    language = Column(Text)
    forId = Column(UUID(as_uuid=True))
    mime = Column(Text)
    props = Column(JSONB)

    # Relationships
    thread = relationship("Thread", back_populates="elements")


class Feedback(Base):
    """Chainlit feedbacks table"""

    __tablename__ = "feedbacks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    forId = Column(UUID(as_uuid=True), nullable=False)
    threadId = Column(UUID(as_uuid=True), ForeignKey("threads.id"), nullable=False)
    value = Column(Integer, nullable=False)
    comment = Column(Text)

    # Relationships
    thread = relationship("Thread", back_populates="feedbacks")
