# 🎙️ Ses Kanalı Ayarlama Rehberi

Botların hangi ses kanalında bağlı kalacağını ayarlamak için 3 yöntem var:

---

## 🔷 YÖNTEMİ 1: .setup Komutu (Tavsiye ✅)

En kolay yöntem. Discord'da sunucunuzda şu komutu çalıştırıyorsun:

```
.setup
```

Adımları takip et:
1. Owner ID kontrol edilir
2. Ses kanalını ping et (örn: `#genel-ses`)
3. Sistem otomatik kaydeder ✅

**Avantajı:** Tamamen otomatik, hata riski yok

**Gerekli:** Sunucuda en az 1 ses kanalı olmalı

---

## 🔷 YÖNTEMİ 2: bot_config.json Elle Düzenleme

Manuel olarak ses kanalı ID'sini yazarsın.

### Adım 1: Ses Kanalı ID'sini Bul

**Discord'da:**
1. Developer Mode'u aç (User Settings → Advanced → Developer Mode ✓)
2. Ses kanalına sağ tıkla
3. "Copy Channel ID" seç
4. ID kopyalanır (örn: `123456789`)

### Adım 2: bot_config.json Dosyasını Aç

Dosya konumu:
```
c:\Users\Çolak\Desktop\Aşk Botlar\bot_config.json
```

### Adım 3: voice_channel_id Ayarla

**Hali:** 
```json
"voice_channel_id": null
```

**Değiştirilecek:**
```json
"voice_channel_id": 123456789
```

**Örnek tam görünüş:**
```json
{
    "owner_id": 987654321,
    "guild_id": 555666777,
    "voice_channel_id": 123456789,    ← BU SATIRI AYARLA
    "log_channel_id": 111222333
}
```

### Adım 4: Dosyayı Kaydet

- Ctrl+S (Visual Studio Code'da)
- Notepad'de: File → Save

### Adım 5: Botları Yeniden Başlat

Terminal'de:
```bash
# Bot 1'i kapat (Ctrl+C)
# Bot 2'yi kapat (Ctrl+C)

# Yeniden başlat
python main_bot1.py
python main_bot2.py
```

✅ Botlar ses kanalına bağlanmalı!

---

## 🔷 YÖNTEMİ 3: .env Dosyasından (İleri)

`.env` dosyasına doğrudan yazabilirsin.

### bot_config.json Düzenleme (Alternatif)

Elle `bot_config.json` düzenlemek yerine, şu format da kullanabilir:

```json
{
    "voice_channel_ids": [
        {
            "guild_id": 555666777,
            "channel_id": 123456789
        }
    ]
}
```

---

## ✅ Hangisini Kullanmalı?

| Yöntem | Zorluğu | Hız | Tavsiye |
|--------|---------|-----|---------|
| .setup | Çok Kolay | Hızlı | ✅ Tavsiye |
| bot_config.json | Kolay | Orta | ✓ Güvenilir |
| .env | Zor | Hızlı | Sadece biliyorsan |

---

## 🎯 Ses Kanalı ID'sini Bulma (Detaylı)

### Discord'da:

1. **Developer Mode'u Aç**
   - User Settings açıyorsun (sol alt dişli)
   - "Advanced" bölümüne git
   - "Developer Mode" aç ✓

2. **Kanalı Bul**
   - Soldaki kanal listesine bak
   - Ses kanalı (🔊 simgesi) seç

3. **ID'yi Kopyala**
   - Ses kanalına sağ tıkla
   - "Copy Channel ID" seç
   - ID otomatik kopyalanır

4. **Yapıştır**
   - bot_config.json dosyasında yapıştırıyorsun

---

## 🔍 Örnek

### Discord Sunucun Böyle Ise:

```
Aşk Sunucusu
├── 📢 Duyurular
├── 💬 genel
├── 🎙️  genel-ses        ← Bu kanalı seçeceksin
├── 🎙️  müzik
└── 🎙️  stream
```

### bot_config.json Şöyle Olur:

```json
{
    "owner_id": 123456789,
    "guild_id": 555666777,
    "voice_channel_id": 888999111,     ← genel-ses kanalının ID'si
    "log_channel_id": 222333444
}
```

---

## ⚠️ Hata Çözümü

### "Ses kanalı bulunamadı"

```
❌ Çözüm: 
1. ID'yi doğru kopyaladın mı?
2. Ses kanalı ID'sini mi yazıyorsun (text kanalı değil)?
3. Kanal sunucuda var mı?
```

### "null" hatası

```
❌ Çözüm:
1. voice_channel_id null mı?
2. Dosyayı kaydettiniz mi? (Ctrl+S)
3. Botu yeniden başlattınız mı?
```

### Bot ses kanalına bağlanmıyor

```
❌ Çözüm:
1. Bot'a "Connect" izni var mı?
2. Bot Yönetici rolüne sahip mi?
3. Sunucu sahibi misiniz?
4. .check_bot ile durumu kontrol et
```

---

## 📝 Hızlı Checklist

- [ ] Developer Mode açtınız mı?
- [ ] Ses kanalı ID'sini kopyaladınız mı?
- [ ] bot_config.json'da `null` yerine ID yazıyorsunuz?
- [ ] Dosyayı kaydettiniz mi?
- [ ] Botları yeniden başlattınız mı?
- [ ] Botlar ses kanalında görünüyor mu?
- [ ] `.check_bot` komutu çalışıyor mu?

---

## 🎉 Başarılı!

Botlar şimdi belirlediğiniz ses kanalında 24/7 koruma sağlayacak! 🛡️

**Ek:** İstediğiniz zaman `.setup` komutunu tekrar çalıştırarak kanalı değiştirebilirsiniz.
