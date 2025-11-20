from fastapi import APIRouter, Request, Response
from fastapi.templating import Jinja2Templates
from app.utils.jwt import verify_password, create_access_token
from app.config.config import settings
from datetime import datetime, timedelta

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

@router.post("/login")
async def login(request: Request, response: Response):
  users = request.app.state.users

  data = await request.json()
  id = data['id']
  password = data['password']

  if not id or not password:
    return { "error": "아이디 혹은 비밀번호를 입력해주세요" }

  user = users.find_one({"id": id})

  if not user or not verify_password(password, user["password"]):
    return { "error": "아이디 혹은 비밀번호를 확인해주세요" }

  token = create_access_token({"id": id, "name": user["name"]})
  response.set_cookie(
    key="access_token",
    value=token,
    max_age=settings.JWT_EXPIRE_MINUTES * 60,
    secure=False,
    httponly=True, 
    samesite="Lax",
    path="/"
  )

  now = datetime.now()
  after_60min = now + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)

  find = {"id": id}
  updateQuery = {
    "$set": {
      "token": {
        "used": 0,
        "expire": after_60min
      },
      "lastLogin": now
    }
  }
  users.update_one(find, updateQuery)

  return { "result": "ok" }
