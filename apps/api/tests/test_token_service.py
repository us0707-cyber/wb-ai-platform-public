from src.services.token_service import decrypt_token, encrypt_token


def test_token_roundtrip():
    encrypted = encrypt_token("secret-token")
    assert encrypted != "secret-token"
    assert decrypt_token(encrypted) == "secret-token"


def test_empty_token_roundtrip():
    assert encrypt_token("") == ""
    assert decrypt_token("") == ""
