from fastapi import FastAPI
from app.db.mongo import lifespan
from app.api.routes import auth

app = FastAPI(title="Chat App", lifespan=lifespan)

# 라우터 등록
app.include_router(auth.router, tags=["Auth"])
