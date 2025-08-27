document.addEventListener('DOMContentLoaded', () => {
    // DOM elemanlarını seçme
    const chatBox   = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn   = document.getElementById('send-btn');
    const doorImage = document.getElementById('door-image');
    const alarmSound= document.getElementById('alarm-sound');
    const alarmImage= document.getElementById('alarm-image');
    const voiceBtn  = document.getElementById('voice-btn');

    // Sohbet geçmişi
    let chatHistory = {
        messages: [],
        kapı: "Kapalı",
        alarm: "Pasif"
    };

    // API URL'i
    const API_URL = 'http://127.0.0.1:8000/chat';

    // === TTS (Text-to-Speech) ===
    const speakText = (text) => {
        try {
            // Önce devam eden konuşmayı kes
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'tr-TR';
            window.speechSynthesis.speak(utterance);
        } catch (e) {
            console.warn('TTS oynatılamadı:', e);
        }
    };

    // Mesajı sohbet kutusuna ekleyen fonksiyon (AI için TTS entegre)
    const appendMessage = (content, type) => {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${type}-message`);
        messageDiv.textContent = content;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;

        if (type === 'ai') {
            speakText(content); // AI yanıtı seslendir
        }
    };

    // Kapı görselini güncelle
    const updateDoorImage = (status) => {
        if (status === "Açık") {
            doorImage.src = 'data/opened.png';
            doorImage.alt = 'Açık Kapı';
        } else {
            doorImage.src = 'data/closed.png';
            doorImage.alt = 'Kapalı Kapı';
        }
    };

    // Alarm sesini yönet
    const updateAlarm = (status) => {
        if (status === "Aktif") {
            alarmSound.play().catch((e) => {
                console.warn('Alarm sesi autoplay engeline takıldı veya hatayla durdu:', e);
            });
        } else {
            alarmSound.pause();
            alarmSound.currentTime = 0;
        }
    };

    // Alarm görselini güncelle
    const updateAlarmImage = (status) => {
        if (status === "Aktif") {
            alarmImage.src = 'data/alarm_on.png';
            alarmImage.alt = 'Aktif Alarm';
        } else {
            alarmImage.src = 'data/alarm_off.png';
            alarmImage.alt = 'Pasif Alarm';
        }
    };

    // API'ye mesaj gönder
    const sendMessage = async () => {
        const messageText = userInput.value.trim();
        if (messageText === "") return;

        // Kullanıcı mesajını işle
        chatHistory.messages.push({ content: messageText, type: 'user' });
        appendMessage(messageText, 'user');

        userInput.value = '';
        sendBtn.disabled = true;

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(chatHistory)
            });

            if (!response.ok) throw new Error('API yanıtı başarısız oldu.');

            const data = await response.json();

            // AI mesajını ekle
            const aiMessage = data.messages[0];
            chatHistory.messages.push(aiMessage);
            appendMessage(aiMessage.content, 'ai');

            // Kapı & alarm durumlarını güncelle
            chatHistory.kapı = data.kapı;
            updateDoorImage(chatHistory.kapı);

            chatHistory.alarm = data.alarm;
            updateAlarm(chatHistory.alarm);
            updateAlarmImage(chatHistory.alarm);

        } catch (error) {
            console.error('Hata:', error);
            appendMessage('Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.', 'ai');
        } finally {
            sendBtn.disabled = false;
        }

        console.log("Kapı durumu geldi:", chatHistory.kapı);
    };

    // === STT (Speech-to-Text) ===
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;
    let listening = false;

    if (SR) {
        recognition = new SR();
        recognition.lang = 'tr-TR';
        recognition.continuous = true;       // butonla durdurulana kadar dinlesin
        recognition.interimResults = false;  // sadece final sonuçlar gelsin

        recognition.onstart = () => {
            listening = true;
            if (voiceBtn) voiceBtn.textContent = '⏹ Durdur';
        };

        recognition.onend = () => {
            listening = false;
            if (voiceBtn) voiceBtn.textContent = '🎤 Konuş';
        };

        recognition.onerror = (event) => {
            console.error('STT Hatası:', event.error);
            // Hata olursa dinlemeyi kapat
            listening = false;
            if (voiceBtn) voiceBtn.textContent = '🎤 Konuş';
        };

        recognition.onresult = (event) => {
            const idx = event.resultIndex;
            const result = event.results[idx];
            if (result.isFinal) {
                const transcript = result[0].transcript.trim();
                if (transcript) {
                    userInput.value = transcript;
                    sendMessage();
                }
            }
        };
    } else {
        console.warn('Bu tarayıcı Web Speech API (STT) desteklemiyor.');
    }

    // Olay dinleyicileri
    if (sendBtn) {
        sendBtn.addEventListener('click', sendMessage);
    }

    if (userInput) {
        userInput.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') sendMessage();
        });
    }

    if (voiceBtn) {
        voiceBtn.addEventListener('click', () => {
            if (!recognition) {
                alert("Tarayıcınız konuşma tanımayı (STT) desteklemiyor.");
                return;
            }
            if (!listening) {
                recognition.start();   // başlat
            } else {
                recognition.stop();    // durdur
            }
        });
    }

    // Başlangıç mesajı
    appendMessage('Merhaba! Ben sekreter bot. Size nasıl yardımcı olabilirim?', 'ai');
});
