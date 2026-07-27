import discord
from discord.ext import commands, tasks
import logging
import os
from dotenv import load_dotenv
from shared_utils import ConfigManager, StatusManager, SecurityManager, is_owner, has_admin_perms, get_embed
from datetime import datetime
import asyncio
import subprocess

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class GuardBot2(commands.Cog):
    """Guard Bot 2 - Yedek Koruma Sistemi"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = ConfigManager.load_config()
        self.active_voice_connections = {}
        self.warns = {}
        self.spam_tracker = {}
        self.voice_connect_attempts = {}  # Retry sayısını takip et
        self.last_connection_attempt = {}  # Son bağlantı zamanı takip et
        self.connection_cooldown = 30  # 30 saniye bekleme
        
        # FFmpeg kontrolü
        if not self._check_ffmpeg():
            logger.warning("⚠️  FFmpeg bulunamadı! Ses bağlantısı çalışmayacak.")
        
        self.heart_beat.start()
        self.check_other_bot.start()
        self.voice_reconnect_monitor.start()  # Bağlantı izleyicisi
        logger.info("✅ Guard Bot 2 yüklendi")
    
    def _check_ffmpeg(self):
        """FFmpeg kurulu olup olmadığını kontrol et"""
        try:
            result = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def cog_unload(self):
        self.heart_beat.cancel()
        self.check_other_bot.cancel()
        self.voice_reconnect_monitor.cancel()
    
    @commands.Cog.listener()
    @commands.Cog.listener()
    async def on_ready(self):
        """Bot hazır olduğunda"""
        logger.info(f"🟢 Guard Bot 2 çevrimiçi: {self.bot.user}")
        
        # Bot2 ID'sini config'e kaydet
        config = ConfigManager.load_config()
        config["bot2_id"] = self.bot.user.id
        ConfigManager.save_config(config)
        
        # Durumu kaydet
        StatusManager.save_status(self.bot.user.id, "online")
        
        # Ses kanalına bağlan
        await self.connect_to_voice_channel()
    
    async def connect_to_voice_channel(self):
        """Ses kanalına bağlan"""
        try:
            guild_id = self.config.get("guild_id")
            voice_channel_id = self.config.get("voice_channel_id")
            
            if not voice_channel_id:
                logger.warning("⚠️  Ses kanalı belirtilmemiş")
                return
            
            if not guild_id:
                logger.warning("⚠️  Sunucu ID'si belirtilmemiş")
                return
            
            # Sunucu bulma
            guild = self.bot.get_guild(guild_id)
            if not guild:
                logger.error(f"❌ Sunucu bulunamadı: {guild_id}")
                return
            
            # Kanal bulma
            channel = guild.get_channel(voice_channel_id)
            if not channel:
                logger.error(f"❌ Ses kanalı bulunamadı: {voice_channel_id}")
                return
            
            # Kanal tipi kontrol
            if not isinstance(channel, discord.VoiceChannel):
                logger.error(f"❌ {channel.name} bir ses kanalı değil (Tip: {type(channel).__name__})")
                return
            
            # Zaten bağlı mı?
            if guild.voice_client and guild.voice_client.is_connected():
                logger.info(f"ℹ️  Bot zaten {guild.voice_client.channel.name}'nda")
                self.active_voice_connections[guild.id] = guild.voice_client
                return
            
            # Bot'un izinleri var mı?
            bot_perms = channel.permissions_for(guild.me)
            if not bot_perms.connect:
                logger.error(f"❌ Bot'un '{channel.name}' kanalına bağlanma izni yok")
                return
            if not bot_perms.speak:
                logger.warning(f"⚠️  Bot'un '{channel.name}' kanalında konuşma izni yok")
            
            # Bağlan
            voice_client = await channel.connect()
            self.active_voice_connections[guild.id] = voice_client
            self.voice_connect_attempts[guild_id] = 0  # Reset retry counter
            logger.info(f"✅ 🎙️  {channel.name} kanalına başarıyla bağlandı")
            
        except discord.ClientException as e:
            logger.error(f"❌ Discord istemci hatası: {e}")
            # 5 saniye sonra tekrar dene
            await asyncio.sleep(5)
            attempts = self.voice_connect_attempts.get(guild_id, 0)
            if attempts < 3:
                self.voice_connect_attempts[guild_id] = attempts + 1
                logger.info(f"🔄 Yeniden bağlanmaya çalışılıyor... ({attempts + 1}/3)")
                await self.connect_to_voice_channel()
        except asyncio.TimeoutError:
            logger.error("❌ Bağlantı zaman aşımı (timeout)")
        except Exception as e:
            logger.error(f"❌ Ses kanalına bağlanırken hata: {type(e).__name__}: {e}")
    
    @tasks.loop(seconds=60)
    async def heart_beat(self):
        """Düzenli kalp atışı (durum kontrolü)"""
        try:
            StatusManager.save_status(self.bot.user.id, "online", datetime.now().isoformat())
            logger.debug("💓 Kalp atışı gönderildi")
        except Exception as e:
            logger.error(f"❌ Kalp atışı hatası: {e}")
    
    @tasks.loop(seconds=20)
    async def voice_reconnect_monitor(self):
        """Ses bağlantısı monitoring ve otomatik yeniden bağlanma"""
        try:
            guild_id = self.config.get("guild_id")
            if not guild_id:
                return
            
            # Bağlantı kopmuş mu kontrol et
            if guild_id in self.active_voice_connections:
                voice_client = self.active_voice_connections[guild_id]
                if voice_client and not voice_client.is_connected():
                    logger.warning(f"⚠️  Ses bağlantısı koptu! Yeniden bağlanıyor...")
                    del self.active_voice_connections[guild_id]
                    await self.connect_to_voice_channel()
            else:
                # Bağlı değilse tekrar bağla
                guild = self.bot.get_guild(guild_id)
                if guild and not guild.voice_client:
                    logger.info("🔄 Ses kanalına bağlı değil, bağlanmaya çalışılıyor...")
                    await self.connect_to_voice_channel()
        except Exception as e:
            logger.error(f"❌ Voice monitor hatası: {e}")
    
    @tasks.loop(seconds=30)
    async def check_other_bot(self):
        """Diğer botun durumunu kontrol et"""
        try:
            other_bot_id = self.config.get("bot1_id")
            if not other_bot_id:
                return
            
            other_status = StatusManager.get_bot_status(other_bot_id)
            
            if not other_status or not other_status.get("online"):
                logger.warning(f"⚠️  Guard Bot 1 offline durumda, Bot 2 korumaya devam ediyor")
            else:
                logger.info("✅ Guard Bot 1 aktif")
                
        except Exception as e:
            logger.error(f"❌ Durum kontrolü hatası: {e}")
    
    # ==================== GÜVENLIK OLAYLARI ====================
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Üye katıldığında"""
        try:
            logger.info(f"📥 Yeni üye: {member} ({member.id})")
            
            # Korumaya ekle
            if self.config["security_features"]["auto_role"]:
                await self.assign_member_role(member)
            
            # Günlüğe yazma
            await self.log_security_event(
                member.guild,
                "member_join",
                f"{member} sunucuya katıldı"
            )
            
        except Exception as e:
            logger.error(f"❌ Üye katılış olayı hatası: {e}")
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Üye ayrıldığında"""
        try:
            logger.info(f"📤 Üye ayrıldı: {member}")
            await self.log_security_event(
                member.guild,
                "member_remove",
                f"{member} sunucudan ayrıldı"
            )
        except Exception as e:
            logger.error(f"❌ Üye ayrılış olayı hatası: {e}")
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Mesaj düzenlendiğinde"""
        if before.author.bot:
            return
        
        try:
            if before.content != after.content:
                logger.debug(f"✏️  {before.author} mesajını düzenledi")
        except Exception as e:
            logger.error(f"❌ Mesaj düzenleme hatası: {e}")
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Mesaj silindiğinde"""
        if message.author.bot:
            return
        
        try:
            logger.debug(f"🗑️  {message.author} tarafından mesaj silindi")
            await self.log_security_event(
                message.guild,
                "message_delete",
                f"Kullanıcı: {message.author}\nİçerik: {message.content[:100]}"
            )
        except Exception as e:
            logger.error(f"❌ Mesaj silme hatası: {e}")
    
    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        """Sunucu ayarları değiştiğinde"""
        logger.info(f"⚙️  Sunucu ayarları güncellendi")
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Üye bilgileri güncellendiğinde"""
        try:
            # Rol değişimi kontrolü
            if before.roles != after.roles:
                added_roles = set(after.roles) - set(before.roles)
                removed_roles = set(before.roles) - set(after.roles)
                
                if added_roles or removed_roles:
                    logger.debug(f"👤 {after} için rol değişimi tespit edildi")
                    
        except Exception as e:
            logger.error(f"❌ Üye güncelleme hatası: {e}")
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Ses durumu değiştiğinde (kanal değişimi, mic/deafen)"""
        try:
            # Bot kendi seseşinin kapanırsa veya kanaldan ayrılırsa
            if member.id == self.bot.user.id:
                if after.channel is None and before.channel is not None:
                    # Bot kanaldan ayrıldı
                    logger.warning(f"⚠️  Bot {before.channel.name}'dan ayrıldı. Yeniden bağlanıyor...")
                    guild_id = self.config.get("guild_id")
                    if guild_id in self.active_voice_connections:
                        del self.active_voice_connections[guild_id]
                    await asyncio.sleep(5)
                    await self.connect_to_voice_channel()
                    
        except Exception as e:
            logger.error(f"❌ Ses durumu güncelleme hatası: {e}")
    
    # ==================== KOMUTLAR ====================
    
    @commands.command(name="check_bot")
    async def check_bot(self, ctx):
        """Bot durumunu kontrol et"""
        if not is_owner(ctx.author.id, self.config.get("owner_id")):
            await ctx.send("❌ Bu komutu kullanma izniniz yok")
            return
        
        try:
            embed = get_embed(
                "🤖 Guard Bot Durumu",
                f"**Bot 2 (Bu Bot):** 🟢 Çevrimiçi\n**Bot ID:** {self.bot.user.id}"
            )
            
            other_bot_id = self.config.get("bot1_id")
            if other_bot_id:
                other_status = StatusManager.get_bot_status(other_bot_id)
                status_text = "🟢 Çevrimiçi" if other_status and other_status.get("online") else "🔴 Çevrimdışı"
                embed.add_field(
                    name="Bot 1",
                    value=f"{status_text}\n**Bot ID:** {other_bot_id}",
                    inline=False
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Hata: {e}")
            logger.error(f"Hata: {e}")
    
    @commands.command(name="warn")
    async def warn_user(self, ctx, member: discord.Member, *, reason="Sebep belirtilmedi"):
        """Kullanıcıyı uyar"""
        if not has_admin_perms(ctx.author):
            await ctx.send("❌ Bu komutu kullanma izniniz yok")
            return
        
        if member.bot:
            await ctx.send("❌ Botlar uyarılamaz")
            return
        
        try:
            user_id = member.id
            if user_id not in self.warns:
                self.warns[user_id] = 0
            
            self.warns[user_id] += 1
            warn_count = self.warns[user_id]
            
            embed = get_embed(
                "⚠️  Kullanıcı Uyarıldı",
                f"**Kullanıcı:** {member.mention}\n**Sebep:** {reason}\n**Uyarı Sayısı:** {warn_count}/{self.config['max_warnings']}"
            )
            await ctx.send(embed=embed)
            
            # Maksimum uyarı aşıldıysa
            if warn_count >= self.config['max_warnings']:
                try:
                    await member.kick(reason=f"Uyarı limitini aşan: {reason}")
                    await ctx.send(f"🚫 {member} kicklendi (Uyarı limiti aşıldı)")
                except:
                    await ctx.send(f"❌ {member} kicklenemedi")
            
            await self.log_security_event(ctx.guild, "user_warn", f"{member} - {reason}")
            
        except Exception as e:
            await ctx.send(f"❌ Hata: {e}")
            logger.error(f"Hata: {e}")
    
    @commands.command(name="lock_server")
    async def lock_server(self, ctx):
        """Sunucuyu kilitle (güvenlik özelliği)"""
        if not is_owner(ctx.author.id, self.config.get("owner_id")):
            await ctx.send("❌ Bu komutu kullanma izniniz yok")
            return
        
        try:
            for role in ctx.guild.roles:
                if role.name == "@everyone":
                    await role.edit(send_messages=False)
            
            self.config["security_features"]["server_lock"] = True
            ConfigManager.save_config(self.config)
            
            embed = get_embed(
                "🔒 Sunucu Kilitlendi",
                "Yalnızca yöneticiler mesaj gönderebilir"
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Hata: {e}")
    
    @commands.command(name="unlock_server")
    async def unlock_server(self, ctx):
        """Sunucuyu kilidi aç"""
        if not is_owner(ctx.author.id, self.config.get("owner_id")):
            await ctx.send("❌ Bu komutu kullanma izniniz yok")
            return
        
        try:
            for role in ctx.guild.roles:
                if role.name == "@everyone":
                    await role.edit(send_messages=True)
            
            self.config["security_features"]["server_lock"] = False
            ConfigManager.save_config(self.config)
            
            embed = get_embed(
                "🔓 Sunucu Kilidi Açıldı",
                "Herkes mesaj gönderebilir"
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Hata: {e}")
    
    @commands.command(name="purge")
    async def purge(self, ctx, amount: int = 10):
        """Mesajları sil"""
        if not has_admin_perms(ctx.author):
            await ctx.send("❌ Bu komutu kullanma izniniz yok")
            return
        
        try:
            deleted = await ctx.channel.purge(limit=amount)
            embed = get_embed(
                "🧹 Temizleme Tamamlandı",
                f"{len(deleted)} mesaj silindi"
            )
            await ctx.send(embed=embed, delete_after=5)
            
        except Exception as e:
            await ctx.send(f"❌ Hata: {e}")
    
    # ==================== YARDIMCI FONKSİYONLAR ====================
    
    async def assign_member_role(self, member: discord.Member):
        """Yeni üyeye rol ata"""
        try:
            # Genel üyeler için role ata
            for role in member.guild.roles:
                if role.name.lower() in ["üye", "member", "users"]:
                    await member.add_roles(role)
                    break
        except Exception as e:
            logger.error(f"❌ Rol atama hatası: {e}")
    
    async def log_security_event(self, guild: discord.Guild, event_type: str, details: str):
        """Güvenlik olayını günlüğe yaz"""
        try:
            SecurityManager.log_event(guild.id, event_type, details)
            
            # Log kanalına gönder
            if self.config.get("log_channel_id"):
                log_channel = guild.get_channel(self.config["log_channel_id"])
                if log_channel:
                    embed = get_embed(
                        f"📝 {event_type.upper()}",
                        details
                    )
                    await log_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Günlük yazma hatası: {e}")


# Bot Kurulumu
def setup(bot):
    """Cog'u yükle"""
    bot.add_cog(GuardBot2(bot))
