"""
Gelişmiş Özellikler - Advanced Features
Anti-Raid, Anti-Spam, Auto-Moderation vb.
"""

import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import logging
from collections import defaultdict
from shared_utils import get_embed

logger = logging.getLogger(__name__)

class AdvancedSecurityFeatures(commands.Cog):
    """Gelişmiş güvenlik sistemi"""
    
    def __init__(self, bot):
        self.bot = bot
        
        # Spam tracking
        self.spam_cache = defaultdict(lambda: {"messages": [], "warnings": 0})
        
        # Raid tracking
        self.join_cache = []
        
        # Flagged users
        self.flagged_users = defaultdict(lambda: {"flags": 0, "reason": []})
        
        self.spam_cleanup.start()
    
    def cog_unload(self):
        self.spam_cleanup.cancel()
    
    @tasks.loop(minutes=5)
    async def spam_cleanup(self):
        """Spam cache'i temizle"""
        current_time = datetime.now()
        users_to_clean = []
        
        for user_id, data in self.spam_cache.items():
            # 5 dakikadan eski mesajları temizle
            data["messages"] = [
                msg_time for msg_time in data["messages"]
                if (current_time - msg_time).seconds < 300
            ]
            
            if not data["messages"] and data["warnings"] == 0:
                users_to_clean.append(user_id)
        
        for user_id in users_to_clean:
            del self.spam_cache[user_id]
    
    async def check_spam(self, message: discord.Message) -> bool:
        """Spam kontrolü"""
        if message.author.bot:
            return False
        
        user_id = message.author.id
        current_time = datetime.now()
        
        # Son 10 saniyedeki mesajları kontrol et
        self.spam_cache[user_id]["messages"].append(current_time)
        
        recent_messages = [
            msg_time for msg_time in self.spam_cache[user_id]["messages"]
            if (current_time - msg_time).seconds < 10
        ]
        
        # 5+ mesaj 10 saniye içinde = Spam
        if len(recent_messages) >= 5:
            self.spam_cache[user_id]["warnings"] += 1
            logger.warning(f"⚠️  {message.author} spam yapıyor")
            return True
        
        return False
    
    async def check_raid(self, guild: discord.Guild, member: discord.Member) -> bool:
        """Raid deseni kontrolü"""
        current_time = datetime.now()
        
        # Son 2 dakikadaki katılışları kontrol et
        self.join_cache.append({
            "time": current_time,
            "member": member
        })
        
        # Eski verileri temizle
        self.join_cache = [
            j for j in self.join_cache
            if (current_time - j["time"]).seconds < 120
        ]
        
        # 10+ üye 2 dakika içinde = Raid
        if len(self.join_cache) >= 10:
            logger.warning(f"🚨 Raid tespiti: {len(self.join_cache)} katılış 2 dakikada")
            return True
        
        return False
    
    async def flag_user(self, user_id: int, reason: str, flag_count: int = 1) -> int:
        """Kullanıcı bayrakla"""
        self.flagged_users[user_id]["flags"] += flag_count
        self.flagged_users[user_id]["reason"].append(reason)
        
        flags = self.flagged_users[user_id]["flags"]
        logger.info(f"🚩 {user_id} bayraklandı: {reason} (Toplam: {flags})")
        
        return flags
    
    async def get_user_risk_score(self, user_id: int) -> dict:
        """Kullanıcı risk puanı hesapla"""
        data = self.flagged_users.get(user_id, {})
        flags = data.get("flags", 0)
        
        # Risk skorunu hesapla
        if flags >= 5:
            risk_level = "🔴 ÇOOK YÜKSEK"
            action = "BAN"
        elif flags >= 3:
            risk_level = "🟠 YÜKSEK"
            action = "KICK"
        elif flags >= 1:
            risk_level = "🟡 ORTA"
            action = "WARN"
        else:
            risk_level = "🟢 DÜŞÜK"
            action = "MONITOR"
        
        return {
            "risk_level": risk_level,
            "flags": flags,
            "reasons": data.get("reason", []),
            "recommended_action": action
        }
    
    @commands.command(name="risk_check")
    async def risk_check(self, ctx, member: discord.Member):
        """Kullanıcı risk kontrolü"""
        from shared_utils import is_owner, ConfigManager
        config = ConfigManager.load_config()
        
        if not is_owner(ctx.author.id, config.get("owner_id")):
            await ctx.send("❌ Yetkiniz yok")
            return
        
        risk = await self.get_user_risk_score(member.id)
        
        embed = get_embed(
            "🚩 Kullanıcı Risk Analizi",
            f"**Kullanıcı:** {member.mention}\n" +
            f"**Risk Seviyesi:** {risk['risk_level']}\n" +
            f"**Bayrak Sayısı:** {risk['flags']}\n" +
            f"**Önerilen İşlem:** {risk['recommended_action']}"
        )
        
        if risk["reasons"]:
            embed.add_field(
                name="Sebepler",
                value="\n".join(risk["reasons"][:5]),
                inline=False
            )
        
        await ctx.send(embed=embed)


