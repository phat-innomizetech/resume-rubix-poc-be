from contextlib import asynccontextmanager
import logging
import logging.config
import asyncio

from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from rubix.api.main import api_router
from rubix.core.config import settings
from rubix.helpers.exception_handler import (
    CustomException,
    http_exception_handler,
)

# from rubix.message.subscriber import Subscriber

logging.config.fileConfig(settings.LOGGING_CONFIG_FILE, disable_existing_loggers=False)
logging.getLogger().setLevel(level=settings.ENV_LOG_LEVEL)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[TIL] %(name)s - %(message)s")


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


# # Global variables to manage subscriber lifecycle
# subscriber_task = None
# subscriber_instance = None


# @asynccontextmanager
# async def lifespan(_: FastAPI):
#     global subscriber_task, subscriber_instance

#     logger.info("FastAPI application startup - starting subscriber...")

#     # Start subscriber
#     try:
#         consumer_binding = ["book.#"]  # Listen to all book events
#         subscriber_instance = Subscriber(binding_keys=consumer_binding)
#         try:
#             await subscriber_instance.connect()
#         except ConnectionRefusedError as e:
#             logger.error(f"Connection refuse from sub: {e}")
#         subscriber_task = asyncio.create_task(subscriber_instance.start_consuming())
#         logger.info("Subscriber started successfully")
#     except Exception as e:
#         logger.warning(f"Failed to start subscriber: {e}")
#         logger.warning("Application will run without message queue functionality")
#         subscriber_instance = None
#         subscriber_task = None

#     yield

#     logger.info("FastAPI application shutdown - stopping subscriber...")

#     # Stop subscriber
#     if subscriber_task:
#         subscriber_task.cancel()
#         try:
#             await subscriber_task
#             logger.info("Subscriber task cancelled successfully")
#         except asyncio.CancelledError:
#             logger.info("Subscriber task stopped")
#         except Exception as e:
#             logger.error(f"Error cancelling subscriber task: {e}")

#     if subscriber_instance:
#         try:
#             await subscriber_instance.close()
#             logger.info("Subscriber connection closed")
#         except Exception as e:
#             logger.error(f"Error closing subscriber: {e}")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A simple FastAPI project template",
    version=settings.API_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    # lifespan=lifespan,
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_exception_handler(CustomException, http_exception_handler)

app.include_router(api_router, prefix=settings.API_V1_STR)
