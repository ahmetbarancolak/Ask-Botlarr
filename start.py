"""
Hızlı Başlangıç Scripti
Guard Bot Sistemini başlatır
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_requirements():
    """Gerekli bileşenleri kontrol et"""
    print("✅ Gerekli bileşenler kontrol ediliyor...")
    
    # Python versiyonu
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ gerekli!")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} kullanılıyor")
    
    # Kütüphaneler
    try:
        import discord
        print(f"✅ discord.py {discord.__version__} yüklü")
    except ImportError:
        print("❌ discord.py yüklü değil. 'pip install -r requirements.txt' çalıştır")
        return False
    
    # .env dosyası
    if not os.path.exists('.env'):
        print("⚠️  .env dosyası bulunamadı")
        if os.path.exists('.env.example'):
            print("📄 .env.example dosyasından .env dosyası oluştur ve token'ları ekle")
        return False
    
    # Token kontrolü
    from dotenv import load_dotenv
    load_dotenv()
    
    bot1_token = os.getenv('BOT1_TOKEN')
    bot2_token = os.getenv('BOT2_TOKEN')
    
    if not bot1_token or bot1_token == "your_bot1_token_here":
        print("❌ BOT1_TOKEN tanımlanmamış veya geçersiz")
        return False
    
    if not bot2_token or bot2_token == "your_bot2_token_here":
        print("⚠️  BOT2_TOKEN tanımlanmamış (ikili sistem çalışmaz)")
        return False
    
    print("✅ Token'lar kontrol edildi")
    return True

def start_bots():
    """Botları başlat"""
    print("\n🚀 Guard Bot Sistemi başlatılıyor...\n")
    
    if not check_requirements():
        print("\n❌ Başlatma başarısız. Lütfen gereken adımları tamamla.")
        sys.exit(1)
    
    print("=" * 50)
    print("BAŞLANGIC SECENEKLERI:")
    print("=" * 50)
    print("1. İki Botu Aynı Anda Başlat")
    print("2. Bot 1'i Başlat")
    print("3. Bot 2'yi Başlat")
    print("4. Çıkış")
    print("=" * 50)
    
    choice = input("\nSeçiminizi yapın (1-4): ").strip()
    
    if choice == "1":
        print("\n📢 Not: İki ayrı terminal penceresi açılacak\n")
        
        # Windows
        if platform.system() == "Windows":
            subprocess.Popen(["start", "cmd", "/k", "python main_bot1.py"], shell=True)
            subprocess.Popen(["start", "cmd", "/k", "python main_bot2.py"], shell=True)
        # macOS
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", "-a", "Terminal", "python main_bot1.py"])
            subprocess.Popen(["open", "-a", "Terminal", "python main_bot2.py"])
        # Linux
        else:
            subprocess.Popen(["gnome-terminal", "--", "python", "main_bot1.py"])
            subprocess.Popen(["gnome-terminal", "--", "python", "main_bot2.py"])
        
        print("✅ Botlar başlatıldı!")
        print("⏳ Her botu Discord'da kontrol et")
        input("Çıkmak için Enter'e bas...")
    
    elif choice == "2":
        print("\n🤖 Bot 1 başlatılıyor...\n")
        try:
            subprocess.run(["python", "main_bot1.py"], check=True)
        except KeyboardInterrupt:
            print("\n\n⏹️  Bot 1 durduruldu")
        except Exception as e:
            print(f"\n❌ Hata: {e}")
    
    elif choice == "3":
        print("\n🤖 Bot 2 başlatılıyor...\n")
        try:
            subprocess.run(["python", "main_bot2.py"], check=True)
        except KeyboardInterrupt:
            print("\n\n⏹️  Bot 2 durduruldu")
        except Exception as e:
            print(f"\n❌ Hata: {e}")
    
    elif choice == "4":
        print("👋 Çıkılıyor...")
        sys.exit(0)
    
    else:
        print("❌ Geçersiz seçim")
        start_bots()

if __name__ == "__main__":
    try:
        start_bots()
    except KeyboardInterrupt:
        print("\n\n👋 Programdan çıkılıyor...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {e}")
        sys.exit(1)
