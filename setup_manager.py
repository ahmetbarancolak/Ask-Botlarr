import discord
from discord.ext import commands
import logging
import asyncio
from datetime import datetime
from shared_utils import (
    ConfigManager, StatusManager, Database, is_owner,
    modern_embed, success_embed, error_embed, warning_embed, info_embed,
    COLORS
)

logger = logging.getLogger(__name__)


class SetupManager(commands.Cog):
    """Kurulum yöneticisi - modern .setup komutu"""

    def __init__(self, bot):
        self.bot = bot
        self.config = ConfigManager.load_config()

    @commands.command(name="setup")
    async def setup(self, ctx):
        """Guard Bot Sistemi kurulumu - adım adım modern arayüz"""
        owner_id = self.config.get("owner_id")

        if owner_id is None:
            await ctx.send(embed=error_embed(
                "Bot Sahip ID'si Ayarlanmamış",
                "**Çözüm (2 dakika):**\n"
                "1️⃣ `bot_config.json` dosyasını aç\n"
                "2️⃣ `\"owner_id\": null` satırını bul\n"
                f"3️⃣ Şu şekilde değiştir: `\"owner_id\": {ctx.author.id},`\n"
                "4️⃣ Dosyayı kaydet (Ctrl+S)\n"
                "5️⃣ Botu yeniden başlat\n"
                "6️⃣ `.setup` komutunu tekrar çalıştır"
            ))
            return

        if ctx.author.id != owner_id:
            await ctx.send(embed=error_embed(
                "Yetkisiz Erişim",
                f"Bu komutu yalnızca bot sahibi (<@{owner_id}>) kullanabilir"
            ))
            return

        # Veritabanına bağlan
        db_ok = await Database.connect()
        db_status = "✅ Bağlı" if db_ok else "❌ Bağlantı yok (dosya tabanlı yedek aktif)"

        await ctx.send(embed=modern_embed(
            title="⚙️ Guard Bot Kurulumu",
            description=(
                "🛡️ **Gelişmiş Sunucu Koruma Sistemine Hoş Geldiniz**\n\n"
                "Bu sihirbaz, sisteminizi adım adım yapılandırır:\n"
                "• 🏠 Sunucu kaydı\n"
                "• 🎙️ Ses kanalı seçimi\n"
                "• 📝 Günlük kanalı seçimi\n"
                "• 🔒 Güvenlik ayarları\n\n"
                f"**Veritabanı:** {db_status}\n\n"
                "**⏱️ Her adımda 60 saniyeniz var.**\n"
                "**💡 İptal etmek için `iptal` yazın.**"
            ),
            color=COLORS["primary"],
            author_name="Guard Bot Kurulum Sihirbazı",
            thumbnail=str(self.bot.user.display_avatar.url),
            footer="Guard Bot • Kurulum Sihirbazı"
        ))
        await asyncio.sleep(1)

        # Adım 1: Sunucu kaydı
        guild_id = ctx.guild.id
        self.config["guild_id"] = guild_id
        await ctx.send(embed=success_embed(
            "Adım 1/4 — Sunucu Kaydedildi",
            f"**Sunucu:** {ctx.guild.name}\n**ID:** `{guild_id}`\n**Üye Sayısı:** {ctx.guild.member_count}"
        ))
        await asyncio.sleep(1)

        # Adım 2: Ses kanalı
        await ctx.send(embed=info_embed(
            "Adım 2/4 — 🎙️ Ses Kanalı Seçimi",
            "Botun **24/7 bağlı kalacağı** ses kanalını belirtin:\n\n"
                "**Seçenek A:** Kanalı ping et → `#kanal-adı`\n"
                "**Seçenek B:** Kanal adını yaz → `genel-ses`\n\n"
                "⏰ 60 saniye içinde cevaplayın • İptal için `iptal`"
        ))

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            voice_msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            if voice_msg.content.lower() == "iptal":
                await ctx.send(embed=warning_embed("Kurulum İptal Edildi", "Ses kanalı seçimi yapılmadı"))
                return

            voice_channel = None
            if voice_msg.channel_mentions:
                voice_channel = voice_msg.channel_mentions[0]
            else:
                for channel in ctx.guild.voice_channels:
                    if channel.name.lower() == voice_msg.content.lower():
                        voice_channel = channel
                        break

            if not voice_channel or not isinstance(voice_channel, discord.VoiceChannel):
                await ctx.send(embed=error_embed(
                    "Ses Kanalı Bulunamadı",
                    "Geçerli bir ses kanalı ping edin veya adını yazın.\n"
                    "Kurulumu yeniden başlatmak için `.setup` yazın."
                ))
                return

            self.config["voice_channel_id"] = voice_channel.id
            await ctx.send(embed=success_embed(
                "Ses Kanalı Kaydedildi",
                f"**Kanal:** {voice_channel.mention}\n**ID:** `{voice_channel.id}`\n\n"
                "✅ Bot bu kanala bağlanacak ve koruma sağlayacak"
            ))
        except asyncio.TimeoutError:
            await ctx.send(embed=error_embed("Zaman Aşımı", "60 saniye içinde cevap verilmedi. Kurulum iptal edildi."))
            return

        await asyncio.sleep(1)

        # Adım 3: Günlük kanalı
        await ctx.send(embed=info_embed(
            "Adım 3/4 — 📝 Günlük Kanalı Seçimi",
            "Tüm güvenlik olaylarının kaydedileceği **günlük kanalını** belirtin:\n\n"
                "**Seçenek A:** Kanalı ping et → `#logs`\n"
                "**Seçenek B:** Kanal adını yaz → `logs`\n\n"
                "⏰ 60 saniye • İsteğe bağlı, atlamak için `atla` • İptal için `iptal`"
        ))

        try:
            log_msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            content = log_msg.content.lower()
            if content == "iptal":
                await ctx.send(embed=warning_embed("Kurulum İptal Edildi", "İşlem durduruldu"))
                return
            if content == "atla":
                await ctx.send(embed=warning_embed("Günlük Kanalı Atlandı", "Günlük kaydı devre dışı. Daha sonra ayarlayabilirsiniz."))
            else:
                log_channel = None
                if log_msg.channel_mentions:
                    log_channel = log_msg.channel_mentions[0]
                else:
                    for channel in ctx.guild.text_channels:
                        if channel.name.lower() == content:
                            log_channel = channel
                            break
                if log_channel:
                    self.config["log_channel_id"] = log_channel.id
                    await ctx.send(embed=success_embed(
                        "Günlük Kanalı Kaydedildi",
                        f"**Kanal:** {log_channel.mention}\n**ID:** `{log_channel.id}`"
                    ))
                else:
                    await ctx.send(embed=warning_embed(
                        "Kanal Bulunamadı",
                        "Günlük kanalı ayarlanmadı. Devam ediliyor..."
                    ))
        except asyncio.TimeoutError:
            await ctx.send(embed=warning_embed("Zaman Aşımı", "Günlük kanalı atlandı"))

        await asyncio.sleep(1)

        # Adım 4: Güvenlik ayarları özeti
        sec = self.config["security_features"]
        sec_fields = [
            {"name": "Anti-Spam", "value": "✅ Açık" if sec.get("anti_spam") else "❌ Kapalı", "inline": True},
            {"name": "Anti-Raid", "value": "✅ Açık" if sec.get("anti_raid") else "❌ Kapalı", "inline": True},
            {"name": "Otomatik Rol", "value": "✅ Açık" if sec.get("auto_role") else "❌ Kapalı", "inline": True},
            {"name": "Sunucu Kilidi", "value": "🔒 Açık" if sec.get("server_lock") else "🔓 Kapalı", "inline": True},
            {"name": "Max Uyarı", "value": f"**{self.config.get('max_warnings', 3)}** uyarı → kick", "inline": True},
            {"name": "Moderasyon", "value": "✅ Aktif" if self.config.get("moderation_enabled") else "❌ Devre dışı", "inline": True},
        ]
        await ctx.send(embed=modern_embed(
            title="Adım 4/4 — 🔒 Güvenlik Ayarları",
            description="Mevcut güvenlik yapılandırması. `.set_protection` ile değiştirebilirsiniz.",
            color=COLORS["accent"],
            fields=sec_fields,
            footer="Guard Bot • Güvenlik Özeti"
        ))

        # Kaydet - hem dosyaya hem veritabanına
        self.config["owner_id"] = owner_id
        self.config["last_setup"] = datetime.now().isoformat()
        ConfigManager.save_config(self.config)
        if Database.is_connected():
            await Database.save_guild_config(guild_id, self.config)
        self.config = ConfigManager.load_config()

        await asyncio.sleep(1)

        # Final özet
        final_fields = [
            {"name": "🏠 Sunucu", "value": f"**{ctx.guild.name}**\n`{guild_id}`", "inline": True},
            {"name": "🎙️ Ses", "value": f"<#{self.config.get('voice_channel_id')}>" if self.config.get("voice_channel_id") else "Ayarlanmadı", "inline": True},
            {"name": "📝 Günlük", "value": f"<#{self.config.get('log_channel_id')}>" if self.config.get("log_channel_id") else "Ayarlanmadı", "inline": True},
            {"name": "🤖 Bot 1", "value": f"`{self.config.get('bot1_id', 'Bekleniyor')}`", "inline": True},
            {"name": "🤖 Bot 2", "value": f"`{self.config.get('bot2_id', 'Bekleniyor')}`", "inline": True},
            {"name": "👤 Sahip", "value": f"<@{owner_id}>", "inline": True},
            {"name": "💾 Veritabanı", "value": db_status, "inline": False},
        ]
        await ctx.send(embed=modern_embed(
            title="✅ Kurulum Tamamlandı",
            description=(
                "🛡️ **Guard Bot Sistemi başarıyla yapılandırıldı!**\n\n"
                "**Sonraki Adımlar:**\n"
                "1️⃣ Bot 1 ve Bot 2 token'larını `.env` dosyasına ekleyin\n"
                "2️⃣ `python main_bot1.py` ve `python main_bot2.py` çalıştırın\n"
                "3️⃣ `.status` ile durumu kontrol edin\n\n"
                "**Hızlı Komutlar:**\n"
                "`.help` • `.status` • `.check_bot` • `.ping`"
            ),
            color=COLORS["success"],
            thumbnail=str(ctx.guild.icon.url) if ctx.guild.icon else None,
            fields=final_fields,
            footer="Guard Bot • Kurulum Tamamlandı"
        ))

    @commands.command(name="status")
    async def status_cmd(self, ctx):
        """Sistem durumunu modern embed ile göster"""
        try:
            sec = self.config["security_features"]
            db_status = "✅ Bağlı" if Database.is_connected() else "❌ Bağlantı yok"
            fields = [
                {"name": "⚙️ Konfigürasyon", "value": (
                    f"**Sunucu:** `{self.config.get('guild_id', 'Ayarlanmadı')}`\n"
                    f"**Ses Kanalı:** `{self.config.get('voice_channel_id', 'Ayarlanmadı')}`\n"
                    f"**Günlük Kanalı:** `{self.config.get('log_channel_id', 'Ayarlanmadı')}`"
                ), "inline": False},
                {"name": "🔒 Güvenlik", "value": (
                    f"Anti-Spam: {'✅' if sec['anti_spam'] else '❌'}\n"
                    f"Anti-Raid: {'✅' if sec['anti_raid'] else '❌'}\n"
                    f"Otomatik Rol: {'✅' if sec['auto_role'] else '❌'}\n"
                    f"Sunucu Kilidi: {'🔒 Açık' if sec['server_lock'] else '🔓 Kapalı'}"
                ), "inline": True},
                {"name": "👥 Koruma", "value": (
                    f"Max Uyarı: **{self.config.get('max_warnings', 3)}**\n"
                    f"Korunan Roller: **{len(self.config.get('protected_roles', []))}**\n"
                    f"Korunan Kullanıcılar: **{len(self.config.get('protected_users', []))}**"
                ), "inline": True},
                {"name": "💾 Veritabanı", "value": db_status, "inline": False},
            ]

            bot1_id = self.config.get("bot1_id")
            bot2_id = self.config.get("bot2_id")
            bot_lines = []
            if bot1_id:
                s = StatusManager.get_bot_status(bot1_id)
                bot_lines.append(f"Bot 1: {'🟢 Çevrimiçi' if s and s.get('online') else '🔴 Çevrimdışı'}")
            if bot2_id:
                s = StatusManager.get_bot_status(bot2_id)
                bot_lines.append(f"Bot 2: {'🟢 Çevrimiçi' if s and s.get('online') else '🔴 Çevrimdışı'}")
            if bot_lines:
                fields.append({"name": "🤖 Bot Durumu", "value": "\n".join(bot_lines), "inline": False})

            await ctx.send(embed=modern_embed(
                title="📊 Guard Bot Sistem Durumu",
                description="Sistemin anlık durumu ve yapılandırması",
                color=COLORS["primary"],
                fields=fields,
                footer="Guard Bot • Durum Raporu"
            ))
        except Exception as e:
            await ctx.send(embed=error_embed("Hata", str(e)))

    @commands.command(name="set_protection")
    async def set_protection(self, ctx, feature: str, state: str):
        """Güvenlik özelliğini aç/kapat"""
        if not is_owner(ctx.author.id, self.config.get("owner_id")):
            await ctx.send(embed=error_embed("Yetkisiz", "Bu komutu kullanma izniniz yok"))
            return
        try:
            state_bool = state.lower() in ['true', 'on', 'evet', '1', 'aç']
            if feature.lower() in self.config["security_features"]:
                self.config["security_features"][feature.lower()] = state_bool
                ConfigManager.save_config(self.config)
                if Database.is_connected():
                    await Database.save_guild_config(self.config.get("guild_id", ctx.guild.id), self.config)
                await ctx.send(embed=success_embed(
                    "Ayar Güncellendi",
                    f"**{feature}**: {'✅ Açık' if state_bool else '❌ Kapalı'}"
                ))
            else:
                valid = ", ".join(self.config["security_features"].keys())
                await ctx.send(embed=error_embed("Bilinmeyen Özellik", f"Geçerli özellikler: {valid}"))
        except Exception as e:
            await ctx.send(embed=error_embed("Hata", str(e)))

    @commands.command(name="help")
    async def help_cmd(self, ctx, category: str = None):
        """Modern yardım menüsü"""
        categories = {
            "yönetim": {
                "title": "⚙️ Yönetim Komutları",
                "cmds": [
                    ("`.setup`", "Sistem kurulumu (sihirbaz)"),
                    ("`.status`", "Sistem durumunu göster"),
                    ("`.check_bot`", "Bot durumunu kontrol et"),
                    ("`.set_protection <özellik> <on/off>`", "Güvenlik özelliğini aç/kapat"),
                ]
            },
            "moderasyon": {
                "title": "⚠️ Moderasyon Komutları",
                "cmds": [
                    ("`.warn @kullanıcı [sebep]`", "Kullanıcıyı uyar (veritabanına kaydeder)"),
                    ("`.warns [@kullanıcı]`", "Kullanıcının uyarı geçmişini göster"),
                    ("`.clearwarns @kullanıcı`", "Kullanıcının uyarılarını temizle"),
                    ("`.purge [sayı]`", "Son N mesajı sil (max 100)"),
                    ("`.mute @kullanıcı [sebep]`", "10 dakika sustur"),
                    ("`.unmute @kullanıcı`", "Susturmayı kaldır"),
                    ("`.slowmode [saniye]`", "Kanal yavaş modu"),
                ]
            },
            "güvenlik": {
                "title": "🔒 Güvenlik Komutları",
                "cmds": [
                    ("`.lock_server`", "Sunucuyu kilitle"),
                    ("`.unlock_server`", "Sunucu kilidini aç"),
                    ("`.addword <kelime>`", "Yasaklı kelime ekle"),
                    ("`.delword <kelime>`", "Yasaklı kelime sil"),
                    ("`.wordlist`", "Yasaklı kelimeleri listele"),
                    ("`.protect_role @rol`", "Rolü korumaya al"),
                    ("`.unprotect_role @rol`", "Rolü korumadan çıkar"),
                    ("`.logs [sayı]`", "Son güvenlik kayıtları (veritabanı)"),
                ]
            },
            "bilgi": {
                "title": "ℹ️ Bilgi Komutları",
                "cmds": [
                    ("`.ping`", "Bot gecikmesi"),
                    ("`.uptime`", "Çalışma süresi"),
                    ("`.serverinfo`", "Sunucu bilgileri"),
                    ("`.userinfo [@kullanıcı]`", "Kullanıcı bilgileri"),
                    ("`.botinfo`", "Bot bilgileri"),
                    ("`.avatar [@kullanıcı]`", "Avatarı göster"),
                ]
            }
        }

        if category:
            cat_key = category.lower().replace(" ", "")
            if cat_key in categories:
                cat = categories[cat_key]
                fields = [{"name": cmd, "value": desc, "inline": False} for cmd, desc in cat["cmds"]]
                await ctx.send(embed=modern_embed(
                    title=cat["title"],
                    description=f"{len(cat['cmds'])} komut",
                    color=COLORS["info"],
                    fields=fields,
                    footer="Guard Bot • Yardım"
                ))
            else:
                await ctx.send(embed=error_embed(
                    "Kategori Bulunamadı",
                    "Kategoriler: `yönetim`, `moderasyon`, `güvenlik`, `bilgi`"
                ))
            return

        all_cmds = []
        for cat in categories.values():
            all_cmds.extend(cat["cmds"])

        overview_fields = [
            {"name": "⚙️ Yönetim", "value": "`.setup` `.status` `.check_bot` `.set_protection`", "inline": False},
            {"name": "⚠️ Moderasyon", "value": "`.warn` `.warns` `.clearwarns` `.purge` `.mute` `.unmute` `.slowmode`", "inline": False},
            {"name": "🔒 Güvenlik", "value": "`.lock_server` `.unlock_server` `.addword` `.delword` `.wordlist` `.protect_role` `.unprotect_role` `.logs`", "inline": False},
            {"name": "ℹ️ Bilgi", "value": "`.ping` `.uptime` `.serverinfo` `.userinfo` `.botinfo` `.avatar`", "inline": False},
            {"name": "📚 Detaylı Yardım", "value": "`.help <kategori>` ile kategori detayları\nÖrn: `.help moderasyon`", "inline": False},
        ]
        await ctx.send(embed=modern_embed(
            title="🛡️ Guard Bot Yardım Menüsü",
            description=(
                f"**{len(all_cmds)}** komut mevcut • Prefix: `.`\n\n"
                "Bir kategorinin detayları için `.help <kategori>` yazın"
            ),
            color=COLORS["primary"],
            author_name="Guard Bot Sistemi",
            thumbnail=str(self.bot.user.display_avatar.url),
            fields=overview_fields,
            footer="Guard Bot • Yardım Menüsü"
        ))


def setup(bot):
    bot.add_cog(SetupManager(bot))
