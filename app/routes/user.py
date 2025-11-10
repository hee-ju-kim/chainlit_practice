from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.utils.jwt import hash_password, verify_password, create_access_token
from app.config.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@router.post("/login")
async def login(request: Request, id: str = Form(...), password: str = Form(...)):
  print('asdfasdf')
  users = request.app.state.users


  user = users.find_one({"id": id})

  if not user or not verify_password(password, user["password"]):
    return templates.TemplateResponse("login.html", {"request": request, "error": "아이디 또는 비밀번호가 틀렸습니다."})

  token = create_access_token({"sub": id, "name": user["name"]})
  maxAge = settings.JWT_EXPIRE_MINUTES * 60
  print('asdfasdf')
  response = RedirectResponse(url="http://localhost:8000/chainlit")
  response.set_cookie(
    key="access_token",
    value=token,
    max_age=maxAge,
    secure=False,
    httponly=True, 
    samesite="Lax" 
  )
  return response


@router.post("/signup")
async def signup(id: str = Form(...), password: str = Form(...), request: Request = None):
  users = request.app.state.users
  if users.find_one({"id": id}):
    raise HTTPException(status_code=400, detail="이미 존재하는 사용자입니다.")

  hashed_pw = hash_password(password)
  users.insert_one({"id": id, "password": hashed_pw})
  return {"msg": "회원가입 성공"}