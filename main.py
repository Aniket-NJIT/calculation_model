from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from app.operations import add, subtract, multiply, divide 
import uvicorn
import logging

# New imports for the User Assignment
from app.database import engine, Base, get_db
from app.models import User
from app.schemas import UserCreate, UserRead
from app.security import get_password_hash



# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Create Database Tables ---
# This creates the tables in PostgreSQL if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Pydantic model for request data
class OperationRequest(BaseModel):
    a: float = Field(..., description="The first number")
    b: float = Field(..., description="The second number")

    @field_validator('a', 'b')
    def validate_numbers(cls, value):
        if not isinstance(value, (int, float)):
            raise ValueError('Both a and b must be numbers.')
        return value

# Pydantic model for successful response
class OperationResponse(BaseModel):
    result: float = Field(..., description="The result of the operation")

# Pydantic model for error response
class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")

# Custom Exception Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTPException on {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Extracting error messages
    error_messages = "; ".join([f"{err['loc'][-1]}: {err['msg']}" for err in exc.errors()])
    logger.error(f"ValidationError on {request.url.path}: {error_messages}")
    return JSONResponse(
        status_code=400,
        content={"error": error_messages},
    )

@app.get("/")
async def read_root(request: Request):
    """
    Serve the index.html template.
    """
    return templates.TemplateResponse(request, "index.html")

@app.post("/add", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def add_route(operation: OperationRequest):
    """
    Add two numbers.
    """
    try:
        result = add(operation.a, operation.b)
        logger.info(f"Successfully added {operation.a} and {operation.b}. Result: {result}") ## to enhance logging
        return OperationResponse(result=result)
    except Exception as e:
        logger.error(f"Add Operation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/subtract", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def subtract_route(operation: OperationRequest):
    """
    Subtract two numbers.
    """
    try:
        result = subtract(operation.a, operation.b)
        logger.info(f"Successfully subtracted {operation.a} and {operation.b}. Result: {result}") ## to enhance logging
        return OperationResponse(result=result)
    except Exception as e:
        logger.error(f"Subtract Operation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/multiply", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def multiply_route(operation: OperationRequest):
    """
    Multiply two numbers.
    """
    try:
        result = multiply(operation.a, operation.b)
        logger.info(f"Successfully multiplied {operation.a} and {operation.b}. Result: {result}") ## to enhance logging
        return OperationResponse(result=result)
    except Exception as e:
        logger.error(f"Multiply Operation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/divide", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def divide_route(operation: OperationRequest):
    """
    Divide two numbers.
    """
    try:
        result = divide(operation.a, operation.b)
        logger.info(f"Successfully divided {operation.a} and {operation.b}. Result: {result}") ## to enhance logging
        return OperationResponse(result=result)
    except ValueError as e:
        logger.error(f"Divide Operation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Divide Operation Internal Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# --- New User Routes ---
@app.post("/users/", response_model=UserRead, status_code=201)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user and securely hash their password.
    """
    # Check if username or email already exists
    existing_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    # Hash the password
    hashed_password = get_password_hash(user.password)
    
    # Create the SQLAlchemy model instance
    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password
    )
    
    # Save to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"Successfully created user: {new_user.username}")
    return new_user

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)