import pytest
from pydantic import ValidationError

from app.schema import CalculationCreate, CalculationType, UserCreate, UserLogin


def test_schema_accepts_valid_payload():
    payload = {"type": "addition", "inputs": [1, 2, 3]}
    schema = CalculationCreate(**payload)
    assert schema.type == CalculationType.ADDITION
    assert schema.inputs == [1.0, 2.0, 3.0]


def test_schema_rejects_invalid_type():
    with pytest.raises(ValidationError):
        CalculationCreate(type="modulo", inputs=[1, 2])


def test_schema_rejects_insufficient_inputs():
    with pytest.raises(ValidationError):
        CalculationCreate(type="addition", inputs=[1])


def test_schema_rejects_division_by_zero_denominator():
    with pytest.raises(ValidationError):
        CalculationCreate(type="division", inputs=[10, 0])


def test_user_create_normalizes_email():
    schema = UserCreate(email=" Student@Example.com ", password="strongpassword123")

    assert schema.email == "student@example.com"


def test_user_create_rejects_bad_email():
    with pytest.raises(ValidationError):
        UserCreate(email="not-an-email", password="strongpassword123")


def test_user_login_rejects_short_password():
    with pytest.raises(ValidationError):
        UserLogin(email="student@example.com", password="short")
