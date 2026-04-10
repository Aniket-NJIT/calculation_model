from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.database import Base

class OperationType(str, enum.Enum):
    ADD = "Add"
    SUB = "Sub"
    MULTIPLY = "Multiply"
    DIVIDE = "Divide"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship to calculations
    calculations = relationship("Calculation", back_populates="user", cascade="all, delete-orphan")

class Calculation(Base):
    __tablename__ = "calculations"

    id = Column(Integer, primary_key=True, index=True)
    a = Column(Float, nullable=False)
    b = Column(Float, nullable=False)
    type = Column(SQLEnum(OperationType), nullable=False)
    result = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Foreign key to the User model
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    # Relationship back to user
    user = relationship("User", back_populates="calculations")