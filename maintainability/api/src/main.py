import logging
import uuid
from pathlib import Path
from typing import Dict

from fastapi import FastAPI, HTTPException

from . import config, models, utils

logger = logging.getLogger(__name__)
app = FastAPI()


@app.get("/health")
def read_root():
    return {"status": "ok"}


def api_endpoint_wrapper(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Exception occurred: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    return wrapper


@app.post("/submit_metrics")
@api_endpoint_wrapper
async def submit_metrics(metrics: Dict[str, models.CompositeMetrics]):
    utils.write_metrics(metrics)
    return {"status": "ok", "message": "Metrics submitted successfully."}


@app.post("/extract_metrics")
@api_endpoint_wrapper
async def extract_metrics(repo: Dict[str, str]):
    session_id = str(uuid.uuid4())
    composite_metrics: Dict[str, utils.CompositeMetrics] = {}
    try:
        for filepath, code in repo.items():
            if len(code.splitlines()) > config.MIN_NUM_LINES:
                composite_metrics[filepath] = utils.compose_metrics(
                    Path(filepath), code, session_id
                )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return composite_metrics
