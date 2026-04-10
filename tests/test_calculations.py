import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from app.models import Calculation, OperationType, User
from app.schemas import CalculationCreate
from app.factory import CalculationFactory
from app.database import Base

# --- Database Setup for Integration Tests ---
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/test_db"
)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    yield session
    session.close()

# --- Unit Tests: Factory ---
def test_factory_operations():
    assert CalculationFactory.compute(5, 3, OperationType.ADD) == 8.0
    assert CalculationFactory.compute(10, 4, OperationType.SUB) == 6.0
    assert CalculationFactory.compute(5, 5, OperationType.MULTIPLY) == 25.0
    assert CalculationFactory.compute(10, 2, OperationType.DIVIDE) == 5.0

def test_factory_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero!"):
        CalculationFactory.compute(10, 0, OperationType.DIVIDE)

# --- Unit Tests: Pydantic Validation ---
def test_calculation_create_valid():
    calc = CalculationCreate(a=10, b=5, type=OperationType.ADD)
    assert calc.a == 10
    assert calc.type == "Add"

def test_calculation_create_divide_by_zero():
    with pytest.raises(ValidationError, match="Division by zero is not allowed"):
        CalculationCreate(a=10, b=0, type=OperationType.DIVIDE)

def test_calculation_create_invalid_type():
    with pytest.raises(ValidationError):
        CalculationCreate(a=10, b=5, type="Modulus")

# --- Integration Tests: Database ---
def test_insert_calculation_record(db_session):
    # 1. Create User
    test_user = User(username="calcuser", email="calc@test.com", password_hash="hash")
    db_session.add(test_user)
    db_session.commit()

    # 2. Validate input via Schema
    calc_in = CalculationCreate(a=15, b=5, type=OperationType.DIVIDE, user_id=test_user.id)
    
    # 3. Compute result via Factory
    result = CalculationFactory.compute(calc_in.a, calc_in.b, calc_in.type)

    # 4. Insert into Database
    db_calc = Calculation(
        a=calc_in.a, 
        b=calc_in.b, 
        type=calc_in.type, 
        result=result, 
        user_id=calc_in.user_id
    )
    db_session.add(db_calc)
    db_session.commit()
    db_session.refresh(db_calc)

    # 5. Assertions
    assert db_calc.id is not None
    assert db_calc.result == 3.0
    assert db_calc.user_id == test_user.id