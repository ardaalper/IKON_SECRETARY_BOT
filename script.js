document.addEventListener('DOMContentLoaded', () => {
    // DOM elemanlarını seçme
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const doorImage = document.getElementById('door-image');

    // Sohbet geçmişini saklamak için bir değişken
    let chatHistory = {
        messages: [],
        kapı: "Kapalı"
    };

    // API URL'i
    const API_URL = 'http://127.0.0.1:8000/chat';

    // Mesajı sohbet kutusuna ekleyen fonksiyon
    const appendMessage = (content, type) => {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${type}-message`);
        messageDiv.textContent = content;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight; // En aşağı kaydır
    };
    // Kapı görselini güncelleyen fonksiyon
    const updateDoorImage = (status) => {
        if (status === "Açık") {
            doorImage.src = 'images/opened.png';
            doorImage.alt = 'Açık Kapı';
        } 
        else if (status === "Kapalı") {
            doorImage.src = 'images/closed.png';
            doorImage.alt = 'Kapalı Kapı';
        }
    };
    // API'ye mesaj gönderen fonksiyon
    const sendMessage = async () => {
        const messageText = userInput.value.trim();
        if (messageText === "") return;

        // Kullanıcı mesajını geçmişe ekle ve ekranda göster
        chatHistory.messages.push({ content: messageText, type: 'user' });
        appendMessage(messageText, 'user');

        userInput.value = ''; // Input kutusunu temizle
        sendBtn.disabled = true; // Gönder butonunu devre dışı bırak

        try {
            // API'ye POST isteği gönder
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(chatHistory)
            });

            if (!response.ok) {
                throw new Error('API yanıtı başarısız oldu.');
            }

            const data = await response.json();

            // API'den gelen AI mesajını geçmişe ekle ve ekranda göster
            const aiMessage = data.messages[0];
            chatHistory.messages.push(aiMessage);
            appendMessage(aiMessage.content, 'ai');

            // Kapı durumunu güncelle
            chatHistory.kapı = data.kapı;
            updateDoorImage(chatHistory.kapı);

        } catch (error) {
            console.error('Hata:', error);
            appendMessage('Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.', 'ai');
        } finally {
            sendBtn.disabled = false; // İşlem bitince butonu tekrar etkinleştir
        }
        console.log("Kapı durumu geldi:", chatHistory.kapı);

    };

    

    // Olay dinleyicileri
    sendBtn.addEventListener('click', sendMessage);

    userInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    // Başlangıç mesajı
    appendMessage('Merhaba! Ben sekreter bot. Size nasıl yardımcı olabilirim?', 'ai');
});