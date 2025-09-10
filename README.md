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

### MAILSENDER.PY

Bu kod, bir Python programı içinde e-posta göndermeyi sağlayan bir fonksiyon tanımlar. send_email fonksiyonu, gönderen e-posta adresi 
(from_email), alıcı e-posta adresi (to_email), gönderenin şifresi (password), konu (subject) ve içerik (body) parametrelerini alarak çalışır. 
Fonksiyon ilk olarak bir MIMEMultipart nesnesi oluşturur; bu nesne sayesinde hem metin hem de görsel gibi farklı içerikler aynı e-postaya 
eklenebilir. Mesajın konu, gönderen ve alıcı bilgileri bu nesneye eklenir. Ardından e-posta gövdesi düz metin olarak eklenir. Eğer belirlenen 
dizinde (./data/ikon_logo.png) bir görsel dosyası varsa, bu görsel okunup MIMEImage kullanılarak e-postaya eklenir ve inline (gömülü) görsel 
olarak gönderilecek şekilde ayarlanır. E-posta gönderme işlemi için smtplib kütüphanesiyle Gmail’in SMTP sunucusuna (smtp.gmail.com, port 587) 
bağlanılır, TLS şifreleme başlatılır ve kullanıcı adı-şifre ile giriş yapılır. Giriş başarılı olursa hazırlanan mesaj gönderilir ve bağlantı 
kapatılır. İşlem başarılı olursa ekrana ve dönüş değerine başarı mesajı yazdırılır; bir hata olursa hata mesajı yakalanır ve kullanıcıya 
bildirilir. Bu sayede fonksiyon, hem yazılı mesaj hem de görsel içerebilen güvenli bir e-posta gönderme mekanizması sağlar.

### DATABASE.PY

- **setup_database()** fonksiyonu, eğer yoksa data klasörünü oluşturur ve içinde security_data.db adında bir SQLite veritabanı açar.
  Veritabanında daha önce tablolar oluşturulmamışsa guests, cargos, emergencies ve staff tablolarını oluşturur. Yani bu fonksiyon projenin
  başlangıcında veritabanını hazır hale getirir ve tabloların var olup olmadığını kontrol ederek eksik olanları ekler.

- **get_db_connection()** fonksiyonu, var olan security_data.db dosyasına bağlantı kurar. Eğer data klasörü yoksa önce klasörü oluşturur. Bu
  sayede, sistem her çağrıldığında doğrudan veritabanına güvenli şekilde bağlanmayı sağlar.

- **get_all_records()** fonksiyonu, guests, cargos, emergencies ve staff tablolarındaki tüm verileri çekip döndürür. Her tablo için kolon
  adlarını alır ve satır verilerini sözlük (dictionary) formatına dönüştürerek daha okunabilir hale getirir. Eğer bir tablo bulunmazsa,
  kullanıcıya uyarı mesajı verir ve ilgili tablo için boş liste döndürür.

- **add_record(table_name, record_data)** fonksiyonu, belirtilen tabloya yeni bir kayıt ekler. SQL enjeksiyonunu engellemek için parametre
  bağlama (?) kullanır. Kolon adlarını ve değerleri otomatik olarak record_data sözlüğünden çıkarır ve sorguya ekler. İşlem başarılı olursa
  onay mesajı döner; hata olursa açıklayıcı bir hata mesajı ile kullanıcıya bilgi verir.

- **delete_record(table_name, record_id)** fonksiyonu, verilen tablo içinden belirtilen id değerine sahip kaydı siler. Eğer kayıt bulunursa
  silme işlemini yapar ve başarı mesajı döner, kayıt yoksa kullanıcıya silinecek bir şey bulunamadığını bildirir. Hatalı sorgu durumunda da
  uygun hata mesajı üretir.

### MAIN.PY

Bu dosya, projenin merkezi yönetim dosyasıdır. Tüm güvenlik sistemi iş akışını tek bir noktada toplar. FastAPI kullanılarak API tabanlı bir 
mimari oluşturulmuş, böylece sohbet sistemi, kamera analizi, kapı ve alarm yönetimi ile veritabanı işlemleri tek bir servis üzerinden kontrol 
edilebilir hale getirilmiştir.

