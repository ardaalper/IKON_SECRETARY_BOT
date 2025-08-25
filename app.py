import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from graph import app
from streamlit_mic_recorder import mic_recorder, speech_to_text
import pyttsx3

# Başlık
st.set_page_config(page_title="Sekreter Bot", page_icon="🤖", layout="wide")
st.title("IKON BOT 🤖")

# Session State -> konuşmayı hatırlaması için
if "state" not in st.session_state:
    st.session_state.state = {"messages": [], "kapı": "Kapalı"}
    st.session_state.ai_speech = "" # Yeni: Ses için değişken




def speak_text(text):

    engine = pyttsx3.init()
    engine.setProperty('rate', 200)
    engine.setProperty('volume', 1.0)
    engine.setProperty('voice', 'tr')  # Türkçe sesi kullanmak için
    engine.say(text)
    engine.runAndWait()


# Layout: Sol taraf chat, sağ üstte kapı görseli
col1, col2 = st.columns([3, 1])  # genişlik oranı

with col2:
    st.subheader("🚪 Kapı Durumu")
    if st.session_state.state["kapı"] == "Açık":
        st.image("./images/opened.png", width=150)
    else:
        st.image("./images/closed.png", width=150)

with col1:
    # Chat arayüzü
    for msg in st.session_state.state["messages"]:
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.write(msg.content)
        elif isinstance(msg, AIMessage):
            with st.chat_message("assistant"):
                st.write(msg.content)

    # Kullanıcıdan input al
    text_from_speech = speech_to_text(language='tr', start_prompt="🎙️ Konuşmaya Başla", stop_prompt="⏹️ Kaydı Durdur", just_once=True, use_container_width=True)
    prompt = st.chat_input("Mesajınızı yazın...")
    
    # Eğer konuşmadan bir metin alınmışsa onu kullan
    if text_from_speech:
        prompt = text_from_speech

    # Sesli okumayı tetikle
    if st.session_state.ai_speech:
        speak_text(st.session_state.ai_speech)
        st.session_state.ai_speech = ""  # Sesi oynattıktan sonra sıfırla

    # Eğer kullanıcı bir prompt girmişse sohbeti başlat
    if prompt:
        # Kullanıcı mesajını göster
        st.session_state.state["messages"].append(HumanMessage(content=prompt))
        with st.chat_message("user"):
            st.write(prompt)

        # AI'dan cevap al
        final_message_content = ""
        for s in app.stream(st.session_state.state, stream_mode="values"):
            message = s["messages"][-1]
            if isinstance(message, AIMessage):
                if message.content:
                    st.session_state.state["messages"].append(message)
                    with st.chat_message("assistant"):
                        st.write(message.content)
                    final_message_content = message.content
            elif isinstance(message, ToolMessage):
                if "kapı açılıyor" in message.content.lower():
                    st.session_state.state["kapı"] = "Açık"
                elif "şifre gerekli" in message.content.lower():
                    st.session_state.state["kapı"] = "Kapalı"
                elif "kapı kapatılıyor" in message.content.lower():
                    st.session_state.state["kapı"] = "Kapalı"

        # Döngü bittikten sonra botun son cevabını ses değişkenine kaydet
        st.session_state.ai_speech = final_message_content

        # 🔄 input sonrası kapı görselini güncellemek için rerun
        st.rerun()