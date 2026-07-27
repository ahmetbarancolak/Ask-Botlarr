# 🛡️ Guard Bot Sistemi - Başlangıç Rehberi

Hoş geldin! Guard Bot Sistemi'ne 🚀

---

## 🎯 Nedir Bu Sistem?

2 adet bağımsız Discord botu, aynı anda 24/7 çalışan ve birbirine yedek olan **gelişmiş sunucu koruma sistemi**.

### ✨ Temel Özellikleri

- ✅ **İkili Bot Sistemi**: Birisi crash'leyse diğer devam eder
- 🎙️ **Ses Kanalı Koruma**: Belirlenen kanallarda 24/7 bağlı
- 🔒 **Gelişmiş Güvenlik**: Anti-spam, Anti-raid, Otomatik moderasyon
- ⚙️ **Kolay Kurulum**: `.setup` komutu ile tam otomatik
- 📊 **İzleme & Raporlama**: Tüm olaylar günlüğe yazılır

---

## 📚 Dokumentasyon Haritası

| Dosya | Amaç | Okuma Süresi |
|-------|------|--------------|
| **README.md** | Sistem Özeti | 5 dakika |
| **SETUP_GUIDE.md** | Adım Adım Kurulum | 15 dakika |
| **COMMANDS.md** | Tüm Komutlar | 10 dakika |
| **ARCHITECTURE.md** | Teknik Yapı | 15 dakika |

---

## 🚀 Hızlı Başlangıç (5 dakika)

### Adım 1: Gerekçi yükle
```bash
pip install -r requirements.txt
```

### Adım 2: Token'ları ekle
```bash
# .env dosyası oluştur
BOT1_TOKEN=your_token_1
BOT2_TOKEN=your_token_2
```

### Adım 3: Botları başlat
```bash
python start.py
```

### Adım 4: Setup komutunu çalıştır
```
Discord'da: .setup
```

✅ **Bitti!** Sistem şimdi 24/7 çalışıyor.

---

## 📖 Detaylı Kurulum

**Zaman:** ~30 dakika

1. [SETUP_GUIDE.md](SETUP_GUIDE.md) oku
   - Discord Developer Portal kurulumu
   - Token alma
   - İzin ayarları

2. Botları çalıştır
3. `.setup` komutu ile sistem kur
4. Komutları test et

---

## 🎮 Komutları Öğren

### Temel Komutlar

```
.setup              → Sistem kur
.status             → Durum kontrol
.check_bot          → Bot durumu
```

### Moderasyon

```
.warn @user         → Uyar
.kick @user         → Kickle
.ban @user          → Banlama
.purge 10           → Mesaj sil
```

### Güvenlik

```
.lock_server        → Sunucu kilitle
.unlock_server      → Kilidi aç
.set_protection     → Özellik ayarla
```

**Hepsi:** [COMMANDS.md](COMMANDS.md)

---

## 🏗️ Sistem Yapısı

```
İki Bot (Bot 1 + Bot 2)
    │
    ├─► Paylaşılan Ayarlar (bot_config.json)
    ├─► Durum Takibi (bot_status.json)
    │
    └─► Kalp Atışı (60 saniye)
        ├─► Bot 1: "Hala çalışıyorum"
        └─► Bot 2: "Hala çalışıyorum"

Diğer Bot Offline ise?
    └─► Aktif bot: "Korumaya devam..."
```

**Detaylı:** [ARCHITECTURE.md](ARCHITECTURE.md)

---

## ❓ Sık Sorulanlar

### S: Bot Kurulumunda Sorun Yaşıyorum
**C:** [SETUP_GUIDE.md](SETUP_GUIDE.md) adımları dikkatlice takip et. Özellikle:
- Discord Developer Portal'da bot oluştur
- Token'ları doğru gir
- İzinleri ayarla

### S: Token'ı Nereden Alırım?
**C:** [SETUP_GUIDE.md](SETUP_GUIDE.md) → Adım 1: Discord Developer Portal

### S: Botları Tek Terminalden Başlatabilir miyim?
**C:** Evet! `python start.py` menüsü kullan

### S: İki Bot da Gerekli mi?
**C:** Hayır, tek bot de çalışır ama yedekli sistem için 2 tavsiye edilir

### S: Ses Kanalında Hiçbir Şey Yapmıyor mı?
**C:** Normal! Botlar koruma için orada durur ama sadece açıktan burada

### S: Güvenlik Komutları Başka Kişiler Kullanabilir mi?
**C:** Hayır, sadece bot sahip (`owner_id`) kullanabilir

---

## 🔐 Güvenlik İpuçları

⚠️ **ÖNEMLİ:**
1. Token'ları asla GitHub'a yükleme
2. `.env` dosyasını `.gitignore`'a ekle
3. Token'ları hiç kimseyle paylaşma
4. Eğer token ifşa olduysa, Discord'da regen et

---

## 📞 Sorun Giderme

### Bot Başlamıyor
```
❌ "BOT1_TOKEN tanımlanmamış"
✅ .env dosyası var mı? Token doğru mu?
```

### Komutlar Çalışmıyor
```
❌ "CommandNotFound"
✅ Prefix doğru mu? (varsayılan: .)
✅ Bot admin izni var mı?
```

### Ses Kanalına Bağlanamıyor
```
❌ "Failed to connect"
✅ Kanal ID doğru mu?
✅ Bot Connect izni var mı?
```

---

## 🌳 Dosya Yapısı

