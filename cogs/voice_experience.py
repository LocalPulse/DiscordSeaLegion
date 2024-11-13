import disnake
from disnake.ext import commands, tasks
import time
import os
import json
from config import user_data

LEVEL_UP_CHANNELS_FILE = "level_up_channels.json"
voice_times = {}
level_up_channels = {}

class VoiceExperience(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_voice_activity.start()
        self.load_level_up_channels()

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

                    guild_id = str(member.guild.id)
                    if guild_id in level_up_channels:
                        channel_id = level_up_channels[guild_id]
                        channel = self.bot.get_channel(int(channel_id))
                        if channel:
                            await channel.send(f"{member.mention} получил {xp_gained} XP за время в голосовом канале!")
                        else:
                            await self.send_to_default_channel(member, xp_gained)
                    else:
                        await self.send_to_default_channel(member, xp_gained)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Слушаем изменения голосовых состояний (вход/выход из голосовых каналов)"""
        if after.channel is None and before.channel is not None:
            if member.id in voice_times:
                time_in_channel = time.time() - voice_times[member.id]
                xp_gained = int(time_in_channel // 60)
                user_data[member.id]["xp"] += xp_gained

                guild_id = str(member.guild.id)
                if guild_id in level_up_channels:
                    channel_id = level_up_channels[guild_id]
                    channel = self.bot.get_channel(int(channel_id))
                    if channel:
                        await channel.send(f"{member.mention} получил {xp_gained} XP за время в голосовом канале!")
                    else:
                        await self.send_to_default_channel(member, xp_gained)
                else:
                    await self.send_to_default_channel(member, xp_gained)

                del voice_times[member.id]

        elif after.channel is not None and before.channel is None:
            voice_times[member.id] = time.time()

    async def send_to_default_channel(self, member, xp_gained):
        """Отправляем сообщение в стандартный текстовый канал на сервере"""
        text_channel = member.guild.text_channels[0]
        await text_channel.send(f"{member.mention} получил {xp_gained} XP за время в голосовом канале!")

    def load_level_up_channels(self):
        """Загружаем настройки каналов для уровня из JSON-файла."""
        if os.path.exists(LEVEL_UP_CHANNELS_FILE):
            try:
                with open(LEVEL_UP_CHANNELS_FILE, "r", encoding="utf-8") as file:
                    global level_up_channels
                    level_up_channels = json.load(file)
            except json.JSONDecodeError:
                print("[ERROR] Ошибка при чтении JSON файла для каналов уровня. Используется пустой словарь.")
                level_up_channels = {}
        else:
            level_up_channels = {}

    def save_level_up_channels(self):
        """Сохраняем настройки каналов уровня в JSON-файл."""
        try:
            with open(LEVEL_UP_CHANNELS_FILE, "w", encoding="utf-8") as file:
                json.dump(level_up_channels, file, indent=4)
        except Exception as e:
            print(f"[ERROR] Ошибка при сохранении настроек каналов уровня: {e}")


def setup(bot):
    bot.add_cog(VoiceExperience(bot))