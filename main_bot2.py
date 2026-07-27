"""
Guard Bot 2 - Yedek Bot
24/7 sunucu koruma sistemi (Yedekli)
"""

import discord
from discord.ext import commands
import logging
import os
from dotenv import load_dotenv
import asyncio
from shared_utils import ConfigManager, StatusManager

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot Kurulumu
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.voice_states = True
intents.messages = True

bot = commands.Bot(
    command_prefix='.', 
    intents=intents,
    help_command=commands.DefaultHelpCommand()
)

# Token
BOT_TOKEN = os.getenv('BOT2_TOKEN')

if not BOT_TOKEN:
    logger.error("❌ BOT2_TOKEN tanımlanmamış. .env dosyasını kontrol edin")
    exit(1)

@bot.event
async def on_ready():
    """Bot başlatıldığında"""
    logger.info(f"✅ Guard Bot 2 Hazır - {bot.user}")
    
    config = ConfigManager.load_config()
    config["bot2_id"] = bot.user.id
    ConfigManager.save_config(config)
    
    # Durum ayarla
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="🛡️ Sunucuyu Koruyor (Yedek) | .help"
        )
    )

@bot.event
async def on_command_error(ctx, error):
    """Komut hatalarını işle"""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Eksik argüman: {error.param.name}")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Yeterli izniniz yok")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ Komut bulunamadı: {ctx.message.content}")
    else:
        await ctx.send(f"❌ Bir hata oluştu: {error}")
        logger.error(f"Komut hatası: {error}")

# Cog'ları yükle
cogs_loaded = False

async def load_cogs():
    """Tüm Cog'ları yükle"""
    global cogs_loaded
    if cogs_loaded:
        return
    
    try:
        # Guard Bot 2 Cog'ı yükle
        try:
            from guard_bot2 import GuardBot2
            await bot.add_cog(GuardBot2(bot))
            logger.info("✅ Guard Bot 2 Cog yüklendi")
        except Exception as e:
            logger.error(f"❌ Guard Bot 2 yüklenemedi: {e}")
        
        # Setup Manager Cog'ı yükle
        try:
            from setup_manager import SetupManager
            await bot.add_cog(SetupManager(bot))
            logger.info("✅ Setup Manager yüklendi")
        except Exception as e:
            logger.error(f"❌ Setup Manager yüklenemedi: {e}")
        
        # Advanced Features Cog'ı yükle (İsteğe bağlı)
        try:
            from advanced_features import AdvancedSecurityFeatures, AutoModerator, ReputationSystem
            await bot.add_cog(AdvancedSecurityFeatures(bot))
            await bot.add_cog(AutoModerator(bot))
            await bot.add_cog(ReputationSystem(bot))
            logger.info("✅ Advanced Features yüklendi")
        except Exception as e:
            logger.debug(f"⚠️  Advanced Features yüklenemedi: {e}")
        
        cogs_loaded = True
        logger.info("✅ Tüm Cog'lar başarıyla yüklendi")
        
    except Exception as e:
        logger.error(f"❌ Cog yükleme hatası: {e}")

@bot.event
async def on_connect():
    """Bağlantı kurulduğunda"""
    logger.info("🔗 Discord'a bağlantı kuruldu")
    await load_cogs()

@bot.event
async def on_disconnect():
    """Bağlantı kesildiğinde"""
    global cogs_loaded
    cogs_loaded = False
    logger.warning("⚠️  Discord'dan bağlantı kesildi")

# Başlatma
if __name__ == "__main__":
    logger.info("🚀 Guard Bot 2 başlatılıyor...")
    try:
        bot.run(BOT_TOKEN)
    except Exception as e:
        logger.error(f"❌ Bot çalışılamadı: {e}")
