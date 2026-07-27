# ✅ BAŞLATMA ÖNCESİ KONTROL LİSTESİ

Guard Bot Sistemi'ni başlatmadan önce bu adımları takip et.

---

## 🔴 ADIM 1: AYARLAR (5 dakika) - ZORUNLU

### bot_config.json Dosyasını Aç

**Windows'ta Açma:**

1. `c:\Users\Çolak\Desktop\Aşk Botlar` klasörüne git
2. `bot_config.json` dosyasına sağ tıkla
3. "Open with" → "Visual Studio Code" VEYA "Notepad"

**Visual Studio Code'da Açma (Tavsiye):**
- `Ctrl+K Ctrl+O`
- `bot_config.json` seç

---

## 🟠 ADIM 2: SAHIP ID'SİNİ AYARLA

### Kendinize Sağ Tıklayıp ID Kopyala

1. Discord'da kendinize sağ tıklayıyorsun
2. "Copy User ID" seç (eğer Developer Mode açık ise)
3. ID numaranız kopyalanır (örn: `123456789`)

### bot_config.json'da Yapıştır

**Aç:**
```json
"owner_id": null,
```

**Değişdir:**
```json
"owner_id": 123456789,    ← Kendi ID'nizi yazıyorsun (SİKUAN BOŞ BIRAKMA!)
```

---

## 🟡 ADIM 3: SUNUCU ID'SİNİ AYARLA (İsteğe Bağlı)

**Otomatik ayarlanır mı?** Evet, `.setup` ile otomatik yazar

**Elle yapan yaparsın:**

1. Sunucuya sağ tıkla
2. "Copy Server ID" seç
3. bot_config.json'da: `"guild_id": 555666777`

---

## 🟢 ADIM 4: TOKEN'LARI KONTROL ET

### .env Dosyası

```env
BOT1_TOKEN=MTUzMTMyNTc3NDg5MDY2Mzk4Ng.Gx12S5...   ← Token var mı?
BOT2_TOKEN=MTUzMTMyNzA5NTI1NzY5ODQ2Ng.GA1X5P...   ← Token var mı?
```

- [ ] BOT1_TOKEN dolu mu?
- [ ] BOT2_TOKEN dolu mu?
- [ ] Token'lar gerçek mi? (fake yazı değil mi?)

---

## 🔵 ADIM 5: DOSYALARI KAYDET

Visual Studio Code'da:
```
Ctrl+S
```

Notepad'de:
```
File → Save
```

✅ Dosya kaydedildi!

---

## ⚫ ADIM 6: BOTLARI BAŞLAT

### Terminal 1 (Bot 1):
```bash
python main_bot1.py
```

### Terminal 2 (Bot 2):
```bash
python main_bot2.py
```

**Ne olmalı?**
```
✅ 🟢 Guard Bot 1 çevrimiçi: YourBot#1234
✅ 🟢 Guard Bot 2 çevrimiçi: YourBot2#5678
✅ 🎙️ Ses kanalına bağlanıyor...
✅ 💓 Kalp atışı gönderildi
```

---

## 🟣 ADIM 7: Discord'da TEST ET

### Setup Komutunu Çalıştır

Discord'da sunucunuzda:
```
.setup
```

**Ne olmalı?**
```
⚙️  GUARD BOT KURULUM BAŞLATILDI
✅ Sunucu Kaydedildi
🎙️  SES KANALI SEÇIMI
```

---

## KONTROL LİSTESİ

### Başlamadan Önce:
- [ ] Discord account'unuz var mı?
- [ ] Guard Bot'u 2 tane sunucuya eklediniz mi?
- [ ] Python 3.8+ yüklü mü? (`python --version`)
- [ ] Kütüphaneleri yüklediniz mi? (`pip install -r requirements.txt`)

### Ayarları Kontrol Ettiniz mi?
- [ ] `owner_id` ayarlandı mı?
- [ ] `guild_id` ayarlandı mı? (veya .setup ile ayarlanacak)
- [ ] `voice_channel_id` ayarlandı mı? (veya .setup ile ayarlanacak)
- [ ] `log_channel_id` ayarlandı mı? (İsteğe bağlı)
- [ ] Tüm dosyalar kaydedildi mi?

### Botlar Çalışıyor mu?
- [ ] Terminal 1: Bot 1 başladı mı?
- [ ] Terminal 2: Bot 2 başladı mı?
- [ ] Discord'da 2 bot görünüyor mu?
- [ ] Botlar online mi?

### Setup Tamamlandı mı?
- [ ] `.setup` komutu çalıştı mı?
- [ ] Ses kanalı seçildi mi?
- [ ] Günlük kanalı seçildi mi? (İsteğe bağlı)
- [ ] Hiç hata var mı?

### Son Kontrol:
- [ ] `.status` komutu çalışıyor mu?
- [ ] `.check_bot` komutu iki botu da gösteriyor mu?
- [ ] Botlar ses kanalında görünüyor mu?

---

## 🆘 HATA ÇÖZÜMLERI

### "owner_id ayarlanmamış" Hatası

```
Çözüm:
1. bot_config.json aç
2. "owner_id": null   →   "owner_id": 123456789
3. Kaydet (Ctrl+S)
4. Botları yeniden başlat
```

### "Bot token tanımlanmamış" Hatası

```
Çözüm:
1. .env aç
2. BOT1_TOKEN ve BOT2_TOKEN'a gerçek token'ları yazıyorsun
3. Kaydet
4. Botları yeniden başlat
```

### "Ses kanalı bulunamadı" Hatası

```
Çözüm:
1. bot_config.json'da voice_channel_id kontrol et
2. Doğru kanal ID'si mi?
3. Ses kanalı sunucuda var mı?
4. .setup komutunu tekrar çalıştır
```

### Bot Bağlanmıyor

```
Çözüm:
1. Token doğru mu?
2. Bot sunucuda ekli mi?
3. Bot yetkili mi?
4. İnternet bağlantısı var mı?
5. Discord server status kontrol et
```

---

## 📞 DESTEK

- **bot_config.json ayarları:** [CONFIG_GUIDE.md](CONFIG_GUIDE.md)
- **Ses kanalı setup:** [VOICE_CHANNEL_SETUP.md](VOICE_CHANNEL_SETUP.md)
- **Tüm rehberler:** [INDEX.md](INDEX.md)
- **Komutlar:** [COMMANDS.md](COMMANDS.md)

---

## 🎯 Sonuç

Tüm adımlar tamamlandı mı?

**Evet** ✅ → `.setup` komutunu çalıştır ve sistemi kur

**Hayır** ❌ → Lütfen hangi adımda takıldığını söyle

---

**Başarılar!** 🚀
