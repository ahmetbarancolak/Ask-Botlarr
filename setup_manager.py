import discord
from discord.ext import commands
import logging
import asyncio
from shared_utils import ConfigManager, is_owner, get_embed

logger = logging.getLogger(__name__)

class SetupManager(commands.Cog):
    """Kurulum yöneticisi - .setup komutu"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = ConfigManager.load_config()
    
    @commands.command(name="setup")
    async def setup(self, ctx):
        """Guard Bot Sistemi Kurulumu"""
        # Sadece bot sahipbilgisine
        owner_id = self.config.get("owner_id")
        
        if owner_id is None:
            await ctx.send(
                "❌ **HATA:** Bot sahip ID'si ayarlanmamış!\\n\\n" +
                "**Çözüm (5 dakika):**\\n" +
                "1. `bot_config.json` dosyasını aç\\n" +
                "2. Şu satırı bul: `\\\"owner_id\\\": null`\\n" +
                f"3. Şöyle değiştir: `\\\"owner_id\\\": {ctx.author.id},`\\n" +
                "4. Dosyayı kaydet (Ctrl+S)\\n" +
                "5. Botu yeniden başlat\\n" +
                "6. `.setup` komutunu tekrar çalıştırıyorsun"
            )
            return
        
        if ctx.author.id != owner_id:
            await ctx.send(f"❌ Sadece bot sahip (<@{owner_id}>) bu komutu kullanabilir")
            return
        
        try:
            # Kurulum başladı
            embed = get_embed(
                "⚙️  GUARD BOT KURULUM BAŞLATILDI",
                "Lütfen adımları takip edin...\n\n" +
                "Bu kurulum süreci aşağıdaki bilgileri soracaktır:\n" +
                "• Sunucu ID'si\n" +
                "• Ses Kanalı\n" +
                "• Günlük Kanalı\n" +
                "• Bot Token'ları"
            )
            await ctx.send(embed=embed)
            
            # Sunucu ID
            guild_id = ctx.guild.id
            self.config["guild_id"] = guild_id
            
            embed = get_embed(
                "✅ Sunucu Kaydedildi",
                f"Sunucu ID: {guild_id}"
            )
            await ctx.send(embed=embed)
            
            # Ses kanalı seçimi
            await ctx.send(
                "🎙️  **SES KANALI SEÇIMI**\\n\\n" +
                "Botun 24/7 bağlı kalacağı ses kanalını seç:\\n\\n" +
                "**Seçenek 1:** Kanalı ping et\\n" +
                "`#genel-ses` (başlık hangi ses kanalı ise onu yazıyorsun)\\n\\n" +
                "**Seçenek 2:** Kanal adını yazıyorsun\\n" +
                "`genel-ses`\\n\\n" +
                "⏰ **60 saniye içinde cevap vermeli!**"
            )
            
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            
            try:
                voice_msg = await self.bot.wait_for('message', timeout=60.0, check=check)
                
                # Kanal bulma
                voice_channel = None
                
                # Eğer mention varsa
                if voice_msg.channel_mentions:
                    voice_channel = voice_msg.channel_mentions[0]
                else:
                    # Kanal adına göre ara
                    for channel in ctx.guild.voice_channels:
                        if channel.name.lower() == voice_msg.content.lower():
                            voice_channel = channel
                            break
                
                if not voice_channel:
                    await ctx.send("❌ Ses kanalı bulunamadı")
                    return
                
                self.config["voice_channel_id"] = voice_channel.id
                
                embed = get_embed(
                    "✅ Ses Kanalı Kaydedildi",
                    f"Kanal: {voice_channel.mention}"
                )
                await ctx.send(embed=embed)
                
            except asyncio.TimeoutError:
                await ctx.send("❌ Zaman aşımı - kurulum iptal edildi")
                return
            
            # Günlük kanalı
            await ctx.send("📝 Lütfen günlük kanalını ping edin:")
            
            try:
                log_msg = await self.bot.wait_for('message', timeout=60.0, check=check)
                
                log_channel = None
                if log_msg.channel_mentions:
                    log_channel = log_msg.channel_mentions[0]
                else:
                    for channel in ctx.guild.text_channels:
                        if channel.name.lower() == log_msg.content.lower():
                            log_channel = channel
                            break
                
                if log_channel:
                    self.config["log_channel_id"] = log_channel.id
                    embed = get_embed(
                        "✅ Günlük Kanalı Kaydedildi",
                        f"Kanal: {log_channel.mention}"
                    )
                else:
                    embed = get_embed(
                        "⚠️  Uyarı",
                        "Günlük kanalı ayarlanmadı (İsteğe bağlı)"
                    )
                
                await ctx.send(embed=embed)
                
            except asyncio.TimeoutError:
                await ctx.send("⚠️  Günlük kanalı atlandı")
            
            # Bot ID'leri
            self.config["owner_id"] = owner_id
            self.config["bot1_id"] = ctx.guild.me.id  # Örnek olarak
            
            await ctx.send(
                "🤖 **Bot Token'larını ayarlama:**\n" +
                "Bot 1 ve Bot 2 token'larını `.env` dosyasına yazmanız gerekiyor:\n\n" +
                "```\nBOT1_TOKEN=your_bot1_token_here\n" +
                "BOT2_TOKEN=your_bot2_token_here\n```"
            )
            
            # Konfigürasyonu kaydet
            ConfigManager.save_config(self.config)
            
            # Sonuç
            embed = get_embed(
                "✅ KURULUM TAMAMLANDI",
                "Guard Bot sistemi başarıyla kuruldu!\n\n" +
                "**Sonraki Adımlar:**\n" +
                "1️⃣ Bot 1 ve Bot 2 token'larını `.env` dosyasına ekleyin\n" +
                "2️⃣ `python main_bot1.py` ve `python main_bot2.py` çalıştırın\n" +
                "3️⃣ `.status` ile durumu kontrol edin\n\n" +
                "**Temel Komutlar:**\n" +
                "`.warn @kullanıcı [sebep]` - Uyar\n" +
                "`.lock_server` - Sunucuyu kilitle\n" +
                "`.unlock_server` - Kilidi aç\n" +
                "`.purge [sayı]` - Mesaj sil\n" +
                "`.check_bot` - Bot durumu"
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Kurulum sırasında hata: {e}")
            logger.error(f"Kurulum hatası: {e}")
    
    @commands.command(name="status")
    async def status_cmd(self, ctx):
        """Sistem durumunu göster"""
        try:
            embed = get_embed(
                "📊 Guard Bot Sistem Durumu",
                ""
            )
            
            embed.add_field(
                name="⚙️  Konfigürasyon",
                value=f"Sunucu: {self.config.get('guild_id', 'Ayarlanmadı')}\n" +
                      f"Ses Kanalı: {self.config.get('voice_channel_id', 'Ayarlanmadı')}\n" +
                      f"Günlük Kanalı: {self.config.get('log_channel_id', 'Ayarlanmadı')}",
                inline=False
            )
            
            embed.add_field(
                name="🔒 Güvenlik Ayarları",
                value=f"Anti-Spam: {'✅' if self.config['security_features']['anti_spam'] else '❌'}\n" +
                      f"Anti-Raid: {'✅' if self.config['security_features']['anti_raid'] else '❌'}\n" +
                      f"Otomatik Rol: {'✅' if self.config['security_features']['auto_role'] else '❌'}\n" +
                      f"Sunucu Kilidi: {'✅ AÇIK' if self.config['security_features']['server_lock'] else '❌ KAPATIK'}",
                inline=False
            )
            
            embed.add_field(
                name="👥 Koruma",
                value=f"Max Uyarı: {self.config.get('max_warnings', 3)}\n" +
                      f"Korunan Roller: {len(self.config.get('protected_roles', []))}\n" +
                      f"Korunan Kullanıcılar: {len(self.config.get('protected_users', []))}",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Hata: {e}")
    
    @commands.command(name="set_protection")
    async def set_protection(self, ctx, feature: str, state: str):
        """Güvenlik özelliğini aç/kapat"""
        if not is_owner(ctx.author.id, self.config.get("owner_id")):
            await ctx.send("❌ Yetkiniz yok")
            return
        
        try:
            state_bool = state.lower() in ['true', 'on', 'evet', '1', 'aç']
            
            if feature.lower() in self.config["security_features"]:
                self.config["security_features"][feature.lower()] = state_bool
                ConfigManager.save_config(self.config)
                
                embed = get_embed(
                    "✅ Ayar Güncellendi",
                    f"{feature}: {'✅ Açık' if state_bool else '❌ Kapalı'}"
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Bilinmeyen özellik")
                
        except Exception as e:
            await ctx.send(f"❌ Hata: {e}")


import asyncio

def setup(bot):
    """Cog'u yükle"""
    bot.add_cog(SetupManager(bot))
