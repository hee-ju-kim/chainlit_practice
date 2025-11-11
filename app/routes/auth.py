from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import JSONResponse
from app.utils.jwt import decode_access_token
from app.config.config import settings
import secrets
import redis

router = APIRouter()

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, decode_responses=True)
EPHEMERAL_TTL = settings.REDIS_EXPIRE

# ---------------------------
# 에페메럴 토큰 발급
# ---------------------------
@router.get("/auth/ephemeral")
def get_ephemeral(request: Request):
  access_token = request.cookies.get("access_token")
  if not access_token:
    raise HTTPException(status_code=401, detail="no access token")

  # jwt 토큰검증
  loginInfo = decode_access_token(access_token)
  print(loginInfo)

  if not loginInfo:
    raise HTTPException(status_code=401, detail="invalid token")

  ip = request.client.host if request.client else ""
  ua = request.headers.get("user-agent", "")
  ephemeral = secrets.token_urlsafe(32)

  # Redis에 저장
  key = f"ephemeral:{ephemeral}"
  r.hset(
      key,
      mapping={
          "token": access_token,
          "ip": ip,
          "ua": ua,
      },
  )
  r.expire(key, EPHEMERAL_TTL)

  return JSONResponse({"ephemeral_token": ephemeral, "ttl": EPHEMERAL_TTL})

# ---------------------------
# 에페메럴 토큰 검증
# ---------------------------
@router.post("/auth/verify-token")
async def verify_ephemeral_token(data: dict):
    token = data.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="Token missing")

    user = r.get(f"ephemeral:{token}")
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # 1회용 처리
    r.delete(f"ephemeral:{token}")
    return {"status": "ok", "user": user}