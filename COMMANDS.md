# 📚 Guard Bot Komut Referansi

## 🔷 Setup & Yönetim Komutları

### `.setup`
Guard Bot sistemini kur ve yapılandır.

**Kullanım:**
```
.setup
```

**Gerekli:** Bot sahip ID'si
**Yapar:**
- Sunucu ID'si kaydedilir
- Ses kanalı seçilir
- Günlük kanalı seçilir
- `bot_config.json` oluşturulur

**Örnek:**
```
.setup
> Lütfen ses kanalını ping edin: #genel-ses
> Lütfen günlük kanalını ping edin: #logs
✅ Kurulum tamamlandı!
```

---

### `.status`
Sistem durumunu kontrol et.

**Kullanım:**
```
.status
```

**Gösterir:**
- Konfigürasyon durumu
- Güvenlik ayarları
- Korunan roller ve kullanıcılar
- Sunucu kilidi durumu

**Çıktı örneği:**
```
📊 Guard Bot Sistem Durumu
⚙️ Konfigürasyon
  Sunucu: 123456789
  Ses Kanalı: 987654321
🔒 Güvenlik Ayarları
  Anti-Spam: ✅
  Sunucu Kilidi: ❌ KAPATIK
```

---

### `.check_bot`
Bot durumunu kontrol et (Bot 1 ve 2).

**Kullanım:**
```
.check_bot
```

**Gösterir:**
- Bot 1 durumu
- Bot 2 durumu
- Bot ID'leri
- Yedek durum

**Çıktı örneği:**
```
🤖 Guard Bot Durumu
Bot 1 (Bu Bot): 🟢 Çevrimiçi
Bot ID: 123456789

Bot 2: 🟢 Çevrimiçi
Bot ID: 987654321
```

---

## ⚠️ Moderasyon Komutları

### `.warn @kullanıcı [sebep]`
Kullanıcıyı uyar.

**Kullanım:**
```
.warn @John spam
.warn @Jane reklam yapıyor
.warn @Baran
```

**Parameterler:**
- `@kullanıcı`: (Zorunlu) Uyarılacak kişi
- `[sebep]`: (İsteğe bağlı) Uyarı sebebi

**Davranış:**
- Her uyarı sayılır
- Max uyarı sınırına ulaşıysa (varsayılan 3) kullanıcı kicklenir
- Günlük kanalına yazılır

**Gerekli:** Admin yetkisi

---

### `.purge [sayı]`
Son N mesajı sil.

**Kullanım:**
```
.purge
.purge 10
.purge 50
```

**Parameterler:**
- `[sayı]`: (İsteğe bağlı, varsayılan: 10) Silinecek mesaj sayısı

**Sınırlar:**
- Maksimum 100 mesaj
- Yalnız kendi kanalından siler
- 14 günden eski mesajları silemez (Discord sınırı)

**Gerekli:** Admin yetkisi

**Örnek:**
```
.purge 20
✅ Temizleme Tamamlandı
20 mesaj silindi
```

---

### `.kick @kullanıcı [sebep]`
Kullanıcıyı kickle.

**Kullanım:**
```
.kick @User
.kick @Spam_Bot bot tarafında sorun
```

**Parameterler:**
- `@kullanıcı`: (Zorunlu) Kicklenecek kişi
- `[sebep]`: (İsteğe bağlı) Kick sebebi

**Notlar:**
- Kullanıcı geri katılabilir
- Audit log'a yazılır

**Gerekli:** Kick Members izni

---

### `.ban @kullanıcı [sebep]`
Kullanıcıyı banlama.

**Kullanım:**
```
.ban @Troll spam ve taciz
.ban @Raider_1
```

**Parameterler:**
- `@kullanıcı`: (Zorunlu) Banlanacak kişi
- `[sebep]`: (İsteğe bağlı) Ban sebebi

**Notlar:**
- Kalıcı işlem
- Unban için Discord sunucu ayarlarında yapılmalı
- Audit log'a yazılır

**Gerekli:** Ban Members izni

---

## 🔒 Güvenlik Komutları

### `.lock_server`
Sunucuyu kilitle (yalnızca yöneticiler mesaj gönderebilir).

**Kullanım:**
```
.lock_server
```

**Gerekli:** Bot sahip ID'si
**Yapar:**
- @everyone rolü kısıtlanır
- Yalnızca admin/mod mesaj atabilir
- Üyeler izleyebilir ama yazamaz

**Kullanım Durumları:**
- Raid saldırısı
- Spam atılması
- Sunucu bakımı

---

### `.unlock_server`
Sunucuyu kilidi aç.

**Kullanım:**
```
.unlock_server
```

