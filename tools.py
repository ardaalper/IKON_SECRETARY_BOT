from langchain_core.tools import tool
import sqlite3
import os
DB_CONN=sqlite3.connect('./data/security_data.db')

# ---- Araçlar (Tools) ----

@tool
def guest(query: str) -> str:
    """Misafir Bilgisi Sorgulama Aracı
    Bu tool, veritabanındaki misafir kayıtlarını arar ve ilgili bilgileri döndürür. 
    Kullanıcı adı (misafir adı) üzerinden sorgulama yapılır. Tool, misafir verilerini hızlıca bulmak için tasarlanmıştır.

    Args:
        query (str): Sorgulanacak misafirin adı. Kısmi veya tam isim girilebilir. Büyük/küçük harf duyarlılığı yoktur.

    Returns:
        str: Eşleşen misafir kayıtlarının listesi. Her kayıt aşağıdaki bilgileri içerir:
            - Misafir adı
            - İlgili personel
            - Varış tarihi
            - Durum
            - Not
        Eğer eşleşme bulunamazsa, uygun bir uyarı mesajı döner.
    """

    cursor = sqlite3.connect('./data/security_data.db').cursor()
    cursor.execute("SELECT name, personnel_name, arrival_date, status, note FROM guests WHERE name LIKE ?", ('%'+query+'%',))
    matches = cursor.fetchall()
    
    if not matches:
        return "Misafir bilgisi bulunamadı."
    
    result = []
    for match in matches:
        result.append(f"Misafir: {match[0]}, İlgili Kişi: {match[1]}, Varış: {match[2]}, Durum: {match[3]}, Not: {match[4]}")
    
    return "\n".join(result)

@tool
def which_guest_of_staff(query: str, password: str = None) -> str:
    """Personelin Misafirleri Sorgulama Aracı
    Bu tool, belirli bir personelin hangi misafirleri olduğunu sorgular. 
    Güvenlik nedeniyle, sorgulama yapabilmek için şifre gereklidir. 
    Tool, yalnızca doğru şifre girildiğinde veritabanına erişir ve sonuç döndürür.

    Args:
        query (str): Personelin adı veya kısmi adı.
        password (str, optional): Sorgulama için gerekli şifre. 
                                Doğru şifre girilmezse bilgi verilemez.

    Returns:
        str: Personelin misafirleri hakkında bilgileri listeler. Her kayıt aşağıdaki bilgileri içerir:
            - Misafir adı
            - İlgili personel
            - Varış tarihi
            - Durum
            - Not
        Eğer eşleşme bulunamazsa veya şifre yanlışsa, açıklayıcı bir uyarı mesajı döner.
    """


    if password == "1234":  # Buraya istediğiniz şifreyi yazabilirsiniz
        cursor = sqlite3.connect('./data/security_data.db').cursor()
        cursor.execute("SELECT name, personnel_name, arrival_date, status, note FROM guests WHERE personnel_name LIKE ?", ('%'+query+'%',))
        matches = cursor.fetchall()
        
        if not matches:
            return "Misafir bilgisi bulunamadı."
        
        result = []
        for match in matches:
            result.append(f"Misafir: {match[0]}, İlgili Kişi: {match[1]}, Varış: {match[2]}, Durum: {match[3]}, Not: {match[4]}")
        
        return "\n".join(result)
    else:
        return "Bilgi almak için şifre gereklidir. Lütfen şifreyi giriniz."

@tool
def cargo(query: str) -> str:
    """Belirli bir veri kaynağından kargoyla ilgili bilgileri arar.
    Gönderiler, teslimatlar veya envanter hakkındaki soruları yanıtlamak için kullanışlıdır.
    Args:
        query (str): Aranacak belirli terim veya öğe.
    """
    cursor = sqlite3.connect('./data/security_data.db').cursor()
    cursor.execute("SELECT personnel_name, cargo_id, company, status FROM cargos WHERE personnel_name LIKE ? OR cargo_id LIKE ? OR company LIKE ? OR status LIKE ?", ('%'+query+'%', '%'+query+'%', '%'+query+'%', '%'+query+'%'))
    matches = cursor.fetchall()

    if not matches:
        return "Kargo bilgisi bulunamadı."
    
    result = []
    for match in matches:
        result.append(f"Personel: {match[0]}, Kargo ID: {match[1]}, Şirket: {match[2]}, Durum: {match[3]}")
    
    return "\n".join(result)



@tool
def security(query: str) -> str:
    """Kullanıcının güvenlik personelini haberdar etmesi için kullanılır. 
    Aynı zamanda tehlike arz eden durumları kontrol eder. Örneğin, yangın, hırsızlık, yaralanma 
    veya diğer acil durumlar."""
    cursor = sqlite3.connect('./data/security_data.db').cursor()


    #os.system("afplay ./data/DangerAlarm.mp3 &")
    #print("\n\nACIL DURUM!!!\n\n")
    # Tehlike yoksa personel bilgisi arayın
    cursor.execute("SELECT name, role FROM staff WHERE name LIKE ?", ('%'+query+'%',))
    staff_exists = cursor.fetchone()

    if staff_exists:
        return "emergency durum!!! Güvenlik birimi olay yerine çağrıldı. Lütfen sakin olun." + f"Şirket personeli {staff_exists[0]} ({staff_exists[1]}) bilgisi bulundu. Lütfen daha detaylı bilgi verin."
    else: 
        return "emergency durum!!! Güvenlik birimi olay yerine çağrıldı. Lütfen sakin olun." + "Güvenlik birimi veya personel bilgisi bulunamadı. Lütfen daha net bir sorgu girin."

@tool
def door_control(query: str, password: str = None) -> str:
    """Kapı açarken şifre yönetir ve şifre doğrulaması yapar.
    Bu araç, kullanıcının kapıyı açma veya kapama gibi işlemleri gerçekleştirmesine olanak tanır.
    Args:
        query (str): Kullanıcının sorgusu (örneğin "kapıyı aç").
        password (str): Kapı açma gibi hassas işlemler için kullanılan şifre.
    """
    
    # Kapı açma komutları
    open_keywords = ["kapıyı aç", "kapıyı açar mısın", "aç kapıyı", "kapıyı arala"]
    close_keywords = ["kapıyı kapat", "kapıyı kapatır mısın", "kapat kapıyı", "kapıyı kilitle"]

    query_lower = query.lower()
    
    # Şifre Kontrolü
    if any(phrase in query_lower for phrase in open_keywords):
        if password == "1234":  # Buraya istediğiniz şifreyi yazabilirsiniz

            return "Şifre doğru. Kapı açılıyor. Hoş geldiniz."
        else:
            return "Kapıyı açmak için şifre gereklidir. Lütfen şifreyi giriniz."
    
    elif any(phrase in query_lower for phrase in close_keywords):
        return "Kapı kapatılıyor. Güle güle."
    
    return "Kapı kontrolü ile ilgili bir komut algılanmadı."
