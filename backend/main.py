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

# Ollama sunucusunun adresi ve modeli
ollama_host = 'http://192.168.0.94:11434'
model_name = 'qwen2.5vl:3b'
client = ollama.Client(host=ollama_host)

def analyze_camera():
    """Kamera görüntüsünü analiz eden ve alarm durumunu döndüren fonksiyon."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Hata: Kamera açılamadı.")
        return "Pasif"

    ret, frame = cap.read()
    cap.release()
    if not ret:
        print("Hata: Kare yakalanamadı.")
        return "Pasif"

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
        
        # Tehlike tespiti için anahtar kelimeler
        danger_keywords = ['bıçak', 'yangın', 'duman', 'silah', 'yaralı', 'kaza', 'makas']
        is_dangerous = any(keyword in analysis_text_raw for keyword in danger_keywords)
        
        if is_dangerous:
            return "Aktif"
        else:
            return "Pasif"
    except Exception as e:
        print(f"Ollama'ya bağlanırken bir hata oluştu: {e}")
        return "Pasif"


@app.get("/")
def read_root():
    return {"message": "Sekreter Bot API'si çalışıyor!"}

@app.post("/chat")
async def handle_chat(chat_history: ChatHistory):
    # Kullanıcı mesajı geldiğinde kamera durumunu kontrol et
    updated_alarm_status = analyze_camera()

    langgraph_messages = []
    for msg in chat_history.messages:
        if msg.type == 'user':
            langgraph_messages.append(HumanMessage(content=msg.content))
        elif msg.type == 'ai':
            langgraph_messages.append(AIMessage(content=msg.content))
    
    agent_state = {
        "messages": langgraph_messages,
        "kapı": chat_history.kapı,
        "alarm": updated_alarm_status # Yeni alarm durumuyla güncellendi
    }

    final_message_content = ""
    updated_kapı_status = agent_state["kapı"]
    
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

    response_history = ChatHistory(
        messages=[Message(content=final_message_content, type="ai")],
        kapı=updated_kapı_status,
        alarm=updated_alarm_status # Nihai alarm durumunu döndür
    )
    
    return response_history