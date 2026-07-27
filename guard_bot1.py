import discord
from discord.ext import commands, tasks
import logging
import os
from dotenv import load_dotenv
from shared_utils import (
    ConfigManager, StatusManager, SecurityManager,
    is_owner, has_admin_perms, get_embed,
    modern_embed, success_embed, error_embed, warning_embed, info_embed,
    COLORS
)
from datetime import datetime, timedelta, timezone
import asyncio
import subprocess

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class GuardBot1(commands.Cog):
    """Guard Bot 1 - Sunucu Koruma Sistemi"""

    def __init__(self, bot):
        self.bot = bot
        self.config = ConfigManager.load_config()
        self.warns = {}
        self.spam_tracker = {}
        self.start_time = datetime.now()
        self.voice_connected = False  # Tek seferlik bağlantı bayrağı

        self.heart_beat.start()
        self.check_other_bot.start()
        logger.info("✅ Guard Bot 1 yüklendi")

    def cog_unload(self):
        self.heart_beat.cancel()
        self.check_other_bot.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"🟢 Guard Bot 1 çevrimiçi: {self.bot.user}")
        StatusManager.save_status(self.bot.user.id, "online")
        # Tek seferlik ses bağlantısı
        if not self.voice_connected:
            await self.connect_to_voice_channel()

    async def connect_to_voice_channel(self):
        """Ses kanalına tek seferde bağlan ve bağlı kal. Loop yok."""
        if self.voice_connected:
            return

        try:
            guild_id = self.config.get("guild_id")
            voice_channel_id = self.config.get("voice_channel_id")

            if not voice_channel_id or not guild_id:
                logger.warning("⚠️  Ses kanalı veya sunucu ID'si belirtilmemiş - ses bağlantısı atlandı")
                return

            guild = self.bot.get_guild(guild_id)
            if not guild:
                logger.error(f"❌ Sunucu bulunamadı: {guild_id}")
                return

            channel = guild.get_channel(voice_channel_id)
            if not channel:
                logger.error(f"❌ Ses kanalı bulunamadı: {voice_channel_id}")
                return

            if not isinstance(channel, discord.VoiceChannel):
                logger.error(f"❌ {channel.name} bir ses kanalı değil")
                return

            if guild.voice_client and guild.voice_client.is_connected():
                logger.info(f"ℹ️  Bot zaten {guild.voice_client.channel.name} kanalında")
                self.voice_connected = True
                return

            bot_perms = channel.permissions_for(guild.me)
            if not bot_perms.connect:
                logger.error(f"❌ '{channel.name}' kanalına bağlanma izni yok")
                return
            if not bot_perms.speak:
                logger.warning(f"⚠️  '{channel.name}' kanalında konuşma izni yok")

            voice_client = await channel.connect(timeout=10.0)
            self.voice_connected = True
            logger.info(f"✅ 🎙️  {channel.name} kanalına bağlandı (tek seferlik, bağlı kalacak)")

        except discord.ClientException as e:
            logger.error(f"❌ Discord bağlantı hatası: {str(e)[:150]}")
        except asyncio.TimeoutError:
            logger.error("❌ Bağlantı zaman aşımı")
        except Exception as e:
            logger.error(f"❌ Ses kanalına bağlanırken hata: {type(e).__name__}: {str(e)[:150]}")

    @tasks.loop(seconds=60)
    async def heart_beat(self):
        try:
            StatusManager.save_status(self.bot.user.id, "online", datetime.now().isoformat())
            logger.debug("💓 Kalp atışı gönderildi")
        except Exception as e:
            logger.error(f"❌ Kalp atışı hatası: {e}")

    @tasks.loop(seconds=30)
    async def check_other_bot(self):
        try:
            other_bot_id = self.config.get("bot2_id")
            if not other_bot_id:
                return
            other_status = StatusManager.get_bot_status(other_bot_id)
            if not other_status or not other_status.get("online"):
                logger.warning("⚠️  Guard Bot 2 offline, Bot 1 korumaya devam ediyor")
            else:
                logger.debug("✅ Guard Bot 2 aktif")
        except Exception as e:
            logger.error(f"❌ Durum kontrolü hatası: {e}")

    # ==================== GÜVENLİK OLAYLARI ====================

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            logger.info(f"📥 Yeni üye: {member} ({member.id})")
            if self.config["security_features"]["auto_role"]:
                await self.assign_member_role(member)
            await self.log_security_event(member.guild, "member_join", f"{member} sunucuya katıldı")
        except Exception as e:
            logger.error(f"❌ Üye katılış hatası: {e}")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        try:
            logger.info(f"📤 Üye ayrıldı: {member}")
            await self.log_security_event(member.guild, "member_remove", f"{member} sunucudan ayrıldı")
        except Exception as e:
            logger.error(f"❌ Üye ayrılış hatası: {e}")

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        try:
            await self.log_security_event(
                message.guild, "message_delete",
                f"Kullanıcı: {message.author}\nİçerik: {message.content[:100]}"
            )
        except Exception as e:
            logger.error(f"❌ Mesaj silme hatası: {e}")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        try:
            if before.roles != after.roles:
                added = set(after.roles) - set(before.roles)
                removed = set(before.roles) - set(after.roles)
                if added or removed:
                    logger.debug(f"👤 {after} için rol değişimi tespit edildi")
        except Exception as e:
            logger.error(f"❌ Üye güncelleme hatası: {e}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Bot kendisi kanaldan atılırsa SADECE bir kez yeniden bağlan
        if member.id == self.bot.user.id and after.channel is None and before.channel is not None:
            logger.warning(f"⚠️  Bot {before.channel.name} kanalından ayrıldı. Tek seferlik yeniden bağlanma...")
            self.voice_connected = False
            await asyncio.sleep(5)
            await self.connect_to_voice_channel()

    # ==================== KOMUTLAR ====================

    @commands.command(name="check_bot")
    async def check_bot(self, ctx):
        if not is_owner(ctx.author.id, self.config.get("owner_id")):
            await ctx.send(embed=error_embed("Yetkisiz", "Bu komutu kullanma izniniz yok"))
            return
        try:
            fields = [{"name": "Bot 1 (Bu Bot)", "value": f"🟢 Çevrimiçi\n**ID:** {self.bot.user.id}", "inline": False}]
            other_bot_id = self.config.get("bot2_id")
            if other_bot_id:
                other_status = StatusManager.get_bot_status(other_bot_id)
                status_text = "🟢 Çevrimiçi" if other_status and other_status.get("online") else "🔴 Çevrimdışı"
                fields.append({"name": "Bot 2", "value": f"{status_text}\n**ID:** {other_bot_id}", "inline": False})
            await ctx.send(embed=modern_embed(
                title="🤖 Guard Bot Durumu",
                description="Sistemdeki botların anlık durumu",
                color=COLORS["info"],
                fields=fields
            ))
        except Exception as e:
            await ctx.send(embed=error_embed("Hata", str(e)))

    @commands.command(name="warn")
    async def warn_user(self, ctx, member: discord.Member, *, reason="Sebep belirtilmedi"):
        if not has_admin_perms(ctx.author):
            await ctx.send(embed=error_embed("Yetkisiz", "Bu komutu kullanma izniniz yok"))
            return
        if member.bot:
            await ctx.send(embed=error_embed("Geçersiz", "Botlar uyarılamaz"))
            return
        try:
            user_id = member.id
            if user_id not in self.warns:
                self.warns[user_id] = 0
            self.warns[user_id] += 1
            warn_count = self.warns[user_id]
            max_w = self.config['max_warnings']
            await ctx.send(embed=warning_embed(
                "Kullanıcı Uyarıldı",
                f"**Kullanıcı:** {member.mention}\n**Sebep:** {reason}\n**Uyarı:** {warn_count}/{max_w}"
            ))
            if warn_count >= max_w:
                try:
                    await member.kick(reason=f"Uyarı limiti aşıldı: {reason}")
                    await ctx.send(embed=modern_embed(
                        title="🚫 Kullanıcı Kicklendi",
                        description=f"{member} uyarı limitini aştı ({warn_count}/{max_w})",
                        color=COLORS["error"]
                    ))
                except Exception:
                    await ctx.send(embed=error_embed("İşlem Başarısız", f"{member} kicklenemedi"))
            await self.log_security_event(ctx.guild, "user_warn", f"{member} - {reason}")
        except Exception as e:
            await ctx.send(embed=error_embed("Hata", str(e)))

    @commands.command(name="lock_server")
    async def lock_server(self, ctx):
        if not is_owner(ctx.author.id, self.config.get("owner_id")):
            await ctx.send(embed=error_embed("Yetkisiz", "Bu komutu kullanma izniniz yok"))
            return
        try:
            for role in ctx.guild.roles:
                if role.name == "@everyone":
                    await role.edit(send_messages=False)
            self.config["security_features"]["server_lock"] = True
            ConfigManager.save_config(self.config)
            await ctx.send(embed=success_embed("Sunucu Kilitlendi", "Yalnızca yöneticiler mesaj gönderebilir"))
        except Exception as e:
            await ctx.send(embed=error_embed("Hata", str(e)))

    @commands.command(name="unlock_server")
    async def unlock_server(self, ctx):
        if not is_owner(ctx.author.id, self.config.get("owner_id")):
            await ctx.send(embed=error_embed("Yetkisiz", "Bu komutu kullanma izniniz yok"))
            return
        try:
            for role in ctx.guild.roles:
                if role.name == "@everyone":
                    await role.edit(send_messages=True)
            self.config["security_features"]["server_lock"] = False
            ConfigManager.save_config(self.config)
            await ctx.send(embed=success_embed("Sunucu Kilidi Açıldı", "Herkes mesaj gönderebilir"))
        except Exception as e:
            await ctx.send(embed=error_embed("Hata", str(e)))

    @commands.command(name="purge")
    async def purge(self, ctx, amount: int = 10):
        if not has_admin_perms(ctx.author):
            await ctx.send(embed=error_embed("Yetkisiz", "Bu komutu kullanma izniniz yok"))
            return
        if amount < 1 or amount > 100:
            await ctx.send(embed=warning_embed("Geçersiz Sayı", "1-100 arası bir değer girin"))
            return
        try:
            deleted = await ctx.channel.purge(limit=amount)
            await ctx.send(embed=success_embed("Temizleme Tamamlandı", f"{len(deleted)} mesaj silindi"), delete_after=5)
        except Exception as e:
            await ctx.send(embed=error_embed("Hata", str(e)))

    @commands.command(name="ping")
    async def ping(self, ctx):
        """Bot gecikmesini göster"""
        latency = round(self.bot.latency * 1000)
        if latency < 100:
            status = "🟢 Mükemmel"
            color = COLORS["success"]
        elif latency < 200:
            status = "🟡 İyi"
            color = COLORS["warning"]
        else:
            status = "🔴 Yüksek"
            color = COLORS["error"]
        await ctx.send(embed=modern_embed(
            title="🏓 Pong!",
            description=f"**Gecikme:** {latency}ms\n**Durum:** {status}",
            color=color,
            footer="Guard Bot • Latency"
        ))

    @commands.command(name="uptime")
    async def uptime(self, ctx):
        """Bot çalışma süresini göster"""
        delta = datetime.now() - self.start_time
        days = delta.days
        hours, rem = divmod(int(delta.total_seconds()), 3600)
        hours = hours % 24
        minutes, _ = divmod(rem, 60)
        await ctx.send(embed=info_embed(
            "⏱️ Çalışma Süresi",
            f"Bot **{days}** gün, **{hours}** saat, **{minutes}** dakikadır çalışıyor"
        ))

    @commands.command(name="serverinfo")
    async def serverinfo(self, ctx):
        """Sunucu bilgilerini göster"""
        guild = ctx.guild
        created_at = guild.created_at.strftime("%d.%m.%Y %H:%M")
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        roles = len(guild.roles)
        fields = [
            {"name": "📋 Genel", "value": f"**Sunucu ID:** {guild.id}\n**Oluşturulma:** {created_at}\n**Bölge:** {guild.preferred_locale}", "inline": False},
            {"name": "👥 Üyeler", "value": f"**Toplam:** {guild.member_count}\n**Sahip:** {guild.owner.mention if guild.owner else 'Bilinmiyor'}", "inline": True},
            {"name": "📢 Kanallar", "value": f"**Metin:** {text_channels}\n**Ses:** {voice_channels}", "inline": True},
            {"name": "🎭 Roller", "value": f"**Toplam:** {roles}", "inline": True},
        ]
        await ctx.send(embed=modern_embed(
            title=f"ℹ️ {guild.name}",
            description="Sunucu bilgileri",
            color=COLORS["info"],
            thumbnail=str(guild.icon.url) if guild.icon else None,
            fields=fields
        ))

    @commands.command(name="userinfo")
    async def userinfo(self, ctx, member: discord.Member = None):
        """Kullanıcı bilgilerini göster"""
        member = member or ctx.author
        created = member.created_at.strftime("%d.%m.%Y")
        joined = member.joined_at.strftime("%d.%m.%Y") if member.joined_at else "Bilinmiyor"
        roles = [r.mention for r in member.roles if r.name != "@everyone"]
        roles_text = ", ".join(roles[:10]) if roles else "Rol yok"
        if len(roles) > 10:
            roles_text += f" (+{len(roles)-10} daha)"
        fields = [
            {"name": "👤 Kullanıcı", "value": f"**Ad:** {member.name}\n**ID:** {member.id}\n**Bot:** {'Evet' if member.bot else 'Hayır'}", "inline": False},
            {"name": "📅 Tarihler", "value": f"**Hesap:** {created}\n**Katılım:** {joined}", "inline": False},
            {"name": "🎭 Roller", "value": roles_text, "inline": False},
        ]
        await ctx.send(embed=modern_embed(
            title=f"ℹ️ {member.display_name}",
            description="Kullanıcı bilgileri",
            color=COLORS["info"],
            thumbnail=str(member.display_avatar.url),
            fields=fields
        ))

    @commands.command(name="mute")
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, reason="Sebep belirtilmedi"):
        """Kullanıcıyı sustur (timeout 10 dakika)"""
        if member.bot:
            await ctx.send(embed=error_embed("Geçersiz", "Botlar susturulamaz"))
            return
        try:
            until = datetime.now(timezone.utc) + timedelta(minutes=10)
            await member.timeout(until, reason=reason)
            await ctx.send(embed=success_embed("Kullanıcı Susturuldu", f"{member.mention} 10 dakika susturuldu\n**Sebep:** {reason}"))
            await self.log_security_event(ctx.guild, "user_mute", f"{member} susturuldu: {reason}")
        except Exception as e:
            await ctx.send(embed=error_embed("Hata", str(e)))

    @commands.command(name="unmute")
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        """Kullanıcının susturmasını kaldır"""
        try:
            await member.timeout(None, reason=f"{ctx.author} tarafından susturması kaldırıldı")
            await ctx.send(embed=success_embed("Susturma Kaldırıldı", f"{member.mention} artık konuşabilir"))
        except Exception as e:
            await ctx.send(embed=error_embed("Hata", str(e)))

    @commands.command(name="slowmode")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int = 0):
        """Kanal için yavaş mod ayarla (saniye)"""
        if seconds < 0 or seconds > 21600:
            await ctx.send(embed=warning_embed("Geçersiz", "0-21600 saniye arası girin"))
            return
        try:
            await ctx.channel.edit(slowmode_delay=seconds)
            if seconds == 0:
                await ctx.send(embed=success_embed("Yavaş Mod Kapatıldı", "Bu kanalda yavaş mod devre dışı"))
            else:
                await ctx.send(embed=success_embed("Yavaş Mod Ayarlandı", f"Bu kanalda yavaş mod: **{seconds}** saniye"))
        except Exception as e:
            await ctx.send(embed=error_embed("Hata", str(e)))

    @commands.command(name="avatar")
    async def avatar(self, ctx, member: discord.Member = None):
        """Kullanıcı avatarını göster"""
        member = member or ctx.author
        await ctx.send(embed=modern_embed(
            title=f"🖼️ {member.display_name} Avatarı",
            color=COLORS["accent"],
            image=str(member.display_avatar.url)
        ))

    @commands.command(name="botinfo")
    async def botinfo(self, ctx):
        """Bot hakkında bilgi"""
        delta = datetime.now() - self.start_time
        uptime_str = f"{delta.days}g {delta.seconds//3600}s {(delta.seconds%3600)//60}d"
        fields = [
            {"name": "🤖 Bot", "value": f"**Ad:** {self.bot.user.name}\n**ID:** {self.bot.user.id}", "inline": True},
            {"name": "⏱️ Çalışma", "value": uptime_str, "inline": True},
            {"name": "📡 Gecikme", "value": f"{round(self.bot.latency*1000)}ms", "inline": True},
            {"name": "🛡️ Sürüm", "value": "Guard Bot v1.0.0", "inline": False},
        ]
        await ctx.send(embed=modern_embed(
            title="🤖 Guard Bot Bilgisi",
            description="Gelişmiş sunucu koruma sistemi",
            color=COLORS["primary"],
            thumbnail=str(self.bot.user.display_avatar.url),
            fields=fields
        ))

    # ==================== YARDIMCI ====================

    async def assign_member_role(self, member: discord.Member):
        try:
            for role in member.guild.roles:
                if role.name.lower() in ["üye", "member", "users"]:
                    await member.add_roles(role)
                    break
        except Exception as e:
            logger.error(f"❌ Rol atama hatası: {e}")

    async def log_security_event(self, guild: discord.Guild, event_type: str, details: str):
        try:
            SecurityManager.log_event(guild.id, event_type, details)
            if self.config.get("log_channel_id"):
                log_channel = guild.get_channel(self.config["log_channel_id"])
                if log_channel:
                    await log_channel.send(embed=modern_embed(
                        title=f"📝 {event_type.upper()}",
                        description=details,
                        color=COLORS["neutral"],
                        footer="Guard Bot • Günlük"
                    ))
        except Exception as e:
            logger.error(f"Günlük yazma hatası: {e}")


def setup(bot):
    bot.add_cog(GuardBot1(bot))
