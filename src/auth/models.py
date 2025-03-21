from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship
from src.database import Base
from sqlalchemy import Column, String, ForeignKey, JSON, DateTime, Text, func, Boolean
from src.gradio_ui import load_default_preset


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    username = Column("username", String, unique=True, nullable=False)
    email = Column("email", String, index=True, unique=True, nullable=False)
    hashed_password = Column("password", String, nullable=False)
    role_id = Column("role_id", UUID, ForeignKey("role.id"))
    is_active = Column("is_active", Boolean, nullable=False, default=True)
    is_verified = Column("is_verified", Boolean, nullable=False, default=False)
    time = Column("registered_at", DateTime(timezone=True), server_default=func.now(), nullable=False)

    user_settings = Column("settings_id", UUID, ForeignKey("user_settings.id"), nullable=True)
    
    
class Role(Base):
    __tablename__ = 'role'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column("name", String, index=True, unique=True, nullable=False)
    permissions = Column("permission", JSON, nullable=False)

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    agent_id = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship to fetch associated messages
    messages = relationship("ChatMessage", back_populates="session")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False)
    role_model = Column(String, nullable=False)  # e.g., "user" or "assistant"
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ChatSession", back_populates="messages")

class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    settings = Column(JSON, nullable=True, default=load_default_preset())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())