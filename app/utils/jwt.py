from cryptography.fernet import Fernet
from app.config.config import settings
import base64
import hashlib

# 키 생성 (환경변수 JWT_SECRET로부터 안전하게 32바이트 키 생성)
def generate_fernet_key(secret_key: str) -> bytes:
  # SHA256으로 32바이트 해시 생성 후 base64로 인코딩
  key = hashlib.sha256(secret_key.encode()).digest()
  return base64.urlsafe_b64encode(key)

FERNET_KEY = generate_fernet_key(settings.JWT_SECRET)
fernet = Fernet(FERNET_KEY)

# 암호화
def hash_password(password: str) -> str:
  token = fernet.encrypt(password.encode())
  return token.decode()

# 검증
def verify_password(password: str, hashed: str) -> bool:
  try:
    decrypted = fernet.decrypt(hashed.encode()).decode()
    return decrypted == password
  except:
    return False

# JWT 관련은 기존대로 사용
import jwt
from datetime import datetime, timedelta

def create_access_token(data: dict, expires_delta: timedelta = None):
  to_encode = data.copy()
  expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.JWT_EXPIRE_MINUTES))
  to_encode.update({"exp": expire})
  encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
  return encoded_jwt

def decode_access_token(token: str):
  try:
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    return payload
  except jwt.ExpiredSignatureError:
    return None
  except jwt.InvalidTokenError:
    return None