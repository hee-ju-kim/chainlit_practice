import chainlit as cl
import os, json
from app.utils.security import decode_access_token
from fastapi.responses import RedirectResponse

CHAT_DIR = "chat_history"
if not os.path.exists(CHAT_DIR):
  os.makedirs(CHAT_DIR)

def get_username_from_cookie(token):
  payload = decode_access_token(token)
  print(payload)
  return payload.get("sub") if payload else "anonymous"

def get_user_history_file(username):
  return os.path.join(CHAT_DIR, f"{username}.json")

def load_history(username):
  path = get_user_history_file(username)
  if os.path.exists(path):
    with open(path, "r", encoding="utf-8") as f:
      return json.load(f)
  return []

def save_history(username, history):
  path = get_user_history_file(username)
  with open(path, "w", encoding="utf-8") as f:
    json.dump(history, f, ensure_ascii=False, indent=2)

@cl.on_chat_start
async def on_start():
  print(cl.user_session)
  token = cl.user_session.get("token")

  if not token:
    await cl.Message("로그인이 필요합니다. 로그인 페이지로 이동합니다.").send()
    response = RedirectResponse(url="http://localhost:8000", status_code=303)
    return response

  user_info = get_username_from_cookie(token)
  if not user_info:
    await cl.Message("유효하지 않은 토큰입니다. 로그인 페이지로 이동합니다.").send()
    await cl.redirect("http://localhost:8000")
    return

  # Chainlit 세션에 사용자 정보 저장
  cl.user_session.set("id", user_info["id"])
  cl.user_session.set("name", user_info["name"])

  await cl.Message(f"안녕하세요, {user_info['name']}님!").send()

  history = load_history(user_info["id"])
  if history:
    await cl.Message(content="📜 이전 대화를 불러왔습니다.").send()
    for msg in history:
      await cl.Message(author=msg["author"], content=msg["content"]).send()
  else:
    await cl.Message(content="새로운 대화를 시작합니다!").send()

@cl.on_message
async def on_message(message: cl.Message):
  username = cl.user_session.get("username", "anonymous")
  user_msg = message.content
  response = f"{username}님, '{user_msg}'에 대한 답변입니다 😊"

  history = load_history(username)
  history.append({"author": username, "content": user_msg})
  history.append({"author": "bot", "content": response})
  save_history(username, history)

  await cl.Message(content=response).send()
