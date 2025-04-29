import logging

from fastapi import APIRouter, HTTPException, status, Request, BackgroundTasks

from socialink import tasks

from socialink.database import database, users_table
from socialink.models.user import UserIn
from socialink.security import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    create_confirmation_token,
    get_user,
    get_subject_for_token_type,
)

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/register", status_code=201)
async def register(user: UserIn, background_tasks: BackgroundTasks, request: Request):
    if await get_user(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with that email already exists",
        )

    hashed_password = get_password_hash(user.password)
    query = users_table.insert().values(email=user.email, password=hashed_password)

    logger.debug(query)

    await database.execute(query)
    background_tasks.add_task(
        tasks.send_user_registration_email,
        user.email,
        confirmation_url=request.url_for(
            "confirm_email", token=create_confirmation_token(user.email)
        ),
    )

    return {
        "detail": "User created. Please confirm your email",
    }


@router.post("/token")
async def login(user: UserIn):
    user = await authenticate_user(user.email, user.password)
    access_token = create_access_token(user.email)
    logger.info(f"Access Token {access_token}")
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/confirm/{token}")
async def confirm_email(token: str):
    email = get_subject_for_token_type(token, "confirmation")
    query = (
        users_table.update().where(users_table.c.email == email).values(confirmed=True)
    )

    logger.debug(query)

    await database.execute(query)
    return {"detail": "User confirmed"}
