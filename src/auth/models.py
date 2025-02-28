from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship
from src.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime, Text, func

class User(Base, SQLAlchemyBaseUserTable[int]):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column("username", String, unique=True, nullable=False)
    hashed_password = Column("password", String, nullable=False)
    time = Column("registered_at", DateTime(timezone=True), server_default=func.now())
    email = Column(String, unique=True, index=True, nullable=False)
    role_id = Column("role_id", Integer, ForeignKey("role.id"))

class Role(Base):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    permissions = Column("permission", JSON)


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    agent_id = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to fetch associated messages
    messages = relationship("ChatMessage", back_populates="session")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # e.g., "user" or "assistant"
    content = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ChatSession", back_populates="messages")

class UserSettings(Base):
    __tablename__ = "user_settings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    settings = Column(JSON, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())