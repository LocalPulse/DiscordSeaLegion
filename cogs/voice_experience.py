import disnake
from disnake.ext import commands, tasks
import time
import os
import json
from config import user_data

LEVEL_UP_CHANNELS_FILE = "channels.json"
VOICE_TIME_FILE = "voice_time_data.json"
voice_times = {}
level_up_channels = {}
voice_time_data = {}

class VoiceExperience(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_voice_activity.start()
        self.load_level_up_channels()
        self.load_voice_time_data()

    def cog_unload(self):
        self.check_voice_activity.cancel()

    async def send_message_to_channel(self, channel, message):
        try:
            await channel.send(message)
        except Exception as e:
            print(f"[ERROR] Ошибка при отправке сообщения: {e}")

    def load_level_up_channels(self):
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

    def load_voice_time_data(self):
        if os.path.exists(VOICE_TIME_FILE):
            try:
                with open(VOICE_TIME_FILE, "r", encoding="utf-8") as file:
                    global voice_time_data
                    voice_time_data = json.load(file)
            except json.JSONDecodeError:
                print("[ERROR] Ошибка при чтении JSON файла для голосового времени. Используется пустой словарь.")
                voice_time_data = {}
        else:
            voice_time_data = {}

    def save_voice_time_data(self):
        try:
            with open(VOICE_TIME_FILE, "w", encoding="utf-8") as file:
                json.dump(voice_time_data, file, indent=4)
        except Exception as e:
            print(f"[ERROR] Ошибка при сохранении данных о времени в голосе: {e}")

    @tasks.loop(minutes=1)
    async def check_voice_activity(self):
        # Проверка наличия подключенных гильдий
        if not self.bot.guilds:
            print("[WARNING] Бот не подключен ни к одной гильдии.")
            return

        for guild in self.bot.guilds:
            for member in guild.members:
                if member.voice and member.voice.channel:
                    if member.id not in voice_times:
                        voice_times[member.id] = time.time()

                    time_in_channel = time.time() - voice_times[member.id]
                    xp_gained = int(time_in_channel // 30)

                    if xp_gained > 0:
                        user_data[member.id]["xp"] += xp_gained
                        voice_times[member.id] = time.time()

                        if str(member.id) not in voice_time_data:
                            voice_time_data[str(member.id)] = 0
                        voice_time_data[str(member.id)] += time_in_channel // 60

                        self.save_voice_time_data()

                        guild_id = str(guild.id)
                        if guild_id in level_up_channels:
                            channel_id = level_up_channels[guild_id]
                            channel = self.bot.get_channel(int(channel_id))
                            if channel:
                                await self.send_message_to_channel(channel, f"🎉 {member.mention} получил {xp_gained} XP за время, проведенное в голосовом канале! 🕒")
                            else:
                                print(f"[WARNING] Канал с ID {channel_id} не найден, отправка сообщения в первый текстовый канал.")
                                await self.send_message_to_channel(guild.text_channels[0], f"🎉 {member.mention} получил {xp_gained} XP за время, проведенное в голосовом канале! 🕒")
                        else:
                            await self.send_message_to_channel(guild.text_channels[0], f"🎉 {member.mention} получил {xp_gained} XP за время, проведенное в голосовом канале! 🕒")

    @check_voice_activity.before_loop
    async def before_check_voice_activity(self):
        await self.bot.wait_until_ready()  # Ждем, пока бот подключится к серверам

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel is None and before.channel is not None:
            if member.id in voice_times:
                time_in_channel = time.time() - voice_times[member.id]
                xp_gained = int(time_in_channel // 30)
                user_data[member.id]["xp"] += xp_gained

                if str(member.id) not in voice_time_data:
                    voice_time_data[str(member.id)] = 0
                voice_time_data[str(member.id)] += time_in_channel // 60

                self.save_voice_time_data()

                guild_id = str(member.guild.id)
                if guild_id in level_up_channels:
                    channel_id = level_up_channels[guild_id]
                    channel = self.bot.get_channel(int(channel_id))
                    if channel:
                        await self.send_message_to_channel(channel, f"🎉 {member.mention} получил {xp_gained} XP за время в голосовом канале! 🕒")
                    else:
                        print(f"[WARNING] Канал с ID {channel_id} не найден, отправка сообщения в первый текстовый канал.")
                        await self.send_message_to_channel(member.guild.text_channels[0], f"🎉 {member.mention} получил {xp_gained} XP за время в голосовом канале! 🕒")
                else:
                    await self.send_message_to_channel(member.guild.text_channels[0], f"🎉 {member.mention} получил {xp_gained} XP за время в голосовом канале! 🕒")

                del voice_times[member.id]

        elif after.channel is not None and before.channel is None:
            voice_times[member.id] = time.time()


def setup(bot):
    bot.add_cog(VoiceExperience(bot))