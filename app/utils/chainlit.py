import logging
import chainlit as cl

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable, RunnableConfig
from typing import Optional

from http.cookies import SimpleCookie

from typing import cast
from app.utils.jwt import decode_access_token

from fastapi import Request


# 로거 수준 설정
logging.getLogger("uvicorn").setLevel(logging.ERROR)
logging.getLogger("uvicorn.access").setLevel(logging.ERROR)

def get_username_from_cookie(token):
  payload = decode_access_token(token)
  print(payload)
  return payload.get("name") if payload else "anonymous"

@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None


# @cl.on_chat_start
# async def on_chat_start(req: Request):
#   # ctx = cl.context
#   # headers = dict(ctx.metadata.get("headers", {}))
#   # cookies = headers.get("cookie")

#   # await cl.Message(content=f"🍪 WebSocket Cookie 헤더:\n{cookies}").send()

#   user_session = cl.user_session.get("request")
#   print(req)
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