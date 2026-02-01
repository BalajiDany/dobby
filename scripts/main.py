import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI

from scripts.backup import postgres_backup, postgres_restore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# This handles the startup and shutdown of the scheduler automatically
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(postgres_backup.run, trigger=CronTrigger(hour="1"))  # Every day @ 01 AM
    scheduler.start()
    yield  # The FastAPI application serves requests here
    scheduler.shutdown()


app = FastAPI(title="FastAPI", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "OK"}


@app.get("/backup")
async def backup():
    await postgres_backup.run()
    return {"status": "OK"}


@app.get("/restore/{date}")
async def restore(date: str):
    await postgres_restore.run(date)
    return {"status": "OK"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
