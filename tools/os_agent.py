import os
import subprocess
import webbrowser
from langchain_core.tools import tool

@tool
def execute_system_command(command: str) -> str:
    """
    Kullanıcının bilgisayarında (Windows) sistem komutları veya scriptler çalıştırır.
    Sadece güvenli ve onaylanmış işlemleri yapmak için kullan.
    Örnek komutlar: 'dir', 'notepad', 'python script.py' vs.
    """
    try:
        # GÜVENLİK 1: BEYAZ LİSTE (WHITELIST)
        # Sadece bu komutların çalıştırılmasına izin ver
        whitelist = ["dir", "echo", "ping", "python", "type", "mkdir", "cd", "ls", "cat", "node"]
        
        cmd_parts = command.strip().split()
        if not cmd_parts:
            return "Hata: Boş komut."
            
        base_cmd = cmd_parts[0].lower()
        
        # Eğer temel komut .exe vb. içeriyorsa temizle (örn: python.exe -> python)
        base_cmd = base_cmd.replace(".exe", "").replace(".cmd", "").replace(".bat", "")
        
        if base_cmd not in whitelist:
            return f"⚠️ GÜVENLİK REDDİ: '{base_cmd}' komutu Beyaz Liste'de (Whitelist) bulunmuyor. Yalnızca şu komutlara izin var: {', '.join(whitelist)}"

        # GÜVENLİK 2: İNSAN ONAYI (HITL)
        # Komutu çalıştırma, arayüze Onay İsteği gönder!
        return f"[COMMAND_REQUEST: {command}]"

    except Exception as e:
        return f"Sistem komutu doğrulama hatası: {str(e)}"

def actually_execute_command(command: str) -> str:
    """
    Sadece ve sadece kullanıcı UI üzerinden 'Onayla' butonuna bastığında çağrılır.
    Komutu güvenli bir SANDBOX klasörü içinde çalıştırır.
    """
    try:
        sandbox_dir = os.path.join(os.getcwd(), "sandbox")
        os.makedirs(sandbox_dir, exist_ok=True)
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=15, cwd=sandbox_dir)
        if result.returncode == 0:
            return f"✅ ONAYLI KOMUT ÇALIŞTI:\n{result.stdout.strip()}"
        else:
            return f"❌ ONAYLI KOMUT HATASI (Kodu {result.returncode}):\n{result.stderr.strip()}"
    except Exception as e:
        return f"Sistem komutu çalıştırılamadı: {str(e)}"

@tool
def open_website(url: str) -> str:
    """
    Kullanıcının varsayılan tarayıcısında belirtilen web sitesini açar.
    URL her zaman http:// veya https:// ile başlamalıdır.
    """
    try:
        if not url.startswith("http"):
            url = "https://" + url
        webbrowser.open(url)
        return f"Tarayıcıda {url} adresi açıldı."
    except Exception as e:
        return f"Web sitesi açılamadı: {str(e)}"

@tool
def send_email_draft(recipient: str, subject: str, body: str) -> str:
    """
    Kullanıcı adına belirtilen alıcıya e-posta taslağı hazırlar veya gönderir.
    (Şu an için taslak modunda çalışır, gerçek SMTP gönderimi için .env içinde SMTP_USER ve SMTP_PASS ayarlanmalıdır).
    """
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    
    # Gerçek gönderim ayarları eksikse simülasyon yap
    if not smtp_user or not smtp_pass:
        return f"[DRAFT MODE - SMTP AYARLARI EKSİK] E-posta Taslağı Hazırlandı:\nKime: {recipient}\nKonu: {subject}\nİçerik: {body}\n\nNot: Gerçek gönderim için .env dosyasına SMTP_USER ve SMTP_PASS ekleyiniz."
    
    import smtplib
    from email.mime.text import MIMEText
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = smtp_user
        msg['To'] = recipient

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        return f"E-posta {recipient} adresine başarıyla gönderildi."
    except Exception as e:
        return f"E-posta gönderiminde hata oluştu: {str(e)}"