- **FastAPI ve Uygulama Yapısı**
  Uygulama, FastAPI üzerine inşa edilmiştir. CORS ayarları sayesinde herhangi bir istemci bu API’ye güvenli şekilde bağlanabilir. Bu katmanda
  ayrıca Pydantic modelleri kullanılarak API’ye gönderilen verilerin doğruluğu garanti altına alınır. Örneğin, Message ve ChatHistory modelleri
  sohbet verilerini, RecordData ve DeleteData modelleri ise veritabanı CRUD işlemlerini temsil eder.

- **Sohbet ve Agent Akışı**
  Sohbet sistemi LangGraph üzerine kuruludur. Kullanıcıdan gelen mesajlar /chat endpoint’i üzerinden alınır. Bu mesajlar, LangGraph
  aracılığıyla işlenerek yapay zekâ modeline gönderilir ve sistem durumu (kapı açık/kapalı, alarm aktif/pasif, şifre denemeleri) sürekli
  güncellenir. Modelin ürettiği yanıtlar, sohbet geçmişine eklenerek istemciye döndürülür. Böylece gerçek zamanlı olarak kapı ve alarm kontrolü
  sağlanabilir.

- **Kamera Analizi ve Güvenlik**
  Kamera analizi arka planda çalışan ayrı bir thread üzerinde gerçekleşir. Bu işlem için YOLO modeli yüklenmiştir. Kamera sürekli olarak analiz 
  edilir ve tehlikeli nesneler (knife, axe, scissors, hammer vb.) tespit edildiğinde sistem otomatik olarak alarm durumunu "Aktif" hale
  getirir. Anlık kamera durumu /camera_status endpoint’i üzerinden ön yüze iletilir. Böylece kullanıcı, sistemde bir tehdit algılandığında
  canlı olarak haberdar olabilir.

- **Admin Paneli ve Veritabanı İşlemleri**
  Admin paneli için birkaç farklı uç nokta tanımlanmıştır. /admin/login basit bir şifre kontrolü yaparak giriş sağlar. /admin/records mevcut
  tüm kayıtları döndürürken, /admin/records/add yeni bir güvenlik kaydı eklemeye, /admin/records/delete ise ID’ye göre bir kaydı silmeye imkan
  tanır. Tüm bu işlemler, SQLite tabanlı bir veritabanı üzerinde gerçekleştirilir. Bu sayede güvenlik verilerinin yönetimi kolayca yapılabilir.

Bu yapı sayesinde sistem, hem otomatik (kamera analizi, şifre denemeleri, alarm yönetimi) hem de manuel (sohbet üzerinden kontrol, admin
paneli CRUD işlemleri) olarak çalışır. Kullanıcı, sohbet ekranı üzerinden kapıyı açıp kapatabilir, alarmı kontrol edebilir veya misafir/kargo 
bilgilerini sorgulayabilir. Kamera tarafında tehlikeli nesne algılanırsa sistem otonom şekilde alarma geçer. Admin tarafında ise tüm güvenlik 
verileri merkezi bir panel üzerinden yönetilebilir.

# MODELLERİN KARŞILAŞTIRMASI

### Rasa

Rasa, chatbot geliştirme ve bakımında en kontrol edilebilir açık kaynak platform olarak öne çıkar. Hem kural tabanlı hem de ML tabanlı diyalog 
akışlarını yönetmek için kapsamlı araçlar sunar. Kullanıcı girişlerini intent ve entity olarak analiz edip, belirlenen akışlara göre yanıt 
üretebilirsiniz. Bakım açısından, tüm veriler ve modeller yerel sunucuda tutulduğu için şeffaf ve güvenlidir, istediğiniz zaman veri 
ekleyebilir, akışı değiştirebilir veya yeni senaryolar ekleyebilirsiniz. Ancak LLM’ler kadar “doğal” ve yaratıcı yanıt üretemez; genellikle 
belirli iş süreçleri ve SSS’ler için uygundur.

Projemde ilk denediğim yapı buydu. Çok hızlı çalışan bir platform. Aslında sabit bir diyalog ağacı kurgulamamız gerektiği durumlarda en 
işlevsel platformun bu olduğunu düşünüyorum. Ama esnek olması gereken ve bu esneklik içerisinde tool çalıştırması gereken senaryolarda yetersiz 
kalıyor.

### GPT‑OSS

