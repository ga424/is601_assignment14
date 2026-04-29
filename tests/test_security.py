from datetime import timedelta

from app.security import create_access_token, decode_access_token, hash_password, verify_password


def test_hash_password_returns_non_plaintext_value():
    plain = "supersecure123"
    hashed = hash_password(plain)

    assert hashed != plain
    assert hashed


def test_verify_password_accepts_correct_password():
    plain = "supersecure123"
    hashed = hash_password(plain)

    assert verify_password(plain, hashed) is True


def test_verify_password_rejects_incorrect_password():
    hashed = hash_password("supersecure123")

    assert verify_password("wrongpassword", hashed) is False


def test_create_access_token_round_trips_claims():
    token = create_access_token("user-123", "student@example.com", timedelta(minutes=5))
    payload = decode_access_token(token)

    assert payload["sub"] == "user-123"
    assert payload["email"] == "student@example.com"
