import disnake
from disnake.ext import commands, tasks
import time
import os
from config import user_data
import json

VOICE_CHANNELS_FILE = "channels.json"
voice_times = {}
voice_channel_notifications = {}


class VoiceExperience(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_voice_activity.start()
        self.load_voice_channels()

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

                    guild_id = member.guild.id
                    if guild_id in voice_channel_notifications:
                        channel = self.bot.get_channel(voice_channel_notifications[guild_id])
                        if channel:
                            await channel.send(f"{member.mention} получил {xp_gained} XP за время в голосовом канале!")
                    else:
                        await member.guild.text_channels[0].send(
                            f"{member.mention} получил {xp_gained} XP за время в голосовом канале!")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Слушаем изменения голосовых состояний (вход/выход из голосовых каналов)"""
        if after.channel is None and before.channel is not None:
            if member.id in voice_times:
                time_in_channel = time.time() - voice_times[member.id]
                xp_gained = int(time_in_channel // 60)
                user_data[member.id]["xp"] += xp_gained

                guild_id = member.guild.id
                if guild_id in voice_channel_notifications:
                    channel = self.bot.get_channel(voice_channel_notifications[guild_id])
                    if channel:
                        await channel.send(f"{member.mention} получил {xp_gained} XP за время в голосовом канале!")
                else:
                    await member.guild.text_channels[0].send(
                        f"{member.mention} получил {xp_gained} XP за время в голосовом канале!")

                del voice_times[member.id]

        elif after.channel is not None and before.channel is None:
            voice_times[member.id] = time.time()

    def load_voice_channels(self):
        """Загружаем настройки каналов из JSON-файла."""
        if os.path.exists(VOICE_CHANNELS_FILE):
            try:
                with open(VOICE_CHANNELS_FILE, "r", encoding="utf-8") as file:
                    global voice_channel_notifications
                    voice_channel_notifications = json.load(file)
            except json.JSONDecodeError:
                print("[ERROR] Ошибка при чтении JSON файла. Используется пустой словарь для каналов.")
                voice_channel_notifications = {}
        else:
            voice_channel_notifications = {}

    def save_voice_channels(self):
        """Сохраняем настройки каналов в JSON-файл."""
        try:
            with open(VOICE_CHANNELS_FILE, "w", encoding="utf-8") as file:
                json.dump(voice_channel_notifications, file, indent=4)
        except Exception as e:
            print(f"[ERROR] Ошибка при сохранении настроек каналов: {e}")


def setup(bot):
    bot.add_cog(VoiceExperience(bot))