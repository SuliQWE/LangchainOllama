import uvicorn
from fastapi import FastAPI
from mysite.api import auth, agent
# from mysite.api import file_json
from mysite.api import file_upload, api_ollama, pdd_gemini
from mysite.admin.setup import setup_admin

app = FastAPI(title="AIDataCheck — Auth Service")
app.include_router(auth.auth_router)
app.include_router(agent.ai_chat_router)
app.include_router(api_ollama.ollama_router)
app.include_router(file_upload.file_router)
app.include_router(pdd_gemini.gemini_router)
setup_admin(app)


if __name__ == "__main__":
    uvicorn.run(app, host='127.0.0.1', port=8000)