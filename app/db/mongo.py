from pymongo import MongoClient
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config.config import settings
from app.utils.jwt import hash_password

@asynccontextmanager
async def lifespan(app: FastAPI):
  client = MongoClient(settings.MONGO_URI)
  db = client[settings.MONGO_DB]
  users_collection = db["users"]
  chat_collection = db["chat_history"]

  # -----------------------------
  # 관리자 계정 자동 생성
  # -----------------------------
  admin_username = settings.ADMIN_USERNAME
  admin_password = settings.ADMIN_PASSWORD
  admin_user = users_collection.find_one({"id": admin_username})

  if not admin_user:
    hashed_pw = hash_password(admin_password)
    users_collection.insert_one({"id": admin_username, "password": hashed_pw, "name": "최고관리자"})
    print(f"[MongoDB] 관리자 계정 '{admin_username}' 생성 완료")

  app.state.client = client
  app.state.db = db
  app.state.users = users_collection
  app.state.chats = chat_collection

  yield

  client.close()
  print("🛑 MongoDB 연결 종료")