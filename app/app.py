from fastapi import FastAPI
from app.db.mongo import lifespan
from app.routes import auth, user
from chainlit.utils import mount_chainlit

app = FastAPI(title="Chat App", lifespan=lifespan)

mount_chainlit(app=app, target="app/utils/chainlit.py", path="/chainlit")

# 라우터 등록
app.include_router(user.router, tags=["User"])
app.include_router(auth.router, tags=["Auth"])
