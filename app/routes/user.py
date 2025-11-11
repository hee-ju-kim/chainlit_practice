from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.utils.jwt import verify_password, create_access_token
from app.config.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
  return templates.TemplateResponse("login.html", {"request": request, "error": None})

@router.post("/login")
async def login(request: Request, id: str = Form(...), password: str = Form(...)):
  users = request.app.state.users
  user = users.find_one({"id": id})

  if not user or not verify_password(password, user["password"]):
    return templates.TemplateResponse("login.html", {"request": request, "error": "아이디 또는 비밀번호가 틀렸습니다."})

  token = create_access_token({"id": id, "name": user["name"]})
  response = RedirectResponse(url="http://localhost:8000/chainlit", status_code=303)
  response.set_cookie(
    key="access_token",
    value=token,
    max_age=settings.JWT_EXPIRE_MINUTES * 60,
    secure=False,
    httponly=True, 
    samesite="Lax" 
  )
  return response
