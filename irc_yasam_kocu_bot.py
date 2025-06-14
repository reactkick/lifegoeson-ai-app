# irc_yasam_kocu_bot.py

import irc.bot
import irc.strings
import openai
import os
from dotenv import load_dotenv

# .env dosyasındaki bilgileri yükle (API anahtarını güvende tutmak için)
load_dotenv()

# --- BOT AYARLARI ---
# Bu kısımları kendi bilgilerinize göre düzenleyin.
IRC_SUNUCU = "irc.kalbim.net"
IRC_PORT = 6667
IRC_KANAL = "#sohbet"  # Botun gireceği kanal, istediğiniz bir kanalla değiştirin
BOT_NICK = "YasamKocuAI"
BOT_GERCEK_AD = "LifeGoesOn AI Bot"
KOMUT = "!sor" # Bota soru sormak için kullanılacak komut

# --- OPENAI API AYARLARI ---
# OpenAI API anahtarınızı .env dosyasına eklemeniz GEREKİR.
# .env dosyası şu şekilde olmalı:
# OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    print("HATA: OPENAI_API_KEY bulunamadı.")
    print("Lütfen 'irc_yasam_kocu_bot.py' ile aynı dizinde bir .env dosyası oluşturun ve içine OPENAI_API_KEY='anahtarınız' satırını ekleyin.")
    exit()

# LifeGoesOn AI projesinin orijinal sistem mesajı (AI'ın karakterini belirler)
AI_SISTEM_MESAJI = """
Sen bir yaşam koçusun. Amacın, insanlara hayatlarının çeşitli alanlarında rehberlik etmek, 
onları motive etmek ve potansiyellerini en üst düzeye çıkarmalarına yardımcı olmaktır. 
Cevapların empatik, yapıcı, pozitif ve yol gösterici olmalı. 
Kullanıcının durumunu anladığını belli et, somut adımlar veya farklı bakış açıları sun. 
Kısa ve net cevaplar ver.
"""

def yapay_zekadan_cevap_al(kullanici_mesaji):
    """OpenAI API'ına bağlanır ve kullanıcı mesajına göre cevap alır."""
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # Daha gelişmiş bir model için "gpt-4" de kullanabilirsiniz (maliyeti etkiler)
            messages=[
                {"role": "system", "content": AI_SISTEM_MESAJI},
                {"role": "user", "content": kullanici_mesaji}
            ],
            temperature=0.7, # 0.0 (net) ile 1.0 (yaratıcı) arası bir değer
            max_tokens=250   # Cevabın maksimum uzunluğu
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API Hatası: {e}")
        return "Üzgünüm, şu anda bir sorun yaşıyorum. Lütfen daha sonra tekrar dene."

class YasamKocuBot(irc.bot.SingleServerIRCBot):
    def __init__(self, kanal, nick, sunucu, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(sunucu, port)], nick, BOT_GERCEK_AD)
        self.kanal = kanal

    def on_welcome(self, c, e):
        """Sunucuya başarıyla bağlandığında çağrılır."""
        print(f"{self.connection.get_nickname()} olarak sunucuya bağlanıldı.")
        print(f"{self.kanal} kanalına katılıyor...")
        c.join(self.kanal)

    def on_join(self, c, e):
        """Bir kanala katıldığında çağrılır."""
        print(f"{self.kanal} kanalına katıldım.")
        # c.privmsg(self.kanal, "Merhaba! Ben Yaşam Koçu AI. Bana bir soru sormak için '!sor <mesajınız>' yazabilirsiniz.")

    def on_pubmsg(self, c, e):
        """Kanala genel bir mesaj yazıldığında çağrılır."""
        # e.arguments[0] mesajın içeriğidir.
        mesaj = e.arguments[0].strip()
        
        # Mesaj bizim komutumuzla mı başlıyor?
        if mesaj.startswith(KOMUT + " "):
            soru = mesaj[len(KOMUT)+1:].strip()
            
            if not soru:
                c.privmsg(self.kanal, "Lütfen bir soru sorun. Örnek: !sor Hayat amacımı nasıl bulabilirim?")
                return
            
            print(f"<{e.source.nick}> sordu: {soru}")
            
            # Cevap alana kadar kullanıcıyı bilgilendir
            c.privmsg(self.kanal, f"{e.source.nick}, sorunu düşünüyorum...")
            
            # Yapay zekadan cevabı al
            cevap = yapay_zekadan_cevap_al(soru)
            
            print(f"AI Cevabı: {cevap}")
            
            # Cevabı kanala gönder
            c.privmsg(self.kanal, f"{e.source.nick}: {cevap}")

def main():
    print("Bot başlatılıyor...")
    bot = YasamKocuBot(IRC_KANAL, BOT_NICK, IRC_SUNUCU, IRC_PORT)
    bot.start()

if __name__ == "__main__":
    main()
