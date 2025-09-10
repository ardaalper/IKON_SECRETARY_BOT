Projenin amacı, bir ofiste kapıcı/sekreter işlevi görecek yapay zeka entegrasyonu yapmak.

Projede kullandığım llm modeli: GPT-OSS:20b OLLAMA

Projede kullandığım görüntü algılama modeli: YOLO v11

Projede kullandığım görüntü algılama veri seti: https://universe.roboflow.com/harmfull-objects/harmful-objects-wmmdi

**GİRİŞ:**

GRAPH.PY

Langgraph kütüphanesini ve teercih edilen llm'i bir araya getiren dosyadır. Graph, kendi içerisinde iki düğüm barındırır. Bunlar call_model ve 
tool_node düğümleridir. Tool_node düğümü llm'in gerekli gördüğü durumlar karşısında çağırması gereken tool ları barındırır. Bu toollar kendi 
içlerinde tanımlarını ve örnek çalışma durumlarını barındırır. Bu sayede llm hangi tool'u çağırması gerektiğini anlar.

AgentState dediğimiz yapı ise TypedDict inherited bir yapıdır ve chatin mesajlaşma trafiğini takip edebilmesi için bir mesaj arrayi barındırır.
Bunun yanı sıra kapı,alarm,şifre deneme statelerini de barındırır ama llm'in bunlara erişimi yoktur. Onun yerine llm'e her mesaj yolladığımızda
bu stateleri mesajın içine gömeriz.

KODU NASIL ÇALIŞTIRMALIYIM?

  1) Şirket sunucusuna bağlı bir bilgisayarda yeni bir terminal açıp **ssh alper@192.168.0.94** komutu girilmeli.

  2) Bağlandıktan sonra açılan terminalde **export OLLAMA_HOST=0.0.0.0:11434** kodu ile sunucu yayınlanmalı.

  3) **ollama serve** komutu ile ollama sunucusu ayağa kaldırılır.

  4) Proje klasöründe backend dizinine gelip yeni terminal açılmalı ve **source venv/bin/acvtivate** komutu ile ortam etkinleştirilir.

  5) Yine aynı terminalde **uvicorn main:app --reload** komutu ile backend ayağa kaldırılır.

  6) Son olarak frontend klasöründe yer alan index.html ile arayüze giriş yapılır. 
 
NOT: mailsender aracı kişisel mail hesabım üzerinden çalıştığı için test aşamasında kendi mailinizi ve email pass inizi girmeniz gerekir. 
