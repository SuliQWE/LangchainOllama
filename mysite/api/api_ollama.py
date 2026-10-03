from fastapi import APIRouter
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from time import perf_counter
from pydantic import BaseModel

ollama_router = APIRouter(prefix="/ollama", tags=["ollama"])

MODEL_NAME = "llama3.2:latest"


class Request(BaseModel):
    prompt: str
    temperature: float
    top_k: int
    top_p: float
    seed: int


class Response(BaseModel):
    answer: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    time_seconds: float
    model: str
    done_reason: str | None = None


@ollama_router.post("/ollama/", response_model=Response)
def ollama(data: Request):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Ты полезный AI-ассистент. Отвечай понятно и по делу, "
                "приводи примеры кода там, где это уместно."
            ),
            (
                "human",
                "{prompt}"
            ),
        ]
    )

    model = ChatOllama(
        model=MODEL_NAME,
        temperature=data.temperature,
        top_k=data.top_k,
        top_p=data.top_p,
        seed=data.seed,
    )

    chain = prompt | model

    start = perf_counter()
    response = chain.invoke({"prompt": data.prompt})
    seconds = perf_counter() - start

    usage = getattr(response, "usage_metadata", None) or {}
    meta = getattr(response, "response_metadata", None) or {}

    return Response(
        answer=response.content,
        input_tokens=usage.get("input_tokens"),
        output_tokens=usage.get("output_tokens"),
        total_tokens=usage.get("total_tokens"),
        time_seconds=seconds,
        model=MODEL_NAME,
        done_reason=meta.get("done_reason"),
    )