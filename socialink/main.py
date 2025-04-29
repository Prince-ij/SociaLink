import logging
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler

from socialink.database import database
from socialink.logging_conf import configure_logging
from socialink.routers.post import router as post_router
from socialink.routers.upload import router as upload_router
from socialink.routers.user import router as user_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)

app.add_middleware(CorrelationIdMiddleware)
app.include_router(post_router)
app.include_router(upload_router)
app.include_router(user_router)


@app.exception_handler
async def http_exception_handle_logging(request, exc):
    logger.error(f"HTPP Exception: {exc.status_code} - {exc.detail}")
    return await http_exception_handler(request, exc)
