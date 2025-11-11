import logging
import chainlit as cl

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable, RunnableConfig

import requests
from typing import cast
from app.utils.jwt import decode_access_token

from urllib.parse import urlparse, parse_qs
import httpx

# 로거 수준 설정
# logging.getLogger("uvicorn").setLevel(logging.ERROR)
# logging.getLogger("uvicorn.access").setLevel(logging.ERROR)

def get_username_from_cookie(token):
  payload = decode_access_token(token)
  print(payload)
  return payload.get("name") if payload else "anonymous"


# @cl.on_chat_start
# async def on_chat_start():
#   # ctx = cl.context
#   # headers = dict(ctx.metadata.get("headers", {}))
#   # cookies = headers.get("cookie")

#   # await cl.Message(content=f"🍪 WebSocket Cookie 헤더:\n{cookies}").send()

#   user_session = cl.user_session.get("request")
#   print('dddd', user_session)
#   print('asdfasdf', vars(cl.user_session))
#   cookies = cl.user_session.get("access_token")
#   token = cookies.get("access_token") if cookies else None
#   print('쿠키', cl.user_session.get("access_token"))
  
#   if not token:
#     await cl.Message("로그인이 필요합니다. 로그인 페이지로 이동합니다.").send()
#     return 

#   user_info = get_username_from_cookie(token)
#   if not user_info:
#     await cl.Message("유효하지 않은 토큰입니다. 로그인 페이지로 이동합니다.").send()
#     await cl.redirect("http://localhost:8000")
#     return

#   # Chainlit 세션에 사용자 정보 저장
#   cl.user_session.set("id", user_info["id"])
#   cl.user_session.set("name", user_info["name"])

#   await cl.Message(f"안녕하세요, {user_info['name']}님!").send()

#   model = ChatOpenAI(streaming=True)
#   prompt = ChatPromptTemplate.from_messages(
#     [
#       (
#         "system",
#         "You're a very knowledgeable historian who provides accurate and eloquent answers to historical questions.",
#       ),
#       ("human", "{question}"),
#     ]
#   )
#   runnable = prompt | model | StrOutputParser()
#   cl.user_session.set("runnable", runnable)

FASTAPI_BASE = "http://localhost:8000"  # FastAPI 서버 주소

@cl.on_chat_start
async def on_chat_start():
	token = None
	# custom_js.js에서 주입한 세션 접근
	if hasattr(cl.user_session, "get"):
		token = cl.user_session.get("token")

	if not token:
		await cl.Message(content="❌ 인증 토큰이 없습니다. 다시 로그인하세요.").send()
		await cl.run_sync(cl.disconnect)
		return

	# FastAPI에 토큰 검증 요청
	resp = requests.post(f"{FASTAPI_BASE}/verify-token", json={"token": token})

	if resp.status_code != 200:
			await cl.Message(content="❌ 토큰이 유효하지 않습니다. 다시 로그인해주세요.").send()
			await cl.run_sync(cl.disconnect)
			return

	user = resp.json()["user"]
	await cl.Message(content=f"✅ 인증 성공! 환영합니다, {user}님!").send()


@cl.on_message
async def on_message(message: cl.Message):
  runnable = cast(Runnable, cl.user_session.get("runnable"))  # type: Runnable

  msg = cl.Message(content="")

  async for chunk in runnable.astream(
      {"question": message.content},
      config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
  ):
      await msg.stream_token(chunk)

  await msg.send()