document.addEventListener('DOMContentLoaded', () => {
    // DOM elemanlarını seçme
    const chatBox   = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn   = document.getElementById('send-btn');
    const doorImage = document.getElementById('door-image');
    const alarmSound= document.getElementById('alarm-sound');
    const alarmImage= document.getElementById('alarm-image');
    const voiceBtn  = document.getElementById('voice-btn');
    const liveCamera = document.getElementById('live-camera');
    const passwordAttemptsDisplay = document.getElementById('password-attempts-display'); // Bu satırı ekleyin
    
    // Yeni DOM elemanlarını seçme
    const adminPanelBtn     = document.getElementById('admin-panel-btn');
    const passwordModal     = document.getElementById('password-modal');
    const closeBtn          = document.querySelector('.close-btn');
    const passwordInput     = document.getElementById('password-input');
    const passwordSubmitBtn = document.getElementById('password-submit-btn');
    const passwordErrorMsg  = document.getElementById('password-error-msg');

    // Sohbet geçmişi
    let chatHistory = {
        messages: [],
        kapı: "Kapalı",
        alarm: "Pasif",
        password_attempts: 0
    };

    // API URL'leri
    const CHAT_API_URL = 'http://127.0.0.1:8000/chat';
    const CAMERA_API_URL = 'http://127.0.0.1:8000/camera_status';

    const startCamera = async () => {
        try {
            // Kamera ve mikrofon erişimi için izin iste
            const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
            liveCamera.srcObject = stream;
        } catch (error) {
            console.error('Kamera erişiminde hata oluştu:', error);
            // Kullanıcıya bir hata mesajı gösterebilirsiniz
            alert('Kamera açılamadı. Lütfen kamera erişimine izin verdiğinizden emin olun.');
        }
    };

    // Sayfa yüklendiğinde kamerayı başlat
    startCamera();
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

    // Şifre deneme sayacını güncelle
    const updatePasswordAttempts = (attempts) => {
        if (passwordAttemptsDisplay) {
            passwordAttemptsDisplay.textContent = `Şifre Deneme: ${attempts}`;
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
            const response = await fetch(CHAT_API_URL, {
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

            // Chat API'sinden gelen alarm durumunu doğrudan kullan
            chatHistory.alarm = data.alarm;
            updateAlarm(chatHistory.alarm);
            updateAlarmImage(chatHistory.alarm);

            chatHistory.password_attempts = data.password_attempts;
            updatePasswordAttempts(chatHistory.password_attempts);
        } catch (error) {
            console.error('Hata:', error);
            appendMessage('Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.', 'ai');
        } finally {
            sendBtn.disabled = false;
        }

        console.log("Kapı durumu geldi:", chatHistory.kapı);
    };

    // === Kamera Analiz Durumunu Güncelleme ===
    const updateCameraStatus = async () => {
        try {
            const response = await fetch(CAMERA_API_URL);
            if (!response.ok) throw new Error('Kamera API yanıtı başarısız oldu.');
            const data = await response.json();
            
            const cameraStatus = data.status;

            // Eğer tehlike varsa alarmı aktif et
            if (cameraStatus === "Aktif") {
                // Sadece durum değiştiyse mesaj ekle
                if (chatHistory.alarm !== "Aktif") {
                    appendMessage("⚠️ Güvenlik sistemi bir tehlike tespit etti! Alarm aktif edildi.", 'ai');
                    chatHistory.alarm = "Aktif";
                    updateAlarm(chatHistory.alarm);
                    updateAlarmImage(chatHistory.alarm);
                }
            } /*else if (cameraStatus === "Pasif") {
                // Tehlike yoksa alarmı pasif yap
                if (chatHistory.alarm === "Aktif") {
                    appendMessage("✅ Tehlike durumu ortadan kalktı. Alarm pasif hale getirildi.", 'ai');
                    chatHistory.alarm = "Pasif";
                    updateAlarm(chatHistory.alarm);
                    updateAlarmImage(chatHistory.alarm);
                }
            }*/
        } catch (error) {
            console.error('Kamera analiz hatası:', error);
            // Hata durumunda da alarmı pasif yapabiliriz
            if (chatHistory.alarm === "Aktif") {
                chatHistory.alarm = "Pasif";
                updateAlarm(chatHistory.alarm);
                updateAlarmImage(chatHistory.alarm);
            }
        }
    };

    // Her 3 saniyede bir kamera durumunu kontrol et
    setInterval(updateCameraStatus, 1000); // 3000 ms = 3 saniye

    // === STT (Speech-to-Text) ===
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;
    let listening = false;

    if (SR) {
        recognition = new SR();
        recognition.lang = 'tr-TR';
        recognition.continuous = true;
        recognition.interimResults = false;

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
                recognition.start();
            } else {
                recognition.stop();
            }
        });
    }

    // Admin paneli ile ilgili kodlar.  /////////////////////////////////////////////
    if (adminPanelBtn) {
        adminPanelBtn.addEventListener('click', () => {
            passwordModal.style.display = 'flex'; // Pop-up'ı göster
            passwordInput.value = ''; // Giriş alanını temizle
            passwordErrorMsg.textContent = ''; // Hata mesajını temizle
        });
    }

    // Kapatma butonuna tıklama olayı
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            passwordModal.style.display = 'none'; // Pop-up'ı gizle
        });
    }

    // Modala tıklandığında kapanmasını sağla (dışarıya tıklanırsa)
    window.addEventListener('click', (event) => {
        if (event.target === passwordModal) {
            passwordModal.style.display = 'none';
        }
    });

    // Şifre gönderme butonu olayı
    if (passwordSubmitBtn) {
        passwordSubmitBtn.addEventListener('click', async () => {
            const enteredPassword = passwordInput.value;
            const ADMIN_API_URL = 'http://127.0.0.1:8000/admin/login'; // Yeni login endpoint'i

            try {
                const response = await fetch(ADMIN_API_URL, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ password: enteredPassword })
                });

                if (response.ok) {
                    // Şifre doğruysa, admin sayfasına yönlendir
                    passwordErrorMsg.textContent = '';
                    passwordModal.style.display = 'none';
                    window.location.href = 'admin.html';
                } else {
                    // Hata durumunda (yanlış şifre), hata mesajını göster
                    const errorData = await response.json();
                    passwordErrorMsg.textContent = errorData.detail || 'Hatalı şifre. Lütfen tekrar deneyin.';
                }
            } catch (error) {
                console.error('API Hatası:', error);
                passwordErrorMsg.textContent = 'Bir hata oluştu. Lütfen tekrar deneyin.';
            }
        });
    }
    // Başlangıç mesajı
    appendMessage('Merhaba! Ben sekreter bot. Size nasıl yardımcı olabilirim?', 'ai');
    // Sayfa yüklendiğinde şifre deneme sayacını ayarla
    updatePasswordAttempts(chatHistory.password_attempts); // Bu satırı ekleyin
});