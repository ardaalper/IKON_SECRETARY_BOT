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
    """
    Kargolarla ilgili bilgileri aramak ve listelemek için kullanılır. 
    Bu araç, şirkete gelen veya gönderilen kargoların durumunu sorgulamak için uygundur. 
    Sadece kargo ile ilgili sorular için kullanılmalıdır. Diğer konular için kullanılmamalıdır.

    Sağlayabileceği bilgiler:
    - Kargonun teslim edilip edilmediği veya mevcut durumu
    - Kargo ID'si üzerinden takip
    - Belirli bir personel adına gelen kargolar
    - Hangi şirketten (kargo firması) geldiği bilgisi

    Args:
        query (str): Kargo hakkında aranacak anahtar kelime veya bilgi 
                     (örneğin personel adı, kargo ID'si, şirket adı veya kargo durumu).
    
    Returns:
        str: Eşleşen kayıtların listesi. Her satırda şu bilgiler bulunur:
             Personel adı, Kargo ID, Kargo firması, Kargonun durumu.
             Eğer kayıt bulunmazsa "Kargo bilgisi bulunamadı." döner.
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
    """Acil durumlar ve güvenlik konularıyla ilgilenen bir araç. Bu aracı, yalnızca bir tehlike veya acil durum tespiti yaptığında ya da bir kullanıcının acil yardım talebi olduğunda kullan.

    İşlev: Güvenlik görevlilerini olay yerine yönlendirir ve durumun ciddiyetini değerlendirir.
    Kullanım Koşulları:
    - Kullanıcı bir tehlike (örneğin: "yangın", "hırsızlık", "bomba", "kavga", "yaralanma") bildirdiğinde.
    - Kullanıcı doğrudan "güvenlik" veya "acil durum" gibi anahtar kelimelerle yardım istediğinde.
    - Kullanıcının davranışları veya sorguları endişe verici veya şüpheli olduğunda.

    Örnekler: "Acil yardım lazım, birisi bayıldı.", "Burası yanıyor, itfaiye gerekli!", "Güvenlik çağırın!", "Şu an odamda bir hırsız var."
    
    Bu araç bir tehdit algıladığında, hızla yanıt vererek durumu ciddiye almalı ve gerekli aksiyonları almalıdır.
    """
    cursor = sqlite3.connect('./data/security_data.db').cursor()


    cursor.execute("SELECT name, role FROM staff WHERE name LIKE ?", ('%'+query+'%',))
    staff_exists = cursor.fetchone()

    if staff_exists:
        return "emergency !!! Güvenlik birimi olay yerine çağrıldı. Lütfen sakin olun." + f"Şirket personeli {staff_exists[0]} ({staff_exists[1]}) bilgisi bulundu. Lütfen daha detaylı bilgi verin."
    else: 
        return "emergency !!! Güvenlik birimi olay yerine çağrıldı. Lütfen sakin olun." + "Güvenlik birimi veya personel bilgisi bulunamadı. Lütfen daha net bir sorgu girin."

@tool
def door_control(query: str, password: str = None) -> str:
    """
    Kapı kontrol işlemleri için kullanılır. 
    Kullanıcıdan gelen talimatlara göre kapıyı açma veya kapatma işlevini gerçekleştirir. 
    Kapı açma işlemleri güvenlik nedeniyle şifre doğrulaması gerektirir. 
    Kapı kapatma işlemleri için şifre gerekmez.

    Kullanım Alanları:
    - Kapıyı açma (şifre doğrulaması ile)
    - Kapıyı kapatma veya kilitleme (şifresiz)
    
    Args:
        query (str): Kullanıcının kapı ile ilgili talimatı. 
                     Örnekler: "kapıyı aç", "kapıyı kapat", "kapıyı kilitle".
        password (str, optional): Kapıyı açmak için gerekli şifre. 
                                  Eğer yanlış veya boş girilirse kapı açılmaz.
    
    Returns:
        str: İşlemin sonucu. 
             - Doğru şifre girilirse: "Şifre doğru. Kapı açılıyor. Hoş geldiniz."
             - Yanlış/boş şifre girilirse: "Kapıyı açmak için şifre gereklidir. Lütfen şifreyi giriniz."
             - Kapı kapatma talimatında: "Kapı kapatılıyor. Güle güle."
             - Geçersiz komut girilirse: "Kapı kontrolü ile ilgili bir komut algılanmadı."
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

@tool
def staff_info(query: str) -> str:
    """Personel Bilgisi Sorgulama Aracı
    Bu tool, veritabanındaki personel kayıtlarını arar ve ilgili bilgileri döndürür. 
    Kullanıcı adı (personel adı) üzerinden sorgulama yapılır. Tool, personel verilerini hızlıca bulmak için tasarlanmıştır.

    Args:
        query (str): Sorgulanacak personelin adı. Kısmi veya tam isim girilebilir. Büyük/küçük harf duyarlılığı yoktur.

    Returns:
        str: Eşleşen personel kayıtlarının listesi. Her kayıt aşağıdaki bilgileri içerir:
            - Personel adı
            - Görev/rol
        Eğer eşleşme bulunamazsa, uygun bir uyarı mesajı döner.
    """

    cursor = sqlite3.connect('./data/security_data.db').cursor()
    cursor.execute("SELECT name, role, konum FROM staff WHERE name LIKE ?", ('%'+query+'%',))
    matches = cursor.fetchall()
    
    if not matches:
        return "Personel bilgisi bulunamadı."
    
    result = []
    for match in matches:
        result.append(f"Personel: {match[0]}, Rol: {match[1]}, Konum: {match[2]}")
    
    return "\n".join(result)