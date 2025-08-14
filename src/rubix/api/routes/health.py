import os
import logging
import psutil
from fastapi import APIRouter
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO, format="[TIL] %(name)s - %(message)s")
logger = logging.getLogger(__name__)


router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "/liveness",
    tags=["Health"],
    description="Health check endpoint to determine if the service is running",
)
def liveness():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()

    logger.debug(f"Health check: PID {os.getpid()} is alive")

    return JSONResponse(
        content={
            "message": "alive",
            "pid": os.getpid(),
            "ram": f"{memory_info.rss / (1024**2)}",
            "success": True,
        }
    )


@router.get(
    "/readiness",
    tags=["Health"],
    description="Health check endpoint to determine if the service is ready to serve traffic",
)
def readiness():
    logger.debug("Health check: Service is ready")

    return JSONResponse(content={"status": "ready"})
