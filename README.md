# 🛡️ Guard Bot Sistemi - Gelişmiş Sunucu Koruma

Yüksek güvenlik özellikleri ile iki adet 24/7 çalışan guard bot sistemi.

---

## ✨ Özellikler

### 🤖 İkili Bot Sistemi
- **Guard Bot 1**: Birincil koruma botu
- **Guard Bot 2**: Yedek koruma botu
- Birisi offline düşerse diğeri korumaya devam eder
- Otomatik durum takibi ve kalp atışı sistemi

### 🎙️ Ses Kanalı Yönetimi
- Belirlenen ses kanallarında 24/7 bağlı kalır
- Ses kanalı düşmesi otomatik olarak algılanır
- Yeniden bağlantı sağlanır

### 🔒 Güvenlik Özellikleri
- ✅ Anti-Spam Koruması
- ✅ Anti-Raid Koruması
- ✅ Otomatik Rol Atama
- ✅ Sunucu Kilitleme/Kilidi Açma
- ✅ Mesaj Silme İzleme
- ✅ Üye Katılış/Ayrılış İzleme
- ✅ Rol Değişimi İzleme
- ✅ Uyarı Sistemi
- ✅ Günlük Kanalına Rapor

### ⚙️ Yönetim Sistemi
- `.setup` komutu ile tam kurulum
- Konfigürasyon dosyası ile verilerin kalıcı kaydı
- Bot sahip ID'si doğrulaması
- Gelişmiş Cog sistemi

---

## 📋 Kurulum

### 1️⃣ Gerekli Kütüphaneleri Yükle

```bash
pip install -r requirements.txt
```

### 2️⃣ Discord Bot'larını Oluştur

