import json
import os
import logging
from datetime import datetime
from typing import Dict, Optional, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_FILE = 'bot_config.json'

# ==================== MONGODB VERİ KATMANI ====================

try:
    from motor.motor_asyncio import AsyncIOMotorClient
    _MOTOR_AVAILABLE = True
except ImportError:
    _MOTOR_AVAILABLE = False
    logger.warning("motor yüklü değil - veritabanı özellikleri devre dışı")

_MONGO_URL = os.getenv("MONGODB_URL", "")
_MONGO_DB = os.getenv("MONGODB_DB_NAME", "guardbot")


class Database:
    """MongoDB asenkron veri katmanı.
    Tüm kalıcı veri (uyarılar, kayıtlar, yapılandırma) burada tutulur.
    Motor (async) kullanır; bot yeniden başlasa bile veriler korunur.
    """

    _client = None
    _db = None
    _connected = False

    @classmethod
    async def connect(cls) -> bool:
        if not _MOTOR_AVAILABLE or not _MONGO_URL:
            logger.warning("MongoDB bağlantısı atlandı (motor yok veya URL yok)")
            return False
        if cls._connected and cls._client is not None:
            return True
        try:
            cls._client = AsyncIOMotorClient(_MONGO_URL, serverSelectionTimeoutMS=8000)
            cls._db = cls._client[_MONGO_DB]
            await cls._client.admin.command("ping")
            cls._connected = True
            logger.info("✅ MongoDB bağlantısı kuruldu")
            return True
        except Exception as e:
            logger.error(f"❌ MongoDB bağlantı hatası: {e}")
            cls._connected = False
            return False

    @classmethod
    def is_connected(cls) -> bool:
        return cls._connected

    @classmethod
    def _get_db(cls):
        return cls._db

    # ---------- UYARILAR ----------

    @classmethod
    async def add_warn(cls, guild_id: int, user_id: int, moderator_id: int, reason: str) -> int:
        """Uyarı ekle ve toplam sayıyı döndür."""
        if not cls._connected:
            return 0
        try:
            doc = {
                "guild_id": guild_id,
                "user_id": user_id,
                "moderator_id": moderator_id,
                "reason": reason,
                "timestamp": datetime.utcnow()
            }
            await cls._db["warns"].insert_one(doc)
            count = await cls._db["warns"].count_documents({
                "guild_id": guild_id,
                "user_id": user_id
            })
            return count
        except Exception as e:
            logger.error(f"Uyarı ekleme hatası: {e}")
            return 0

    @classmethod
    async def get_warns(cls, guild_id: int, user_id: int) -> List[Dict[str, Any]]:
        if not cls._connected:
            return []
        try:
            cursor = cls._db["warns"].find({
                "guild_id": guild_id,
                "user_id": user_id
            }).sort("timestamp", -1)
            return await cursor.to_list(length=50)
        except Exception as e:
            logger.error(f"Uyarı okuma hatası: {e}")
            return []

    @classmethod
    async def get_warn_count(cls, guild_id: int, user_id: int) -> int:
        if not cls._connected:
            return 0
        try:
            return await cls._db["warns"].count_documents({
                "guild_id": guild_id,
                "user_id": user_id
            })
        except Exception as e:
            logger.error(f"Uyarı sayma hatası: {e}")
            return 0

    @classmethod
    async def clear_warns(cls, guild_id: int, user_id: int) -> int:
        if not cls._connected:
            return 0
        try:
            result = await cls._db["warns"].delete_many({
                "guild_id": guild_id,
                "user_id": user_id
            })
            return result.deleted_count
        except Exception as e:
            logger.error(f"Uyarı temizleme hatası: {e}")
            return 0

    # ---------- GÜVENLİK KAYITLARI ----------

    @classmethod
    async def add_log(cls, guild_id: int, event_type: str, details: str, actor_id: int = None) -> bool:
        if not cls._connected:
            return False
        try:
            doc = {
                "guild_id": guild_id,
                "type": event_type,
                "details": details,
                "actor_id": actor_id,
                "timestamp": datetime.utcnow()
            }
            await cls._db["security_logs"].insert_one(doc)
            return True
        except Exception as e:
            logger.error(f"Kayıt ekleme hatası: {e}")
            return False

    @classmethod
    async def get_recent_logs(cls, guild_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        if not cls._connected:
            return []
        try:
            cursor = cls._db["security_logs"].find(
                {"guild_id": guild_id}
            ).sort("timestamp", -1).limit(limit)
            return await cursor.to_list(length=limit)
        except Exception as e:
            logger.error(f"Kayıt okuma hatası: {e}")
            return []

    # ---------- YAPILANDIRMA ----------

    @classmethod
    async def save_guild_config(cls, guild_id: int, config: Dict) -> bool:
        if not cls._connected:
            return False
        try:
            config["guild_id"] = guild_id
            config["updated_at"] = datetime.utcnow()
            await cls._db["guild_configs"].update_one(
                {"guild_id": guild_id},
                {"$set": config},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Yapılandırma kaydetme hatası: {e}")
            return False

    @classmethod
    async def load_guild_config(cls, guild_id: int) -> Optional[Dict]:
        if not cls._connected:
            return None
        try:
            doc = await cls._db["guild_configs"].find_one({"guild_id": guild_id})
            if doc:
                doc.pop("_id", None)
                doc.pop("updated_at", None)
            return doc
        except Exception as e:
            logger.error(f"Yapılandırma okuma hatası: {e}")
            return None

    # ---------- KORUNAN ÖĞELER ----------

    @classmethod
    async def add_protected_role(cls, guild_id: int, role_id: int) -> bool:
        if not cls._connected:
            return False
        try:
            await cls._db["protected_roles"].update_one(
                {"guild_id": guild_id, "role_id": role_id},
                {"$set": {"guild_id": guild_id, "role_id": role_id}},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Korumalı rol ekleme hatası: {e}")
            return False

    @classmethod
    async def remove_protected_role(cls, guild_id: int, role_id: int) -> bool:
        if not cls._connected:
            return False
        try:
            result = await cls._db["protected_roles"].delete_one(
                {"guild_id": guild_id, "role_id": role_id}
            )
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Korumalı rol silme hatası: {e}")
            return False

    @classmethod
    async def get_protected_roles(cls, guild_id: int) -> List[int]:
        if not cls._connected:
            return []
        try:
            cursor = cls._db["protected_roles"].find({"guild_id": guild_id})
            docs = await cursor.to_list(length=100)
            return [d["role_id"] for d in docs]
        except Exception as e:
            logger.error(f"Korumalı rol okuma hatası: {e}")
            return []

    # ---------- YASAK KELİMELER ----------

    @classmethod
    async def add_banned_word(cls, guild_id: int, word: str) -> bool:
        if not cls._connected:
            return False
        try:
            word = word.lower().strip()
            await cls._db["banned_words"].update_one(
                {"guild_id": guild_id, "word": word},
                {"$set": {"guild_id": guild_id, "word": word}},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Yasak kelime ekleme hatası: {e}")
            return False

    @classmethod
    async def remove_banned_word(cls, guild_id: int, word: str) -> bool:
        if not cls._connected:
            return False
        try:
            result = await cls._db["banned_words"].delete_one(
                {"guild_id": guild_id, "word": word.lower().strip()}
            )
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Yasak kelime silme hatası: {e}")
            return False

    @classmethod
    async def get_banned_words(cls, guild_id: int) -> List[str]:
        if not cls._connected:
            return []
        try:
            cursor = cls._db["banned_words"].find({"guild_id": guild_id})
            docs = await cursor.to_list(length=500)
            return [d["word"] for d in docs]
        except Exception as e:
            logger.error(f"Yasak kelime okuma hatası: {e}")
            return []

    # ---------- ANTI-RAID TAKİBİ ----------

    @classmethod
    async def record_join(cls, guild_id: int, user_id: int) -> int:
        """Üye girişini kaydet ve son 60 saniyedeki toplam giriş sayısını döndür."""
        if not cls._connected:
            return 0
        try:
            now = datetime.utcnow()
            await cls._db["join_events"].insert_one({
                "guild_id": guild_id,
                "user_id": user_id,
                "timestamp": now
            })
            from datetime import timedelta
            threshold = now - timedelta(seconds=60)
            count = await cls._db["join_events"].count_documents({
                "guild_id": guild_id,
                "timestamp": {"$gte": threshold}
            })
            return count
        except Exception as e:
            logger.error(f"Giriş kaydı hatası: {e}")
            return 0

    @classmethod
    async def cleanup_old_joins(cls, guild_id: int) -> None:
        """60 saniyeden eski giriş kayıtlarını temizle."""
        if not cls._connected:
            return
        try:
            from datetime import timedelta
            threshold = datetime.utcnow() - timedelta(seconds=120)
            await cls._db["join_events"].delete_many({
                "guild_id": guild_id,
                "timestamp": {"$lt": threshold}
            })
        except Exception as e:
            logger.error(f"Eski giriş temizleme hatası: {e}")

    @classmethod
    async def close(cls) -> None:
        if cls._client:
            cls._client.close()
            cls._connected = False

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
