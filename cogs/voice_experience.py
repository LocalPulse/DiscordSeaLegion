import disnake
from disnake.ext import commands, tasks
import time
import os
from config import user_data

voice_times = {}

class VoiceExperience(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_voice_activity.start()

    def cog_unload(self):
        """Останавливаем задачу при выгрузке cog"""
        self.check_voice_activity.cancel()

    @tasks.loop(minutes=1)
    async def check_voice_activity(self):
        """Проверка активности пользователей в голосовых каналах каждую минуту"""
        for member in self.bot.guilds[0].members:
            if member.voice:
                if member.id not in voice_times:
                    voice_times[member.id] = time.time()

                time_in_channel = time.time() - voice_times[member.id]
                xp_gained = int(time_in_channel // 60)

                if xp_gained > 0:
                    user_data[member.id]["xp"] += xp_gained
                    voice_times[member.id] = time.time()

                    await member.guild.text_channels[0].send(f"{member.mention} получил {xp_gained} XP за время в голосовом канале!")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Слушаем изменения голосовых состояний (вход/выход из голосовых каналов)"""
        if after.channel is None and before.channel is not None:
            # Пользователь покидает голосовой канал
            if member.id in voice_times:
                time_in_channel = time.time() - voice_times[member.id]
                xp_gained = int(time_in_channel // 60)
                user_data[member.id]["xp"] += xp_gained

                await member.guild.text_channels[0].send(f"{member.mention} получил {xp_gained} XP за время в голосовом канале!")
                del voice_times[member.id]

        elif after.channel is not None and before.channel is None:
            voice_times[member.id] = time.time()

def setup(bot):
    bot.add_cog(VoiceExperience(bot))