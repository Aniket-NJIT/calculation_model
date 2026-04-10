from pydantic import BaseModel, EmailStr, model_validator, ConfigDict
from datetime import datetime
from typing import Optional
from app.models import OperationType # Import the Enum

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- New Calculation Schemas ---

class CalculationBase(BaseModel):
    a: float
    b: float
    type: OperationType

class CalculationCreate(CalculationBase):
    user_id: Optional[int] = None

    @model_validator(mode='after')
    def validate_division(self):
        if self.type == OperationType.DIVIDE and self.b == 0:
            raise ValueError("Division by zero is not allowed.")
        return self

class CalculationRead(CalculationBase):
    id: int
    result: float
    user_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)