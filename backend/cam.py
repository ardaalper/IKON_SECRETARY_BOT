from flask import Flask, jsonify, request
from flask_cors import CORS
import cv2
import base64
import ollama
import time
import threading

app = Flask(__name__)
CORS(app)  # CORS'u etkinleştirin

# Ollama sunucusunun adresi ve modeli
ollama_host = 'http://192.168.0.94:11434'
model_name = 'qwen2.5vl'
client = ollama.Client(host=ollama_host)

# Kamera nesnesi
cap = cv2.VideoCapture(0)

# Son analiz sonucunu tutacak global değişken
last_analysis_result = "Güvenli"
# Kilitleme mekanizması (birden fazla isteğin çakışmasını engellemek için)
analysis_lock = threading.Lock()

def analyze_frame():
    """Arka planda sürekli olarak kamera görüntüsünü analiz eden fonksiyon."""
    global last_analysis_result
    while True:
        with analysis_lock:
            ret, frame = cap.read()
            if not ret:
                print("Kare yakalanamadı.")
                continue

            _, buffer = cv2.imencode('.jpg', frame)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            prompt_text = "Bu resimde tehlike oluşturabilecek bir durum veya nesne var mı? Örneğin: ateş, duman, silah, yaralı insan, bıçak, makas gibi. Varsa kısaca açıkla, yoksa 'tehlike yok' yaz."

            try:
                response = client.generate(
                    model=model_name,
                    prompt=prompt_text,
                    images=[image_base64]
                )
                analysis_text_raw = response['response'].strip()
                danger_keywords = ['bıçak', 'yangın', 'duman', 'silah', 'yaralı', 'kaza', 'makas']
                is_dangerous = any(keyword in analysis_text_raw.lower() for keyword in danger_keywords)
                
                if is_dangerous:
                    last_analysis_result = "TEHLIKE"
                else:
                    last_analysis_result = "Güvenli"
                print(f"Analiz sonucu: {last_analysis_result}")
            except Exception as e:
                print(f"Ollama'ya bağlanırken bir hata oluştu: {e}")
                last_analysis_result = "Hata"
        
        # Her 3 saniyede bir analiz yap
        time.sleep(3) 

# Flask API uç noktası
@app.route('/analyze_camera', methods=['GET'])
def get_camera_status():
    """Ön uçtan gelen istek üzerine kamera analiz sonucunu döndürür."""
    global last_analysis_result
    # Sadece son analiz sonucunu döndür
    return jsonify({"status": last_analysis_result})

# Sunucu başlangıcı
if __name__ == '__main__':
    # Kamera analizini arka planda ayrı bir thread'de başlat
    analysis_thread = threading.Thread(target=analyze_frame, daemon=True)
    analysis_thread.start()
    
    # Flask sunucusunu başlat
    app.run(host='0.0.0.0', port=5000, debug=False)