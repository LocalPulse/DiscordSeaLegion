import disnake
from disnake.ext import commands, tasks
import time
import os
from config import user_data  # Подключаем user_data для сохранения XP

# Словарь для хранения времени входа пользователя в голосовой канал
voice_times = {}

class VoiceExperience(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_voice_activity.start()  # Запускаем задачу по проверке активности пользователей

    def cog_unload(self):
        """Останавливаем задачу при выгрузке cog"""
        self.check_voice_activity.cancel()

    @tasks.loop(minutes=1)
    async def check_voice_activity(self):
        """Проверка активности пользователей в голосовых каналах каждую минуту"""
        for member in self.bot.guilds[0].members:  # Предположим, что бот подключен к одному серверу
            if member.voice:
                # Если пользователь в голосовом канале, начисляем ему опыт
                if member.id not in voice_times:
                    voice_times[member.id] = time.time()  # Запоминаем время входа в канал

                # Рассчитываем время нахождения в канале
                time_in_channel = time.time() - voice_times[member.id]
                xp_gained = int(time_in_channel // 60)  # 1 XP за минуту в голосовом канале

                if xp_gained > 0:
                    user_data[member.id]["xp"] += xp_gained  # Добавляем XP
                    voice_times[member.id] = time.time()  # Обновляем время входа в канал

                    # Отправляем сообщение о получении опыта
                    await member.guild.text_channels[0].send(f"{member.mention} получил {xp_gained} XP за время в голосовом канале!")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Слушаем изменения голосовых состояний (вход/выход из голосовых каналов)"""
        if after.channel is None and before.channel is not None:
            # Пользователь покидает голосовой канал
            if member.id in voice_times:
                time_in_channel = time.time() - voice_times[member.id]
                xp_gained = int(time_in_channel // 60)  # XP за время в канале
                user_data[member.id]["xp"] += xp_gained

                # Отправляем сообщение о получении XP
                await member.guild.text_channels[0].send(f"{member.mention} получил {xp_gained} XP за время в голосовом канале!")
                del voice_times[member.id]  # Убираем пользователя из словаря

        elif after.channel is not None and before.channel is None:
            # Пользователь зашел в голосовой канал
            voice_times[member.id] = time.time()  # Запоминаем время входа в канал

def setup(bot):
    bot.add_cog(VoiceExperience(bot))