1. [Discord Developer Portal](https://discord.com/developers/applications) adresine git
2. "New Application" ile yeni app oluştur
3. Bot token'ını kopyala
4. İki bot için bunu tekrarla

### 3️⃣ Bot İzinlerini Ayarla

Developer Portal'da her bot için:

```
Scopes: bot
Permissions:
  - Manage Roles
  - Manage Channels
  - Manage Messages
  - Kick Members
  - Ban Members
  - Send Messages
  - Read Messages/View Channels
  - Connect (Voice)
  - Speak (Voice)
  - Move Members
  - Manage Guild
  - View Audit Log
```

Generated URL'i kullanarak bot'u sunucuya ekle.

### 4️⃣ Token'ları Ayarla

`.env` dosyasını oluştur ve token'ları ekle:

```env
BOT1_TOKEN=your_bot1_token_here
BOT2_TOKEN=your_bot2_token_here
```

### 5️⃣ Kurulum Komutunu Çalıştır

Bot 1'i başlat:
```bash
python main_bot1.py
```

Discord'da sunucunuzda `.setup` komutunu çalıştır:
```
.setup
```

Talimatları takip et:
- Sunucu otomatik kaydedilir
- Ses kanalını ping et
- Günlük kanalını ping et (opsiyonel)
- Bot 2 token'ını .env'ye ekle

---

## 🚀 Botları Çalıştırma

### Terminal 1 - Bot 1:
```bash
python main_bot1.py
```

### Terminal 2 - Bot 2:
```bash
python main_bot2.py
```

Her iki bot da çalışmalı ve ses kanalına bağlanmalı.

---

## 📝 Komutlar

### Temel Komutlar

| Komut | Kullanım | Açıklama |
|-------|----------|---------|
| `.setup` | `.setup` | Guard Bot sistemini kur |
| `.status` | `.status` | Sistem durumunu göster |
| `.check_bot` | `.check_bot` | Botların durumunu kontrol et |

### Moderasyon Komutları

| Komut | Kullanım | Açıklama |
|-------|----------|---------|
| `.warn` | `.warn @kullanıcı [sebep]` | Kullanıcıyı uyar |
| `.purge` | `.purge [sayı]` | Son N mesajı sil |
| `.kick` | `.kick @kullanıcı [sebep]` | Kullanıcıyı kickle |
| `.ban` | `.ban @kullanıcı [sebep]` | Kullanıcıyı banlama |

### Güvenlik Komutları

| Komut | Kullanım | Açıklama |
|-------|----------|---------|
| `.lock_server` | `.lock_server` | Sunucuyu kilitler |
| `.unlock_server` | `.unlock_server` | Sunucunun kilidini açar |
| `.set_protection` | `.set_protection anti_spam on` | Güvenlik özelliğini aç/kapat |

### Yönetim Komutları

| Komut | Kullanım | Açıklama |
|-------|----------|---------|
| `.help` | `.help [komut]` | Yardım |
| `.help [kategori]` | `.help moderasyon` | Kategori yardımı |

---

## 🔧 Konfigürasyon

### bot_config.json

Otomatik olarak oluşturulur, ihtiyaç duyarsan elle de düzenleyebilirsin:

```json
{
    "owner_id": 123456789,
    "guild_id": 987654321,
    "voice_channel_id": 111111111,
    "log_channel_id": 222222222,
    "max_warnings": 3,
    "security_features": {
        "anti_spam": true,
        "anti_raid": true,
        "auto_role": true,
        "server_lock": false
    }
}
```

### Başlıca Ayarlar

- **owner_id**: Bot sahip ID'si (Admin komutları için)
- **max_warnings**: Kicklemeden önce uyarı sayısı
- **security_features**: Güvenlik özellikleri
- **protected_roles**: Korunan roller (Yöneticiler vb.)

---

## 📊 Sistem Mimarisi

```
Guard Bot Sistemi
├── main_bot1.py          (Bot 1 - Birincil)
├── main_bot2.py          (Bot 2 - Yedek)
├── guard_bot1.py         (Guard Bot 1 Cog)
├── guard_bot2.py         (Guard Bot 2 Cog)
├── setup_manager.py      (Kurulum Yöneticisi)
├── shared_utils.py       (Ortak Fonksiyonlar)
├── bot_config.json       (Konfigürasyon - Otomatik Oluşturulur)
└── bot_status.json       (Durum Takibi - Otomatik Oluşturulur)
```

---

## 🔄 Botlar Arası İletişim

### Durum Takibi
- Her bot 60 saniyede bir "kalp atışı" gönderir
- Durum `bot_status.json` dosyasında kaydedilir
- Diğer bot otomatik olarak durum kontrolü yapar

### Yedekleme Mantığı
```
Bot 1 Online  →  Koruma Sağlıyor
Bot 2 Online  →  Yedek Kopyası

Bot 1 Offline →  Bot 2 Korumaya Devam
Bot 2 Offline →  Bot 1 Korumaya Devam
```

---

## ⚠️ Hata Giderme

### Bot Bağlanamıyor
```
❌ "Failed to connect to voice channel"
✅ Çözüm: Discord.py ses geçkişlerini yeniden kontrol et
```

### Token Hatası
```
❌ "BOT1_TOKEN tanımlanmamış"
✅ Çözüm: .env dosyasına token ekle
```

### İzin Hatası
```
❌ "Missing Permissions"
✅ Çözüm: Bot rolleri yönetici yetkisine yükselt
```

### Ses Kanalı Bulunamadı
```
❌ "Voice channel not found"
✅ Çözüm: .setup'ı tekrar çalıştır, kanalı doğru seç
```

---

## 📚 Dosya Yapısı Detayları

### shared_utils.py
- `ConfigManager`: Konfigürasyon yönetimi
- `StatusManager`: Bot durum takibi
- `SecurityManager`: Güvenlik olayları
- Helper fonksiyonlar

### guard_bot1.py & guard_bot2.py
- Güvenlik olayları (member join, message delete, vb.)
- Moderasyon komutları
- Ses kanalı yönetimi
- Durum kontrolü

### setup_manager.py
- Interactive kurulum arayüzü
- Sistem durumu raporu
- Güvenlik ayarları yönetimi

---

## 🎯 İleri Özellikler (Gelecek Sürüm)

- [ ] Database entegrasyonu (SQLite/PostgreSQL)
- [ ] Web dashboard
- [ ] İleri istatistik
- [ ] Otomatik backup
- [ ] Discord.py 3.0 uyumluluğu
- [ ] Kubernetes desteği
- [ ] Multi-server yönetim
- [ ] Advanced filtering sistemi

---

## 📄 Lisans

Kişisel kullanım için. Ticari kullanım için izin gerekir.

---

## 💬 Destek

Sorunlar için loglara bakın:
- Guard Bot 1: `main_bot1.py` çıktısı
- Guard Bot 2: `main_bot2.py` çıktısı
- Günlük Kanalı: Discord'daki mesajlar

---

**🔐 Güvenlik Uyarısı**: Token'larınızı asla herkese göstermeyin!
