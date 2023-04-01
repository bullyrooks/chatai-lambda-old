from fastapi import FastAPI
from chat import Chat
import logging

app = FastAPI()
logger = logging.getLogger("main")


@app.get("/chat")
async def root():
    logger.info("http request in")
    return Chat.getMessage()
