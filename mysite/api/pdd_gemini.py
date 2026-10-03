import os
import json
from time import perf_counter

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types

gemini_router = APIRouter(prefix="/pdd", tags=["pdd"])

MODEL_NAME = "gemini-3.6-flash"

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """
Ты — эксперт по дорожным знакам ПДД РФ.
Твоя единственная задача — определять дорожные знаки на фотографиях.

Правила:
1. Если на фото ЕСТЬ дорожный знак ПДД — определи его название, категорию
   (предупреждающие, приоритета, запрещающие, предписывающие,
   особых предписаний, информационные, сервиса, дополнительной информации)
   и дай краткое описание его значения.
2. Если на фото НЕТ дорожного знака (любое другое изображение) — сообщи
   об этом в поле comment, а name/category/description оставь null.
3. Отвечай СТРОГО в формате JSON, без markdown, без ```json оберток,
   без пояснений вне JSON:
{
  "is_sign": true/false,
  "name": "название знака или null",
  "category": "категория знака или null",
  "description": "описание значения знака или null",
  "comment": "краткий комментарий, если знак не найден"
}
"""


class SignResponse(BaseModel):
    is_sign: bool
    name: str | None = None
    category: str | None = None
    description: str | None = None
    comment: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    time_seconds: float
    model: str
    done_reason: str | None = None


@gemini_router.post("/predict/", response_model=SignResponse)
async def predict(
    file: UploadFile = File(...),
    temperature: float = 0.3,
    top_p: float = 0.9,
    top_k: int = 40,
    seed: int = 42,
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Файл должен быть изображением")

    image_bytes = await file.read()

    start = perf_counter()
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=file.content_type),
                "Проанализируй изображение согласно инструкции.",
            ],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                seed=seed,
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Ошибка обращения к Gemini: {e}")
    seconds = perf_counter() - start

    raw_text = (response.text or "").strip()
    raw_text = raw_text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail=f"Модель вернула некорректный JSON: {raw_text[:300]}")

    usage = getattr(response, "usage_metadata", None)
    input_tokens = getattr(usage, "prompt_token_count", None) if usage else None
    output_tokens = getattr(usage, "candidates_token_count", None) if usage else None
    total_tokens = getattr(usage, "total_token_count", None) if usage else None

    done_reason = None
    if response.candidates:
        finish_reason = response.candidates[0].finish_reason
        done_reason = finish_reason.name if hasattr(finish_reason, "name") else str(finish_reason)

    return SignResponse(
        is_sign=data.get("is_sign", False),
        name=data.get("name"),
        category=data.get("category"),
        description=data.get("description"),
        comment=data.get("comment"),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        time_seconds=seconds,
        model=MODEL_NAME,
        done_reason=done_reason,
    )