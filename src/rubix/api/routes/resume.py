from fastapi import APIRouter
import logging

logging.basicConfig(level=logging.INFO, format="[TIL] %(name)s - %(message)s")
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resume", tags=["resume"])