**Gerekli:** Bot sahip ID'si
**Yapar:**
- @everyone rolü normal duruma döner
- Herkes mesaj gönderebilir

---

### `.set_protection <özellik> <on/off>`
Güvenlik özelliğini aç/kapat.

**Kullanım:**
```
.set_protection anti_spam on
.set_protection anti_raid off
.set_protection auto_role true
.set_protection server_lock false
```

**Özellikler:**
- `anti_spam`: Spam koruması
- `anti_raid`: Raid koruması  
- `auto_role`: Yeni üyelere rol atar
- `server_lock`: Sunucu kilidi durumu

**Değerler:**
- Açma: `on`, `true`, `evet`, `1`, `aç`
- Kapatma: `off`, `false`, `hayır`, `0`, `kapat`

**Gerekli:** Bot sahip ID'si

---

## 👥 Analiz Komutları

### `.risk_check @kullanıcı`
Kullanıcı risk seviyesini kontrol et.

**Kullanım:**
```
.risk_check @Suspicious_User
.risk_check @John
```

**Parameterler:**
- `@kullanıcı`: (Zorunlu) Kontrol edilecek kişi

**Risk Seviyeleri:**
- 🟢 DÜŞÜK: Güvenilir (Skor: 0)
- 🟡 ORTA: İzlemek gerekli (Skor: 1-2)
- 🟠 YÜKSEK: Uyarısı var (Skor: 3-4)
- 🔴 ÇOOK YÜKSEK: Tehditkar (Skor: 5+)

**Çıktı örneği:**
```
🚩 Kullanıcı Risk Analizi
Kullanıcı: @Spam_User
Risk Seviyesi: 🔴 ÇOOK YÜKSEK
Bayrak Sayısı: 5
Önerilen İşlem: BAN

Sebepler:
- Spam atma
- Reklam yapma
```

**Gerekli:** Bot sahip ID'si

---

### `.reputation [@kullanıcı]`
İtibar durumunu göster.

**Kullanım:**
```
.reputation
.reputation @John
```

**Parameterler:**
- `[@kullanıcı]`: (İsteğe bağlı) Başkasının itibarı (varsayılan: kendiniz)

**Durumlar:**
- ⭐ Özel Üye: +10 ve üzeri
- 😊 Saygıdeğer: +5 ila +9
- 😐 Normal: 0 ila +4
- 😠 Şüpheli: -1 ila -5
- 🚫 Kötü: -5 ve altı

---

## 🆘 Yardım Komutları

### `.help`
Tüm komutları listele.

**Kullanım:**
```
.help
```

**Gösterir:**
- Tüm mevcut komutlar
- Kısa açıklamalar

---

### `.help <komut>`
Belirli komut hakkında bilgi.

**Kullanım:**
```
.help warn
.help lock_server
```

**Gösterir:**
- Komut açıklaması
- Parametreler
- Örnek kullanım

---

## 🎯 Komut Kısayolları

| Kısa | Tam | Açıklama |
|------|-----|----------|
| `.h` | `.help` | Yardım |
| `.p` | `.purge` | Mesaj sil |
| `.w` | `.warn` | Uyar |
| `.k` | `.kick` | Kickle |
| `.b` | `.ban` | Banlama |

---

## ⚡ Hızlı İpuçları

### İzin Hataları
```
❌ "Missing Permissions"
→ Admin yetkisine sahip misiniz?
→ Bot yeterli izne sahip mi?
```

### Komut Çalışmıyor
```
❌ "CommandNotFound"
→ Komut adını doğru yazdınız mı?
→ Prefix doğru mu? (varsayılan: .)
```

### Kanalı Ping Edemedin
```
❌ "Channel not found"
→ #kanal-adı kullan
→ veya: <#CHANNEL_ID>
```

---

## 📊 Komut Grupları

### Yönetim (Tümü)
- `.setup` - Kurulum
- `.status` - Durum
- `.check_bot` - Bot durumu

### Moderasyon (Admin)
- `.warn` - Uyar
- `.kick` - Kickle
- `.ban` - Banlama
- `.purge` - Temizle

### Güvenlik (Bot Sahip)
- `.lock_server` - Kilitle
- `.unlock_server` - Kilidi Aç
- `.set_protection` - Özellik Ayarla

### Analiz (Bot Sahip)
- `.risk_check` - Risk Kontrol
- `.reputation` - İtibar

---

## 🔔 Notlar

- Tüm komutlar `discord.py` tarafından desteklenir
- Yetkisiz kullanım: Otomatik olarak reddedilir
- Tüm işlemler audit log'a yazılır
- Hata alıyorsanız, terminal çıktısını kontrol edin

---

**Son Güncelleme:** 2026-07-27
**Versiyon:** 1.0.0
