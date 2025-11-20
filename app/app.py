from fastapi import FastAPI
from app.db.mongo import lifespan
from chainlit.utils import mount_chainlit

app = FastAPI(title="Chat App", lifespan=lifespan)

mount_chainlit(app=app, target="app/utils/chainlit.py", path="/")
