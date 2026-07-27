# ⚙️ AYARLAR REHBERI - bot_config.json

`bot_config.json` dosyası sistemin tüm ayarlarını kontrol eder.

---

## 🔴 AYARLANMASI ZORUNLU (Başlamadan Önce)

### 1️⃣ owner_id - Bot Sahip ID'si

**Nedir?** Sistemi kontrol edebilecek tek kişinin Discord ID'si

**Nereye yazılır?**
```json
"owner_id": null   ← BU SATIRI AYARLA
```

**Nasıl bulunur?**
- Discord'da Developer Mode aç (User Settings → Advanced)
- Kendinize sağ tıklayıyorsun
- "Copy User ID" seç
- bot_config.json'da yapıştırıyorsun

**Örnek:**
```json
"owner_id": 987654321
```

**Doğrulama:**
```
.setup komutu çalıştırılınca mesaj yazıyor mı?
Evet = Doğru ✅
Hayır = Yanlış ❌
```

---

### 2️⃣ guild_id - Sunucu ID'si

**Nedir?** Guard Bot'ların koruyacağı sunucunun ID'si

**Otomatik ayarlanır mı?** Evet, `.setup` ile

**Elle ayarlamak isterseniz:**
```json
"guild_id": null   ← Sunucu ID'sini yazıyorsun
```

**Nasıl bulunur?**
- Sunucuya sağ tıkla
- "Copy Server ID" seç

**Örnek:**
```json
"guild_id": 555666777
```

---

### 3️⃣ voice_channel_id - Ses Kanalı ID'si

**Nedir?** Botların 24/7 bağlı kalacağı ses kanalı

**Otomatik ayarlanır mı?** Evet, `.setup` ile

**Elle ayarlamak isterseniz:** [VOICE_CHANNEL_SETUP.md](VOICE_CHANNEL_SETUP.md) oku

---

## 🟡 İSTEĞE BAĞLI AYARLAR (Tavsiye)

### log_channel_id - Günlük Kanalı

**Nedir?** Tüm sunucu olaylarının kaydedileceği kanal

**Ayarlanmazsa?** Günlük yazılmaz ama bot çalışmaya devam eder

**Ayarlama:**
```json
"log_channel_id": 222333444
```

---

### max_warnings - Uyarı Limiti

**Nedir?** Kaç uyarıdan sonra kullanıcı kicklenir?

**Varsayılan:** 3

**Değiştirme:**
```json
"max_warnings": 5
```

---

## 🟢 GÜVENLİK ÖZELLIKLERI

Açıp kapatabilirsiniz (true/false):

```json
"security_features": {
    "anti_spam": true,      → Spam koruması
    "anti_raid": true,      → Raid koruması
    "auto_role": true,      → Yeni üyelere rol atar
    "server_lock": false    → Sunucu kilidi
}
```

**Açmak:** `true`
**Kapatmak:** `false`

---

## 📋 Tam Örnek

```json
{
    "owner_id": 123456789,                    ← KENDİ ID'NİZ
    "guild_id": 555666777,                    ← SUNUCU ID'SİNİZ
    "voice_channel_id": 888999111,            ← SES KANALI ID'SİNİZ
    "log_channel_id": 222333444,              ← GÜNLÜK KANALI ID'SİNİZ (İsteğe bağlı)
    "bot1_id": null,                          ← OTOMATIK DOLACAK
    "bot2_id": null,                          ← OTOMATIK DOLACAK
    "moderation_enabled": true,
    "max_warnings": 3,
    "security_features": {
        "anti_spam": true,
        "anti_raid": true,
        "auto_role": true,
        "server_lock": false
    },
    "protected_roles": [],
    "protected_users": [],
    "last_setup": null,
    "version": "1.0.0"
}
```

---

## ✅ Kurulum Checklistesi

### BAŞLAMADAN ÖNCEKİ AYARLAR (Zorunlu)

- [ ] `owner_id` ayarlandı mı? (Kendi ID'niz)
- [ ] `guild_id` ayarlandı mı? (Sunucu ID'si)
- [ ] `voice_channel_id` ayarlandı mı? (Ses kanalı ID'si)

### ÖNERİLEN AYARLAR (Tavsiye)

- [ ] `log_channel_id` ayarlandı mı?
- [ ] `max_warnings` kontrol edildi mi?
- [ ] Güvenlik özellikleri açık mı?

---

## 🔧 HATIRLANAN HATA ÇÖZÜMLERI

### "owner_id ayarlanmamış" Hatası

```json
❌ HATA:
"owner_id": null

✅ ÇÖZÜM:
"owner_id": 123456789    ← Kendi ID'niz yazıyorsun
```

### JSON Syntax Hatası

```json
❌ HATA (virgül eksik):
"owner_id": 123456789
"guild_id": 555666777

✅ ÇÖZÜM (virgül eklendi):
"owner_id": 123456789,
"guild_id": 555666777,
```

### Değer null olmuş

```json
❌ HATA:
"voice_channel_id": null

✅ ÇÖZÜM:
.setup komutunu çalıştırıyorsun VEYA
elle ID'yi yazıyorsun:
"voice_channel_id": 888999111
```

---

## 📖 Dosyayı Düzenleme

### Visual Studio Code'da:

1. Dosyayı aç: `bot_config.json`
2. Değer değiştir
3. Kaydet: `Ctrl+S`
4. Botu yeniden başlat

### Notepad'de:

1. Dosyaya sağ tıkla
2. "Open with" → Notepad
3. Düzenle
4. Kaydet: `Ctrl+S`
5. Botu yeniden başlat

### Hata Ayıklama:

1. Dosyayı kaydettiniz mi?
2. JSON format doğru mu? (virgüller, parantezler)
3. Botu yeniden başlattınız mı?

---

## 🎯 İD'leri Adım Adım Bulma

### Owner ID (Kendi ID'niz):

1. Discord açıyorsun
2. Profil fotoğrafına tıklayıyorsun (sol alt)
3. "Copy User ID" seç
4. bot_config.json'da yapıştırıyorsun

### Guild ID (Sunucu):

1. Sunucuya sağ tıklayıyorsun
2. "Copy Server ID" seç
3. bot_config.json'da yapıştırıyorsun

### Voice Channel ID (Ses Kanalı):

1. Developer Mode aç
2. Ses kanalına sağ tıklayıyorsun
3. "Copy Channel ID" seç
4. bot_config.json'da yapıştırıyorsun

---

## ✨ Tamamlandı!

Artık başlayabilirsiniz:

```bash
python main_bot1.py
python main_bot2.py
```

Discord'da: `.status` ile kontrol et ✅

---

**Soru varsa:** [SETUP_GUIDE.md](SETUP_GUIDE.md) oku veya [INDEX.md](INDEX.md) görünüşü kontrol et.
