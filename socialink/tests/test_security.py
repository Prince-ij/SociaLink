import pytest
from jose import jwt

from socialink import security
from socialink.security import get_password_hash, get_user, verify_password


def test_access_token_expire_minutes():
    assert security.access_token_expire_minutes() == 30


def test_confirm_token_expire_minutes():
    assert security.confirm_token_expire_minutes() == 1440


def test_create_access_token():
    token = security.create_access_token("123")
    assert {"sub": "123", "type": "access"}.items() <= jwt.decode(
        token, key=security.SECRET_KEY, algorithms=[security.ALGORITHM]
    ).items()


def test_create_confirmation_token():
    token = security.create_confirmation_token("123")
    assert {"sub": "123", "type": "confirmation"}.items() <= jwt.decode(
        token, key=security.SECRET_KEY, algorithms=[security.ALGORITHM]
    ).items()


@pytest.mark.anyio
def test_password_hash():
    password = "testpasswd"

    assert verify_password(password, get_password_hash(password))


@pytest.mark.anyio
def test_get_subject_for_token_type_valid_confirmation():
    email = "test@example.com"
    token = security.create_confirmation_token(email)

    assert email == security.get_subject_for_token_type(token, "confirmation")


@pytest.mark.anyio
def test_get_subject_for_token_type_valid_access():
    email = "test@example.com"
    token = security.create_access_token(email)

    assert email == security.get_subject_for_token_type(token, "access")


@pytest.mark.anyio
async def test_get_subject_for_token_type_expired(mocker):
    mocker.patch("socialink.security.confirm_token_expire_minutes", return_value=-1)
    email = "test@example.com"
    token = security.create_confirmation_token(email)

    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "access")

    assert "Token has expired" == exc_info.value.detail


@pytest.mark.anyio
async def test_get_subject_for_token_type_missing_sub():
    email = "test@example.com"
    token = security.create_access_token(email)

    payload = jwt.decode(
        token, key=security.SECRET_KEY, algorithms=[security.ALGORITHM]
    )
    del payload["sub"]

    token = jwt.encode(payload, key=security.SECRET_KEY, algorithm=security.ALGORITHM)

    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "access")

    assert "Token is missing 'sub' field" == exc_info.value.detail


@pytest.mark.anyio
async def test_get_subject_for_token_type_wrong_type():
    email = "test@example.com"
    token = security.create_access_token(email)

    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "confirmation")


@pytest.mark.anyio
async def test_get_subject_for_token_invalid_token():
    token = "Invalid token"

    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "access")

    assert "Invalid token" == exc_info.value.detail


@pytest.mark.anyio
async def test_get_user(registered_user: dict):
    user = await get_user(registered_user["email"])

    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_get_user_not_found():
    user = await get_user("tinubu@gmail.com")

    assert user is None


@pytest.mark.anyio
async def test_authenticate_user(confirmed_user: dict):
    user = await security.authenticate_user(
        confirmed_user["email"], confirmed_user["password"]
    )

    assert user.email == confirmed_user["email"]


@pytest.mark.anyio
async def test_authenticate_user_not_found():
    with pytest.raises(security.HTTPException):
        await security.authenticate_user("balablue@email", "tinubu")


@pytest.mark.anyio
async def test_authenticate_user_wrong_password(registered_user: dict):
    with pytest.raises(security.HTTPException):
        await security.authenticate_user(registered_user["email"], "tinubu")


@pytest.mark.anyio
async def test_get_current_user(registered_user: dict):
    token = security.create_access_token(registered_user["email"])
    user = await security.get_current_user(token)

    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_get_current_user_invalid_token():
    with pytest.raises(security.HTTPException):
        await security.get_current_user("Invalid Token")


@pytest.mark.anyio
async def test_get_current_user_with_wrong_access_token(registered_user: dict):
    token = security.create_confirmation_token(registered_user["email"])

    with pytest.raises(security.HTTPException):
        await security.get_current_user(token)
