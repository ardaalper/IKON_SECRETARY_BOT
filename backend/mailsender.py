import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

def send_email(from_email, to_email, password, subject, body):
    msg = MIMEMultipart()

    
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    msg.attach(MIMEText(body, 'plain'))
    image_path = './data/ikon_logo.png'
    if image_path:
        with open(image_path, 'rb') as img_file:
            img = MIMEImage(img_file.read())
            img.add_header('Content-ID', '<attached_image>')
            img.add_header('Content-Disposition', 'inline', filename=image_path)
            msg.attach(img)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()
        print("Mail başarıyla gönderildi.")
        return f"misafir için mail ({to_email}) adresine gönderildi."
        
    except Exception as e:
        print(f"Mail gönderilirken hata oluştu: {e}")
        return "Mail gönderilirken hata oluştu."