class AutoModerator(commands.Cog):
    """Otomatik moderasyon"""
    
    def __init__(self, bot):
        self.bot = bot
        
        # Yasak kelimeler
        self.banned_words = [
            "spam", "buy", "click here", "free money"
        ]
    
    async def scan_message(self, message: discord.Message) -> tuple[bool, str]:
        """Mesajı tara"""
        content = message.content.lower()
        
        for word in self.banned_words:
            if word in content:
                return True, f"Yasak kelime bulundu: {word}"
        
        # URL kontrolü
        if "http://" in content or "https://" in content:
            # Sadece whitelisted URL'leri izin ver
            if not any(domain in content for domain in ["discord.gg", "twitch.tv"]):
                return True, "Şüpheli URL bulundu"
        
        return False, ""
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Mesaj kontrolü"""
        if message.author.bot:
            return
        
        is_flagged, reason = await self.scan_message(message)
        
        if is_flagged:
            logger.warning(f"🚫 {message.author} flaglandi: {reason}")
            
            try:
                await message.delete()
                await message.channel.send(
                    f"⚠️  {message.author.mention} - {reason}\n" +
                    "Uygunsuz içerik paylaşmayın.",
                    delete_after=5
                )
            except:
                pass


class ReputationSystem(commands.Cog):
    """İtibar sistemi - Olumlu ve olumsuz davranış takibi"""
    
    def __init__(self, bot):
        self.bot = bot
        self.reputation = defaultdict(lambda: {"positive": 0, "negative": 0})
    
    def get_reputation_score(self, user_id: int) -> int:
        """İtibar puanı hesapla"""
        data = self.reputation[user_id]
        return data["positive"] - data["negative"]
    
    async def add_reputation(self, user_id: int, amount: int, reason: str):
        """İtibar ekle"""
        if amount > 0:
            self.reputation[user_id]["positive"] += amount
            logger.info(f"⬆️  {user_id} itibarı +{amount}: {reason}")
        else:
            self.reputation[user_id]["negative"] += abs(amount)
            logger.info(f"⬇️  {user_id} itibarı {amount}: {reason}")
    
    @commands.command(name="reputation")
    async def reputation(self, ctx, member: discord.Member = None):
        """İtibar durumu göster"""
        target = member or ctx.author
        score = self.get_reputation_score(target.id)
        data = self.reputation[target.id]
        
        if score >= 10:
            status = "⭐ Özel Üye"
        elif score >= 5:
            status = "😊 Saygıdeğer"
        elif score >= 0:
            status = "😐 Normal"
        elif score >= -5:
            status = "😠 Şüpheli"
        else:
            status = "🚫 Kötü"
        
        embed = get_embed(
            f"📊 İtibar - {target.name}",
            f"**Durum:** {status}\n" +
            f"**Skor:** {score}\n" +
            f"**Olumlu:** +{data['positive']}\n" +
            f"**Olumsuz:** -{data['negative']}"
        )
        
        await ctx.send(embed=embed)


# Setup
def setup(bot):
    """Gelişmiş özellikleri yükle"""
    bot.add_cog(AdvancedSecurityFeatures(bot))
    bot.add_cog(AutoModerator(bot))
    bot.add_cog(ReputationSystem(bot))
