from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from graph import get_graph

import cv2
import base64
import ollama
import time
import threading

# FastAPI uygulamasını oluşturun
app = FastAPI()

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gelen mesajın yapısını tanımlayan bir Pydantic modeli
class Message(BaseModel):
    content: str
    type: str # 'user' veya 'ai'

# Sohbet geçmişini saklamak için model
class ChatHistory(BaseModel):
    messages: List[Message]
    kapı: str = "Kapalı"
    alarm: str = "Pasif"

# LangGraph uygulamasını bir kez derle
compiled_graph = get_graph()

# === KAMERA ANALİZİ İÇİN YENİ BÖLÜM ===
# Son analiz sonucunu tutacak global değişken
last_alarm_status = "Pasif"
# Ollama sunucusunun adresi ve modeli
ollama_host = 'http://192.168.0.94:11434'
model_name = 'qwen2.5vl'
client = ollama.Client(host=ollama_host)
# Kilitleme mekanizması (thread güvenliği için)
analysis_lock = threading.Lock()

def analyze_camera_in_background():
    """Arka planda sürekli olarak kamera görüntüsünü analiz eden fonksiyon."""
    global last_alarm_status
    print("Kamera analiz thread'i başlatılıyor...")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Hata: Kamera açılamadı.")
        last_alarm_status = "Hata"
        return

    while True:
        with analysis_lock:
            ret, frame = cap.read()
            if not ret:
                print("Hata: Kare yakalanamadı.")
                time.sleep(1)
                continue

            # Görüntüyü base64 formatına çevir
            _, buffer = cv2.imencode('.jpg', frame)
            image_base64 = base64.b64encode(buffer).decode('utf-8')

            # Tehlike tespiti için prompt
            prompt_text = "Bu resimde tehlike oluşturabilecek bir durum veya nesne var mı? Örneğin: ateş, duman, silah, yaralı insan, bıçak, makas gibi. Varsa kısaca açıkla, yoksa 'tehlike yok' yaz."

            try:
                response = client.generate(
                    model=model_name,
                    prompt=prompt_text,
                    images=[image_base64]
                )
                analysis_text_raw = response['response'].strip().lower()
                
                # 'tehlike yok' ifadesini dikkate alın
                if "tehlike yok" in analysis_text_raw:
                    new_status = "Pasif"
                else:
                    danger_keywords = ['bıçak', 'yangın', 'duman', 'silah', 'yaralı', 'kaza', 'makas']
                    is_dangerous = any(keyword in analysis_text_raw for keyword in danger_keywords)
                    if is_dangerous:
                        new_status = "Aktif"
                    else:
                        new_status = "Pasif"

                if new_status != last_alarm_status:
                    if new_status == "Aktif":
                        print("\n❗ TEHLİKE TESPİT EDİLDİ ❗")
                    else:
                        print("✅ Güvenli")
                
                last_alarm_status = new_status
            except Exception as e:
                print(f"Ollama'ya bağlanırken bir hata oluştu: {e}")
                last_alarm_status = "Hata"
        
        # Her 3 saniyede bir analiz yap
        time.sleep(10) 

# Flask API uç noktası
@app.get("/")
def read_root():
    return {"message": "Sekreter Bot API'si çalışıyor!"}

@app.post("/chat")
async def handle_chat(chat_history: ChatHistory):
    langgraph_messages = []
    for msg in chat_history.messages:
        if msg.type == 'user':
            langgraph_messages.append(HumanMessage(content=msg.content))
        elif msg.type == 'ai':
            langgraph_messages.append(AIMessage(content=msg.content))
    
    agent_state = {
        "messages": langgraph_messages,
        "kapı": chat_history.kapı,
        "alarm": chat_history.alarm # Sohbet yanıtına en son alarm durumunu ekle
    }

    final_message_content = ""
    updated_kapı_status = agent_state["kapı"]
    last_alarm_status = agent_state["alarm"]
    async for s in compiled_graph.astream(agent_state, stream_mode="values"):
        message = s["messages"][-1]
        
        if isinstance(message, AIMessage):
            if message.content:
                final_message_content = message.content
        elif isinstance(message, ToolMessage):
            if "kapı açılıyor" in message.content.lower():
                updated_kapı_status = "Açık"
            elif "kapı kapatılıyor" in message.content.lower():
                updated_kapı_status = "Kapalı"
        if "emergency" in message.content.lower():
            last_alarm_status = "Aktif"
        else:
            last_alarm_status = "Pasif"
    response_history = ChatHistory(
        messages=[Message(content=final_message_content, type="ai")],
        kapı=updated_kapı_status,
        alarm=last_alarm_status # Nihai alarm durumunu döndür
    )
    
    return response_history

# Kamera durumunu döndüren yeni API uç noktası
@app.get("/camera_status")
async def get_camera_status():
    """Ön uçtan gelen istek üzerine güncel kamera analiz sonucunu döndürür."""
    global last_alarm_status
    return {"status": last_alarm_status}

# Sunucu başlangıcında kamera analiz thread'ini başlat
@app.on_event("startup")
async def startup_event():
    # Kamera analizini arka planda ayrı bir thread'de başlat
    analysis_thread = threading.Thread(target=analyze_camera_in_background, daemon=True)
    analysis_thread.start()