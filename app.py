import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn

from memory.vector_db import LongTermMemory
from core.multi_agent_system import MultiAgentSystem

app = FastAPI(title="The Agency Dashboard")

# Statik dosyalar ve template ayarları
os.makedirs("templates", exist_ok=True)
templates = Jinja2Templates(directory="templates")

# AI Sistemini başlat (Global olarak)
memory = None
ns = None

@app.on_event("startup")
async def startup_event():
    global memory, ns
    print("Şirket Karargahı (Multi-Agent System) başlatılıyor...")
    memory = LongTermMemory()
    ns = MultiAgentSystem(memory)
    print("Sistem hazır!")

class ChatRequest(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/api/chat")
def chat_endpoint(req: ChatRequest):
    if not ns:
        return {"status": "error", "message": "Sistem henüz başlatılmadı."}
        
    try:
        response = ns.run(req.message)
        return {"status": "success", "response": response}
    except Exception as e:
        print(f"Sunucu Hatası: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