GPT‑OSS, chatbot bakımında esnek ve düşük maliyetli bir çözüm sunar. Yerel çalıştırılabilir ve fine-tune edilebilir olması, şirketlerin kendi 
chatbot verisiyle modeli geliştirmesine imkan tanır. GPT‑OSS’in büyük bağlam penceresi ve güçlü metin üretim kapasitesi, kullanıcı sorularına 
daha doğal ve çeşitli yanıtlar vermeyi mümkün kılar. Bakım açısından, veri güncelleme ve özel yanıt optimizasyonu için modelin yeniden 
eğitilmesi veya prompt engineering yapılması gerekir. LLM olduğu için, Rasa’ya kıyasla “sihirli” gibi görünen yanıtlar üretir, ancak çok dar 
kapsamlı veya kritik bilgi gerektiren durumlarda hatalar olabilir.

Projemin en son halinde kullandığım ve en verim aldığım model. Lokal olarak şirket bilgisayarında çalışırken diyalog esnasında yalnızca iki 
saniyede cevap üretebiliyordu. Ve bu cevaplarda tool kullansa bile süre değişmiyordu. GPT-OSS, toolları en etkin biçimde kullanan model. aynı 
zamanda girdiğim sistem propmtlara bağlılığı da diyalog esnasında hiç değişmiyor.

### Llama (3 / 4)

Llama modelleri, açık kaynaklı ve yüksek performanslı LLM’ler olarak chatbot bakımında GPT‑OSS’e benzer avantajlar sağlar. Özellikle Llama 4 
serisi, uzun bağlamları takip edebilir ve kompleks diyalogları yönetebilir. Bakım açısından, model üzerinde fine-tune yapabilir veya kendi veri 
setinizi kullanarak domain-specific chatbot geliştirebilirsiniz. Llama’nın açık kaynak olması, güvenlik ve özelleştirme için esneklik sağlar. 
Dezavantajı, Rasa kadar sistematik akış yönetimi araçları sunmaması; bu nedenle diyalog mantığını modelin kendisine bırakmanız gerekebilir.

Türkçe dil desteği biraz zayıf. Tool desteği var ama tool konfigürasyonu aşırı karmaşık olmasa da openai modellerinden daha zor.

### GPT‑4o

GPT‑4o, chatbot bakımında en güçlü ve multimodal modeldir. Metin, ses ve görsel girdileri işleyebilir, bağlamı uzun süre takip edebilir ve 
insan benzeri yanıtlar üretebilir. Bakım açısından API üzerinden kullanıldığı için modelin altyapısı sizin kontrolünüzde değildir, ancak prompt 
engineering ile yönlendirme mümkündür. GPT‑4o, kritik iş süreçleri ve müşteri etkileşimi için yüksek kaliteli yanıt sağlar; ancak maliyeti 
yüksektir ve veri gizliliği açısından yerel model gibi tam kontrol sunmaz.

GPT-OSS ile benzer performans gösterdi. Benim yaptığım işlemler kompleks olmadığı için net bir performans farkı gözlemleyemesem de api call 
sayesinde online çalışması cevap verme zamanını bir saniyeye düşürüyordu. Benim hedefim tamamen yerel çalışan bir sistem olduğu için tercih 
etmedim.


# KODU NASIL ÇALIŞTIRMALIYIM?

  1) Şirket sunucusuna bağlı bir bilgisayarda yeni bir terminal açıp **ssh alper@192.168.0.94** komutu girilmeli.

  2) Bağlandıktan sonra açılan terminalde **export OLLAMA_HOST=0.0.0.0:11434** kodu ile sunucu yayınlanmalı.

  3) **ollama serve** komutu ile ollama sunucusu ayağa kaldırılır.

  4) Proje klasöründe backend dizinine gelip yeni terminal açılmalı ve **source venv/bin/acvtivate** komutu ile ortam etkinleştirilir.

  5) Yine aynı terminalde **uvicorn main:app --reload** komutu ile backend ayağa kaldırılır.

  6) Son olarak frontend klasöründe yer alan index.html ile arayüze giriş yapılır. 
 
NOT: mailsender aracı kişisel mail hesabım üzerinden çalıştığı için test aşamasında kendi mailinizi ve email pass inizi girmeniz gerekir. 