```
Aşk Botlar/
│
├── 📘 Rehberler
│   ├── README.md             ← ANA REHBER (Buradan Başla!)
│   ├── SETUP_GUIDE.md        ← KURULUM TALIMATARI
│   ├── COMMANDS.md           ← KOMUT REFERANSI
│   └── ARCHITECTURE.md       ← TEKNİK YAPIŞ
│
├── 🤖 Bot Kodları
│   ├── main_bot1.py          Bot 1
│   ├── main_bot2.py          Bot 2
│   ├── guard_bot1.py         Bot 1 Özellikleri
│   ├── guard_bot2.py         Bot 2 Özellikleri
│   ├── setup_manager.py      Setup & Yönetim
│   ├── advanced_features.py  İleri Özellikler
│   └── shared_utils.py       Ortak Fonksiyonlar
│
├── ⚙️ Ayarlar
│   ├── bot_config.json       Sistem Ayarları
│   ├── .env                  Token'lar (Gizli!)
│   └── .env.example          Şablon
│
├── 🚀 Başlangıç
│   └── start.py              Hızlı Başlat
│
├── 📦 Kütüphaneler
│   └── requirements.txt      Gerekli Paketler
│
└── 📄 Bu Dosya
    └── INDEX.md              (Şu an burasında)
```

---

## 📚 Okuma Sırası (Tavsiye)

### 1️⃣ İlk Defa Kurulum Yapıyorsanız

1. **README.md** (5 dk) - Genel bakış
2. **SETUP_GUIDE.md** (30 dk) - Adım adım
3. Botları başlat ve test et
4. **COMMANDS.md** (10 dk) - Komutları öğren

### 2️⃣ Zaten Kurulu, Derinlemesine Öğreniyorsanız

1. **ARCHITECTURE.md** (15 dk) - Nasıl çalışıyor
2. Kod dosyalarına bak
3. `shared_utils.py` - Temel fonksiyonlar
4. `guard_bot1.py` - Güvenlik olayları

### 3️⃣ Sorun Çözmek İçin

1. Terminal hatalarını oku
2. [SETUP_GUIDE.md](SETUP_GUIDE.md) → Hata Çözümü
3. [COMMANDS.md](COMMANDS.md) → Komut Detayları
4. GitHub Issues (future)

---

## 💡 İpuçları

### Terminal'de Botları Çalıştırırken
- Iki ayrı terminal penceresi aç
- Bot 1: `python main_bot1.py`
- Bot 2: `python main_bot2.py`
- Çıkmak: `Ctrl+C`

### Setup Sorunları Yaşıyorsanız
- Ses kanalını ping et: `#channel-name`
- Log kanalını ping et: `#logs`
- Günlük kanal isteğe bağlıdır

### Komut İçin Parametre Gerekmiyorsa
- `.purge` = Son 10 mesajı sil
- `.reputation` = Kendi itibarım

---

## 🎓 Gelişmiş Konular

### Konfigürasyonu Elle Düzenleme

`bot_config.json` dosyasını düzenle:

```json
{
    "owner_id": 123456789,              // Kendi ID'niz
    "max_warnings": 3,                  // Uyarı limiti
    "security_features": {
        "anti_spam": true,              // Spam koruması
        "auto_role": true               // Otomatik rol
    }
}
```

### Gelişmiş Güvenlik Özellikleri

`advanced_features.py` dosyasında:
- Anti-spam sistemi
- Anti-raid algılaması
- Kullanıcı risk skoru
- İtibar sistemi

---

## 📊 Sistem Genel Bakış

```
🟢 Bot 1 Çevrimiçi
🟢 Bot 2 Çevrimiçi
───────────────────
✅ Sunucu Koruması AKTIF
✅ Ses Kanalı: #genel-ses
✅ Günlük Kanalı: #logs
✅ Güvenlik Özellikleri: 4/4
✅ Kalp Atışı: ✓ ✓
```

---

## 🚀 Sonraki Adımlar

1. **Kurulum Tamamla** → [SETUP_GUIDE.md](SETUP_GUIDE.md)
2. **Komutları Öğren** → [COMMANDS.md](COMMANDS.md)
3. **Sistem Yapısını Anla** → [ARCHITECTURE.md](ARCHITECTURE.md)
4. **Özelleştir** → Kod dosyalarını düzenle

---

## 📞 Destek

**Sorunu Bulursan:**
1. [SETUP_GUIDE.md](SETUP_GUIDE.md) → Hata Çözümü oku
2. Terminal çıktısını kontrol et
3. `bot_status.json` durumunu kontrol et

**Terminal'e Bak:**
- `python main_bot1.py` çıktısı
- Hatalar ve uyarılar orada

**Discord'a Bak:**
- Günlük kanalındaki mesajlar
- Bot status/presence
- Server logs

---

## ✅ Kontrol Listesi (Kurulum Sonrası)

- [ ] Bot 1 çevrimiçi mi?
- [ ] Bot 2 çevrimiçi mi?
- [ ] Her ikisi de ses kanalında mı?
- [ ] `.status` komutu çalışıyor mu?
- [ ] `.check_bot` diğer botu gösteriyor mu?
- [ ] Günlük kanalı alıyor mu?
- [ ] Hiç hata var mı?

---

**🎉 Başarıyla Başladın!**

Eğer hala sorun yaşıyorsan, [SETUP_GUIDE.md](SETUP_GUIDE.md) kontrol et.

Mutlu botları tutmalar! 🤖✨
