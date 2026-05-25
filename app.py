import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn

from memory.vector_db import LongTermMemory
from core.multi_agent_system import MultiAgentSystem
from tools.os_agent import actually_execute_command

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
        messages = ns.run(req.message)
        # Mesajları seri hale getir (Frontend için)
        response_list = []
        for msg in messages:
            # İsim tespiti (LangChain farklı yerlerde tutabiliyor)
            agent_name = getattr(msg, "name", None)
            if not agent_name and "name" in msg.additional_kwargs:
                agent_name = msg.additional_kwargs["name"]
            
            if not agent_name:
                agent_name = "Supervisor" # Varsayılan

            response_list.append({
                "agent": agent_name,
                "content": msg.content
            })
        return {"status": "success", "responses": response_list}
    except Exception as e:
        print(f"Sunucu Hatası: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

@app.post("/api/evolve")
def evolve_endpoint():
    """Tetiklendiğinde gece optimizasyon (öğrenme) döngüsünü başlatır."""
    if not ns:
        return {"status": "error", "message": "Sistem hazır değil."}
    
    try:
        report = ns.evolve()
        return {"status": "success", "report": report}
    except Exception as e:
        return {"status": "error", "message": str(e)}

class ExecuteRequest(BaseModel):
    command: str

@app.post("/api/execute_approved")
def execute_approved_endpoint(req: ExecuteRequest):
    """Sadece kullanıcı arayüzden onayladığında çalışır."""
    try:
        # Arka planda güvenli (sandbox içinde) çalıştır ve sonucu al
        result = actually_execute_command(req.command)
        
        # Sonucu direkt sohbete geri dönmek için MultiAgentSystem'in chat'ine enjekte edeceğiz
        # Bunu başarmak için yapay zekaya "Komut onaylandı ve sonucu bu:" şeklinde bir mesaj yolluyoruz
        if ns:
            ns.run(f"[SİSTEM BİLDİRİMİ] Kullanıcı komutu onayladı. Komut Sonucu:\n{result}\n(Bunu kullanıcıya kısaca bildir.)")
            
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
