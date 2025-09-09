from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from graph import get_graph
from ultralytics import YOLO
import cv2
import time
import threading
from database import get_all_records

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
    password_attempts: int = 0

# LangGraph uygulamasını bir kez derle
compiled_graph = get_graph()

# === KAMERA ANALİZİ İÇİN YENİ BÖLÜM ===
# Son analiz sonucunu tutacak global değişken
last_alarm_status = "Pasif"


# Kilitleme mekanizması (thread güvenliği için)
analysis_lock = threading.Lock()



# Yolo modeli yükle
yolo_model_path = "best_harmfulobjects.pt"  # senin eğittiğin model
model_classes =  ['Axe', 'Chainsaw', 'Chisel', 'Coin', 'Drink', 'Dumbbell', 'Fork', 'Hammer', 'Knife', 'Scissors', 'Screwdriver', 'Stapler']
yolo_model = YOLO(yolo_model_path)

def analyze_camera_in_background():
    """Arka planda sürekli olarak kamera görüntüsünü analiz eden fonksiyon (YOLO tabanlı)."""
    global last_alarm_status
    # print("Kamera analiz thread'i başlatılıyor...") 
    
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

            # YOLO tespiti
            results = yolo_model.predict(source=frame, conf=0.8, verbose=False)  # conf eşik değeri
            detected_objects = []
            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    # Senin dataset'inde 0,1,2 vs sınıf idleri var
                    # Eğer sınıf tehlike içeriyorsa alarm aktif
                    detected_objects.append(yolo_model.names[cls_id].lower())

            # Tehlike kontrolü
            danger_keywords = ['axe', 'chainsaw', 'chisel', 'fork', 'hammer', 'knife', 'scissors', 'screwdriver']  # senin tehlike listene göre
            is_dangerous = any(obj in danger_keywords for obj in detected_objects)
            #print(f"Tespit Edilen Nesneler: {detected_objects} | Tehlike: {is_dangerous}")
            new_status = "Aktif" if is_dangerous else "Pasif"

            if new_status != last_alarm_status:
                if new_status == "Aktif":
                    print("\n❗ TEHLİKE TESPİT EDİLDİ ❗", detected_objects)
                else:
                    print("✅ Güvenli")

            last_alarm_status = new_status
        
        time.sleep(1)
        #print("Kamera analiz thread'i çalışıyor...")


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
        "alarm": chat_history.alarm, # Sohbet yanıtına en son alarm durumunu ekle
        "password_attempts": chat_history.password_attempts
    }

    final_message_content = ""
    updated_kapı_status = agent_state["kapı"]
    last_alarm_status = "Pasif"
    last_password_attempts = agent_state["password_attempts"]
    
    async for s in compiled_graph.astream(agent_state, stream_mode="values"):
        message = s["messages"][-1]
        
        if isinstance(message, AIMessage):
            if message.content:
                final_message_content = message.content
        elif isinstance(message, ToolMessage):
            if "kapı açılıyor" in message.content.lower():
                updated_kapı_status = "Açık"
                last_password_attempts = 0
                last_alarm_status = "Pasif"
            if "kapı kapatılıyor" in message.content.lower():
                updated_kapı_status = "Kapalı"
            if "emergency" in message.content.lower():
                last_alarm_status = "Aktif"
            if "sifre dogru" in message.content.lower():
                last_password_attempts = 0
                last_alarm_status = "Pasif"
            if "hatalı sifre." in message.content.lower():
                last_password_attempts += 1
            if last_password_attempts >= 3:
                last_alarm_status = "Aktif"
                print("❗ 3 HATALI ŞİFRE GİRİLDİ, ALARM AKTİF ❗")
                last_password_attempts = 0  # Reset attempts after alarm
        print(":::" + str(last_password_attempts))
            
    response_history = ChatHistory(
        messages=[Message(content=final_message_content, type="ai")],
        kapı=updated_kapı_status,
        alarm=last_alarm_status, # Nihai alarm durumunu döndür
        password_attempts=last_password_attempts
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

# --- ADMIN PANELİ İÇİN YENİ UÇ NOKTA: VERİLERİ GÖRÜNTÜLEME ---


@app.get("/admin/records")
async def get_all_security_records():
    """
    Veritabanındaki tüm güvenlik kayıtlarını döndürür.
    Bu endpoint, database.py dosyasındaki get_all_records fonksiyonunu kullanır.
    """
    try:
        records = get_all_records()
        return {"records": records}
    except Exception as e:
        # Hata durumunda, istemciye 500 Internal Server Error döndürür
        raise HTTPException(status_code=500, detail=f"Veritabanı okunurken bir hata oluştu: {str(e)}")
    
# --- ADMIN PANELİ GİRİŞİ İÇİN ŞİFRE KONTROL ENDPOINT'İ ---

# Basit bir admin şifresi
ADMIN_PASSWORD = "admin123"

# Şifre kontrolü için Pydantic modeli
class AdminData(BaseModel):
    password: str

@app.post("/admin/login")
async def admin_login(admin_data: AdminData):
    """
    Admin paneli için şifre kontrolü yapar.
    """
    if admin_data.password == ADMIN_PASSWORD:
        return {"message": "Giriş başarılı."}
    else:
        # Şifre yanlışsa 401 Unauthorized hatası döndürür
        raise HTTPException(status_code=401, detail="Hatalı şifre.")