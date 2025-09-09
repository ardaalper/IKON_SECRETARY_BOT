Projenin amacı, bir ofiste kapıcı/sekreter işlevi görecek yapay zeka entegrasyonu yapmak.

Projede kullandığım llm modeli: GPT-OSS:20b OLLAMA

Projede kullandığım görüntü algılama modeli: YOLO v11

Projede kullandığım görüntü algılama veri seti: https://universe.roboflow.com/harmfull-objects/harmful-objects-wmmdi

BAŞLICA GÖREVLER VE ÖZELLİKLER:
  
  - Kapı açma kapama kontrolü: Kullanıcı doğru şifreyi girerse kapıyı açar. Yanlış şifre veya şifresiz girişleri engeller. tools.py'daki door_control toolu bu kontrolü gerçekleştirir.
  
  - Kargo kontrolü: Gelen kargolar hakkında sorgulama yapılmasını sağlar. tools.py'daki cargo toolu bu kontrolü gerçekleştirir.
  
  - Misafir karşılama: Bu işlevi yerine getirirken iki mod var. İlki, kullanıcı eğer birisinin misaifiri olduğunu söylerse, ziyaret etmek istediği kişinin bilgilerini, ofisteki konumunu söyler. İkinci mod ise korumalı mod. Kullanıcı, bir personelin misaifrlerini öğrenmek istediği zaman ancak şifreyi girerse o personelin misafirleri hakkındaki bilgiye ulaşabilir.  tools.py'daki guest ve which_guest_of_staff toolları bu kontrolleri gerçekleştirir.
  
  - Personel bilgisi sorgulama: Kullanıcı adı (personel adı) üzerinden sorgulama yapılır. staff_info toolu görevlidir.
  
  - Email ile haberleşme: send_guest_email toolu ile haber iletilmek istenen şirket personeline otomatik e-mail atılır
  
  - Güvenlik: bu işlevi yerine getiren iki ayrı araç var. İlki konuşmalardaki tehlikeli ifadeleri veya yardım çağrılarını değerlendiren security toolu. Bu tool, tehlike içeren durumlarda alarm durumunu aktifleştirir. İkinci araç ise video kameradan her saniye görntü çekerek bu görüntülerde sıkıntı arz eden durum olup olmadığını kontrol eder. Görüntü tehlikeli nesne içeriyorsa alarm durumunu aktifleştirir.

  - tts ve stt: Kullanıcı dilerse bota iletmek istediği mesajları konuşma yoluyla iletebilir. Bot, verdiği mesajları sohbet kutusuna yazmanın yanı sıra seslendirerek de iletir.

BACKEND DOSYALARI:

   - security_data.db : burada şirket personeli hakkındaki bilgiler bulunur. gelen kargo, email adresleri, beklenen ziyaretçiler, ofisteki konumlar vb.
  
   - graph.py : langgraph framworkü içerisinde tool'ların ve llm'in etkileşiminden sorumludur.
  
   - mailsender.py : Botun otomatik olarak mail yollaması için mail servisine erişimini düzenler.
  
   - tools.py : gerekli tooların fonksiyon tanımlarını içerir.
  
   - visionYOLO_test.py : Geliştirme sürecinde eğitilen YOLO varyasyonlarınını doğru çalıştığını kontrol etmek için gerekli test ortamını sağlar.
  
   - main.py : Backend;in end pointlerini tutan ve statelerin güncellenmesinde yönetilmesinden sorumlu en üst katman. Sohbet geçmişi frontendde tutulduğu için /chat kanalı kendisine gelen sohbet geçmişiyle beraber sohbet cevabını llme iletir. /camera_statu kanalı ise arka planda her saniye görüntüyü değerlendirir. Endpointte sunulan kamera alarm durumunu her saniye yeniler ve frontende sunar.

KODU NASIL ÇALIŞTIRMALIYIM?

  1) Şirket sunucusuna bağlı bir bilgisayarda yeni bir terminal açıp **ssh alper@192.168.0.94** komutu girilmeli.

  2) Bağlandıktan sonra açılan terminalde **export OLLAMA_HOST=0.0.0.0:11434** kodu ile sunucu yayınlanmalı.

  3) **ollama serve** komutu ile ollama sunucusu ayağa kaldırılır.

  4) Proje klasöründe backend dizinine gelip yeni terminal açılmalı ve **source venv/bin/acvtivate** komutu ile ortam etkinleştirilir.

  5) Yine aynı terminalde **uvicorn main:app --reload** komutu ile backend ayağa kaldırılır.

  6) Son olarak frontend klasöründe yer alan index.html ile arayüze giriş yapılır. 
 
NOT: mailsender aracı kişisel mail hesabım üzerinden çalıştığı için test aşamasında kendi mailinizi ve email pass inizi girmeniz gerekir. 
