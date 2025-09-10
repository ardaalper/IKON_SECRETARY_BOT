Projenin amacı, bir ofiste kapıcı/sekreter işlevi görecek yapay zeka entegrasyonu yapmak.

Projede kullandığım llm modeli: GPT-OSS:20b OLLAMA

Projede kullandığım görüntü algılama modeli: YOLO v11

Projede kullandığım görüntü algılama veri seti: https://universe.roboflow.com/harmfull-objects/harmful-objects-wmmdi

# GİRİŞ:

### GRAPH.PY

Langgraph kütüphanesini ve teercih edilen llm'i bir araya getiren dosyadır. Graph, kendi içerisinde iki düğüm barındırır. Bunlar call_model ve 
tool_node düğümleridir. Tool_node düğümü llm'in gerekli gördüğü durumlar karşısında çağırması gereken tool ları barındırır. Bu toollar kendi 
içlerinde tanımlarını ve örnek çalışma durumlarını barındırır. Bu sayede llm hangi tool'u çağırması gerektiğini anlar.

AgentState dediğimiz yapı ise TypedDict inherited bir yapıdır ve chatin mesajlaşma trafiğini takip edebilmesi için bir mesaj arrayi barındırır.
Bunun yanı sıra kapı,alarm,şifre deneme statelerini de barındırır ama llm'in bunlara erişimi yoktur. Onun yerine llm'e her mesaj yolladığımızda
bu stateleri mesajın içine gömeriz.

call_model, response üretmek istediği zaman bu konuşma geçmişini paket haline getirip modele yollar ve cevap bekler. mdeol ssh ile bağlanılan 
şirket bilgisaayarındadır ve offlinedır. modele istek atılmadan önce toollara erişim verilir, bu sayede onları kullanabilir.

### TOOLS.PY

Modelimizin düzgün biçimde çalışabilmesi için gerekli kilit yapı. İçerisinde çeşitli tool'ları barındırır.

- **guest(query: str)**
  Bu araç, misafir bilgilerini sorgulamak için kullanılır. Veritabanındaki guests tablosunda misafir adını (kısmi veya tam) arar ve eşleşen 
  kayıtları döndürür. Her kayıt misafirin adı, ilgili personel, varış tarihi, durumu ve varsa not bilgilerini içerir. Eğer eşleşme bulunamazsa 
  "Misafir bilgisi bulunamadı." mesajı verir.

- **which_guest_of_staff(query: str, password: str = None)**
  Bu araç, belirli bir personelin misafirlerini sorgulamak için kullanılır. Güvenlik amacıyla şifre kontrolü içerir. İlk olarak personelin
  varlığını kontrol eder, ardından şifre doğru ise personelin misafir listesini getirir. Yanlış veya eksik şifre girilirse bilgi verilmez ve
  "hatalı şifre" uyarısı döner.

- **cargo(query: str)**
  Bu araç, şirkete gelen veya gönderilen kargoları sorgulamak için tasarlanmıştır. Veritabanındaki cargos tablosunda personel adı, kargo ID’si,
  kargo firması veya kargo durumu üzerinden arama yapabilir. Eşleşen kayıtlar personel adı, kargo ID, firma ve mevcut durum bilgilerini
  listeler. Kayıt yoksa "Kargo bilgisi bulunamadı." mesajı verir.

- **security(query: str)**
  Bu araç, acil durumlarda güvenlik çağırmak için kullanılır. Kullanıcı bir tehlike (yangın, hırsızlık, kavga, yaralanma vb.) bildirdiğinde
  güvenlik birimini olay yerine yönlendirir. Eğer sorgu belirli bir personele dair güvenlik bağlantısı içeriyorsa, ilgili personelin bilgilerini
  de döndürür. Her durumda güvenliği çağırdığına dair net bir acil durum mesajı verir.

- **door_control(query: str, password: str = None)**
  Bu araç, kapı kontrolünü yönetir. Kullanıcının kapıyı açma veya kapatma talimatlarına göre hareket eder. Kapı açma işlemleri güvenlik amacıyla
  şifre ister; doğru şifre girildiğinde "Kapı açılıyor" mesajı döner, yanlışsa "hatalı şifre" uyarısı verir. Kapıyı kapatma veya kilitleme
  işlemleri için şifre gerekmez. Geçersiz komutlarda kullanıcıyı bilgilendirir.

- **staff_info(query: str)**
  Bu araç, veritabanındaki personel bilgilerini sorgulamak için kullanılır. Aranan personelin adı üzerinden kayıt arar ve eşleşen kayıtları
  personel adı, görev/rol ve konum bilgisiyle birlikte döndürür. Eğer personel bulunamazsa "Personel bilgisi bulunamadı." mesajı verir.

- **send_guest_email(staff_name: str, guest_name: str = "", content_text: str = "")**
  Bu araç, misafir geldiğinde ilgili personele otomatik e-posta göndermek için kullanılır. İlk olarak personelin veritabanında kayıtlı olup
  olmadığını ve e-posta adresini kontrol eder. Eğer adres bulunursa, .env dosyasındaki e-posta kimlik bilgileriyle SMTP üzerinden mail
  gönderilir. Konu satırında misafir bilgisi, içerikte ise content_text yer alır.

# KODU NASIL ÇALIŞTIRMALIYIM?

  1) Şirket sunucusuna bağlı bir bilgisayarda yeni bir terminal açıp **ssh alper@192.168.0.94** komutu girilmeli.

  2) Bağlandıktan sonra açılan terminalde **export OLLAMA_HOST=0.0.0.0:11434** kodu ile sunucu yayınlanmalı.

  3) **ollama serve** komutu ile ollama sunucusu ayağa kaldırılır.

  4) Proje klasöründe backend dizinine gelip yeni terminal açılmalı ve **source venv/bin/acvtivate** komutu ile ortam etkinleştirilir.

  5) Yine aynı terminalde **uvicorn main:app --reload** komutu ile backend ayağa kaldırılır.

  6) Son olarak frontend klasöründe yer alan index.html ile arayüze giriş yapılır. 
 
NOT: mailsender aracı kişisel mail hesabım üzerinden çalıştığı için test aşamasında kendi mailinizi ve email pass inizi girmeniz gerekir. 
