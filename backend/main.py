from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from graph import get_graph # Güncellediğimiz graph.py dosyasını içe aktarıyoruz

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
        "alarm": chat_history.alarm
    }

    final_message_content = ""
    updated_kapı_status = agent_state["kapı"]
    updated_alarm_status = agent_state["alarm"]
    updated_alarm_status = "Pasif"
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
                updated_alarm_status = "Aktif"
            else:
                updated_alarm_status = "Pasif"

    response_history = ChatHistory(
        messages=[Message(content=final_message_content, type="ai")],
        kapı=updated_kapı_status,
        alarm=updated_alarm_status
    )
    
    return response_history
