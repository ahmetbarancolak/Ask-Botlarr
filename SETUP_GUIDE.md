# 📖 Detaylı Kurulum Rehberi

## Adım 1: Discord Developer Portal Kurulumu

### 1.1 Yeni Application Oluştur
1. [Discord Developer Portal](https://discord.com/developers/applications) git
2. "New Application" butonuna tıkla
3. Uygulama adını gir (örn: "Guard Bot 1")
4. "Create" butonuna tıkla

### 1.2 Bot Ekle
1. Sol menüden "Bot" seçeneğine tıkla
2. "Add Bot" butonuna tıkla
3. Bot'un altında "TOKEN" butonuna tıkla
4. Token'ı kopyala (SECRET tutuluşu!)

### 1.3 İzinleri Ayarla
1. "Bot" sayfasında scroll down et
2. "TOKEN SCOPES" bölümünde `bot` seçeneklerini seç:
   - Applications.commands
   - Bot

3. "PERMISSIONS" bölümünde şu izinleri seç:
   - General (Manage Server, Manage Roles, Manage Channels, View Audit Log)
   - Text (Send Messages, Read Messages/View Channels, Manage Messages)
   - Voice (Connect, Speak, Move Members)
   - Moderation (Kick Members, Ban Members)

4. Alt kısımda oluşturulan URL'yi kopyala

### 1.4 Bot'u Sunucuya Ekle
1. Kopyalanan URL'yi tarayıcıya yapıştır
2. Bot'u eklemek istediğin sunucuyu seç
3. İzinleri onayla

**Not: Bu adımları 2 bot için tekrarla!**

---

## Adım 2: Proje Kurulumu

### 2.1 Python Yükle
- Python 3.8 veya üzeri gerekli
- [python.org](https://www.python.org) adresinden indir

### 2.2 Bağımlılıkları Yükle

Windows:
```bash
pip install -r requirements.txt
```

macOS/Linux:
```bash
pip3 install -r requirements.txt
```

### 2.3 .env Dosyası Oluştur

1. `.env.example` dosyasını kopyala `.env` yap
2. Token'larını ekle:

```env
BOT1_TOKEN=your_bot1_token_here_paste_it_here
BOT2_TOKEN=your_bot2_token_here_paste_it_here
```

**⚠️ ÖNEMLİ:** Token'ları GitHub veya başka yerlere saklamayın!

---

## Adım 3: Botları Çalıştırma

### Seçenek 1: start.py ile Hızlı Başlangıç

```bash
python start.py
```

Menüden seçim yap:
1. İki Botu Aynı Anda Başlat
2. Bot 1'i Başlat
3. Bot 2'yi Başlat

### Seçenek 2: Manuel Başlatma

Terminal 1:
```bash
python main_bot1.py
```

Terminal 2 (yeni terminal açt):
```bash
python main_bot2.py
```

### Seçenek 3: VSCode'da

Terminal 1:
```bash
python main_bot1.py
```

Terminal 2:
```bash
python main_bot2.py
```

---

## Adım 4: Setup Komutu

### 4.1 Botların Başlatıldığını Kontrol Et

Her bot için Discord'da:
- Bot online olmalı
- Ses kanalına bağlı olmalı
- Activity göstermesi gerekir

### 4.2 Setup Komutunu Çalıştır

Discord'da (sunucunda):
```
.setup
```

Sorular:
1. **Sunucu**: Otomatik kaydedilir
2. **Ses Kanalı**: Kanalı ping et
   ```
   #ses-kanalı
   ```
3. **Günlük Kanalı**: Kanalı ping et (isteğe bağlı)
   ```
   #logs
   ```

### 4.3 Sistem Durumunu Kontrol Et

```
.status
```

Çıktı örneği:
```
⚙️ Konfigürasyon
Sunucu: 123456789
Ses Kanalı: 987654321
Günlük Kanalı: 111111111
```

---

## 🔧 Konfigürasyon Dosyaları

### bot_config.json

Otomatik oluşturulur. Elle düzeltmek için:

```json
{
    "owner_id": 123456789,              // Bot sahip ID'niz
    "guild_id": 987654321,              // Sunucu ID'si
    "voice_channel_id": 111111111,      // Ses kanalı ID'si
    "log_channel_id": 222222222,        // Günlük kanalı ID'si
    "max_warnings": 3,                  // Kicklenmeden önceki uyarı
    "security_features": {
        "anti_spam": true,              // Spam koruması
        "anti_raid": true,              // Raid koruması
        "auto_role": true,              // Otomatik rol
        "server_lock": false            // Sunucu kilidi
    }
}
```

### ID'leri Nasıl Bulunur?

Discord'da Developer Mode:
1. User Settings → Advanced
2. Developer Mode'u açın
3. Herhangi bir şeye sağ tıkla → "Copy User ID" / "Copy Server ID" / "Copy Channel ID"

---

## ❓ Sıkça Sorulan Sorular

### S: Bot Ses Kanalına Bağlanamıyor
**C:** 
- Bot'a "Connect" ve "Speak" izni var mı?
- Ses kanalı düşmüş olabilir
- Bot token'ı doğru mu?

Çözüm:
```bash
# Bot'u yeniden başlat
# Temineleri temizle (Ctrl+C) ve tekrar çalıştır
```

### S: ".setup" Komutu Çalışmıyor
**C:** Sadece bot sahipbilgisiye çalışır
- `owner_id` kontrol et
- Kendi ID'niz kullanıyor musunuz?

### S: İki Bot Aynı Kanalda Olabilir mi?
**C:** Evet! Voice state'te görünürler ama işlem yaparlarken sorun olmaz

### S: Tokenimi Birileri Buldu, Ne Yapmalı?
**C:**
1. Hemen Discord Developer Portal git
2. "Regenerate" butonuna tıkla
3. `.env` dosyasını güncelle
4. Botları yeniden başlat

### S: Bot Hata Veriyor, Nasıl Düzeltmeliyim?
**C:** Loglara bak:
- Bot Terminal Çıktısı: Ana hatalar
- Discord Günlük Kanalı: Sunucu olayları
- `bot_status.json`: Bot durumu

---

## 🚨 Hata Çözümü

### Hata: "No module named 'discord'"

```bash
pip install -r requirements.txt
```

### Hata: "BOT1_TOKEN tanımlanmamış"

```
1. .env dosyası oluştur
2. Token'ları ekle
3. Botları yeniden başlat
```

### Hata: "Guild not found"

```
1. Guild ID'sini kontrol et
2. Bot o sunucuda var mı?
3. .setup komutunu tekrar çalıştır
```

### Hata: "Ses kanalına bağlanamadı"

```
1. Bot'un Connect izni var mı?
2. Kanal ID'si doğru mu?
3. Bot sahip izinli mi?
4. Discord API status kontrolü: discordstatus.com
```

### Hata: "Token geçersiz"

```
1. Token'ı Developer Portal'dan tekrar kopyala
2. Boş alanlar olabilir, kontrol et
3. .env dosyasını kaydet (Ctrl+S)
4. Botları yeniden başlat
```

---

## 📊 Sistem İzleme

### Günlük Kontrol Listesi

- [ ] İki Bot Çevrimiçi mi?
- [ ] Ses Kanalında mı?
- [ ] Günlük Kanalı mesaj alıyor mu?
- [ ] Hiç hata var mı?

### Komutlar ile İzleme

```bash
# Bot durumunu kontrol et
.check_bot

# Sistem durumunu kontrol et
.status

# Risk seviyesi kontrol et
.risk_check @kullanıcı
```

---

## 🎯 Sonraki Adımlar

1. **Rolleri Ayarla**
   - "Üye" rolü oluştur
   - "Yönetici" rolü kontrol et
   - Bot'u yüksek role koy

2. **Komutları Test Et**
   - `.warn @birisi test` - Uyarı sistemi
   - `.purge 5` - Mesaj silme
   - `.lock_server` - Sunucu kilitleme

3. **Günlükleri Kontrol Et**
   - Kanal içi aktivite
   - Bot hataları
   - Güvenlik olayları

---

## 📞 Destek Kaynakları

- [Discord.py Dokümantasyonu](https://discordpy.readthedocs.io/)
- [Discord Developer Portal](https://discord.com/developers)
- [Discord API Status](https://discordstatus.com/)

---

**✅ Kurulum Tamamlandı!** Artık Guard Bot sistemi 24/7 çalışıyor. 🎉
