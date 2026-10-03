from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from langchain.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from mysite.database.schema import ChatResponse, ChatRequest
from .dependencies import get_current_user, get_db
from mysite.database.models import UserProfile, StatusChoices, ChatCount

ai_chat_router = APIRouter(prefix="/ai_chat", tags=["AI Chat"])

model = ChatOllama(model='llama3.2', temperature=0)

PROMPT = (
    'Ты опытный senior python-разработчик с 10 летним опытом работы. '
    'Ты должен отвечать на вопросы кратко и с примерами. '
    'Пиши кратко, максимум 5 предложений.'
)


@ai_chat_router.post('/chat_gpt/', response_model=ChatResponse)
async def ai_chat1(data: ChatRequest, current_user: UserProfile = Depends(get_current_user)):
    if not data.question or not data.question.strip():
        raise HTTPException(status_code=400, detail='Пустое сообщение нельзя отправить')

    if current_user.status == StatusChoices.basic:
        raise HTTPException(status_code=403, detail='Функция доступна только по PRO подписке')

    messages = [SystemMessage(content=PROMPT), HumanMessage(content=data.question)]
    response = await model.ainvoke(messages)

    return ChatResponse(answer=response.content)


@ai_chat_router.post('/gemini/', response_model=ChatResponse)
async def ai_chat2(data: ChatRequest, current_user: UserProfile = Depends(get_current_user), db: Session = Depends(get_db)):
    if not data.question or not data.question.strip():
        raise HTTPException(status_code=400, detail='Пустое сообщение нельзя отправить')

    if current_user.status == StatusChoices.basic:
        count = db.query(ChatCount).filter(ChatCount.user_id == current_user.id).first()
        if count is None:
            count = ChatCount(user_id=current_user.id, requests_count=0)
            db.add(count)
            db.commit()
            db.refresh(count)

        if count.requests_count >= 1:
            raise HTTPException(status_code=402, detail='Бесплатный лимит исчерпан. Оформите PRO подписку')

        count.requests_count += 1
        count.last_request_date = datetime.now()
        db.commit()

    messages = [SystemMessage(content=PROMPT), HumanMessage(content=data.question)]
    response = await model.ainvoke(messages)

    return ChatResponse(answer=response.content)