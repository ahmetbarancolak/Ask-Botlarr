import json
import os
import logging
from datetime import datetime
from typing import Dict, Optional, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_FILE = 'bot_config.json'

# Modern renk paleti
COLORS = {
    "primary": 0x2B6CF6,      # Mavi
    "success": 0x2ECC71,      # Yeşil
    "warning": 0xF1C40F,     # Sarı
    "error":   0xE74C3C,     # Kırmızı
    "info":    0x3498DB,     # Açık mavi
    "neutral": 0x2F3136,     # Koyu gri
    "accent":  0xE67E22,     # Turuncu
    "purple":  0x9B59B6,     # Mor (özel durumlar)
}

class ConfigManager:
    """Konfigürasyon yöneticisi"""

    @staticmethod
    def load_config() -> Dict:
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Konfigürasyon okunamadı: {e}")
                return ConfigManager.default_config()
        return ConfigManager.default_config()

    @staticmethod
    def save_config(config: Dict) -> bool:
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Konfigürasyon kaydedilemedi: {e}")
            return False

    @staticmethod
    def default_config() -> Dict:
        return {
            "owner_id": None,
            "guild_id": None,
            "voice_channel_id": None,
            "log_channel_id": None,
            "bot1_token": None,
            "bot2_token": None,
            "bot1_id": None,
            "bot2_id": None,
            "moderation_enabled": True,
            "max_warnings": 3,
            "security_features": {
                "anti_spam": True,
                "anti_raid": True,
                "auto_role": True,
                "server_lock": False
            },
            "protected_roles": [],
            "protected_users": [],
            "last_setup": None,
            "version": "1.0.0"
        }

class StatusManager:
    """Bot durum yöneticisi"""

    STATUS_FILE = 'bot_status.json'

    @staticmethod
    def save_status(bot_id: int, status: str, timestamp: str = None) -> bool:
        try:
            data = {}
            if os.path.exists(StatusManager.STATUS_FILE):
                with open(StatusManager.STATUS_FILE, 'r') as f:
                    data = json.load(f)
            data[str(bot_id)] = {
                "status": status,
                "last_heartbeat": timestamp or datetime.now().isoformat(),
                "online": status == "online"
            }
            with open(StatusManager.STATUS_FILE, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Durum kaydedilemedi: {e}")
            return False

    @staticmethod
    def get_bot_status(bot_id: int) -> Optional[Dict]:
        try:
            if os.path.exists(StatusManager.STATUS_FILE):
                with open(StatusManager.STATUS_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get(str(bot_id))
        except Exception as e:
            logger.error(f"Durum okunamadı: {e}")
        return None

    @staticmethod
    def get_active_bot() -> Optional[int]:
        try:
            if os.path.exists(StatusManager.STATUS_FILE):
                with open(StatusManager.STATUS_FILE, 'r') as f:
                    data = json.load(f)
                    for bot_id, info in data.items():
                        if info.get("online"):
                            return int(bot_id)
        except Exception as e:
            logger.error(f"Aktif bot bulunamadı: {e}")
        return None

class SecurityManager:
    """Güvenlik yönetimi"""

    @staticmethod
    def check_raid_pattern(members_joined: int, time_window_seconds: int = 60) -> bool:
        return members_joined > 5 if time_window_seconds == 60 else False

    @staticmethod
    def check_spam(user_id: int, message_count: int = 5, time_window: int = 10) -> bool:
        return message_count > 5

    @staticmethod
    def log_event(guild_id: int, event_type: str, details: str) -> None:
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "type": event_type,
            "details": details
        }
        logger.info(f"[{event_type}] {details}")

def is_owner(user_id: int, owner_id: int) -> bool:
    return user_id == owner_id

def has_admin_perms(member) -> bool:
    return member.guild_permissions.administrator

def get_embed(title: str, description: str, color: int = COLORS["neutral"]) -> 'discord.Embed':
    """Basit embed oluştur (eski çağrılarla uyumlu)"""
    from discord import Embed
    embed = Embed(title=title, description=description, color=color)
    embed.timestamp = datetime.now()
    return embed

def modern_embed(
    title: str = "",
    description: str = "",
    color: int = COLORS["primary"],
    author_name: str = None,
    author_icon: str = None,
    thumbnail: str = None,
    image: str = None,
    footer: str = "Guard Bot Sistemi",
    footer_icon: str = None,
    fields: List[Dict] = None,
    inline_fields: bool = True
) -> 'discord.Embed':
    """Modern, tutarlı görselli embed oluşturucu.

    fields: [{"name": str, "value": str, "inline": bool (opsiyonel)}]
    """
    from discord import Embed
    embed = Embed(title=title, description=description, color=color)
    embed.timestamp = datetime.now()

    if author_name:
        embed.set_author(name=author_name, icon_url=author_icon)
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    if image:
        embed.set_image(url=image)
    embed.set_footer(text=footer, icon_url=footer_icon)

    if fields:
        for f in fields:
            embed.add_field(
                name=f.get("name", "\u200b"),
                value=f.get("value", "\u200b"),
                inline=f.get("inline", inline_fields)
            )
    return embed

def success_embed(title: str, description: str = "") -> 'discord.Embed':
    return modern_embed(
        title=f"✅ {title}",
        description=description,
        color=COLORS["success"],
        footer="Guard Bot • Başarılı"
    )

def error_embed(title: str, description: str = "") -> 'discord.Embed':
    return modern_embed(
        title=f"❌ {title}",
        description=description,
        color=COLORS["error"],
        footer="Guard Bot • Hata"
    )

def warning_embed(title: str, description: str = "") -> 'discord.Embed':
    return modern_embed(
        title=f"⚠️ {title}",
        description=description,
        color=COLORS["warning"],
        footer="Guard Bot • Uyarı"
    )

def info_embed(title: str, description: str = "") -> 'discord.Embed':
    return modern_embed(
        title=title,
        description=description,
        color=COLORS["info"],
        footer="Guard Bot • Bilgi"
    )
