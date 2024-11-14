import disnake
from disnake.ext import commands
import json
import os

CHANNELS_FILE = "channels.json"
level_up_channels = {}

class ChannelManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.load_level_up_channels()

    def load_level_up_channels(self):
        if os.path.exists(CHANNELS_FILE):
            try:
                with open(CHANNELS_FILE, "r", encoding="utf-8") as file:
                    global level_up_channels
                    level_up_channels = json.load(file)
            except json.JSONDecodeError:
                print("[ERROR] Ошибка при чтении JSON файла. Используется пустой словарь для каналов.")
                level_up_channels = {}
        else:
            level_up_channels = {}

    def save_level_up_channels(self):
        try:
            with open(CHANNELS_FILE, "w", encoding="utf-8") as file:
                json.dump(level_up_channels, file, indent=4)
        except Exception as e:
            print(f"[ERROR] Ошибка при сохранении настроек каналов: {e}")

    @commands.command(name="set_channel1")
    @commands.has_permissions(administrator=True)
    async def set_channel(self, ctx, channel: disnake.TextChannel = None):
        if channel is None:
            await ctx.send(
                "⚠️ Вы не указали канал. Укажите текстовый канал, где бот будет отправлять сообщения о достижении уровня.\n"
                "Пример использования: `!set_channel #канал`"
            )
            return

        guild_id = ctx.guild.id
        level_up_channels[guild_id] = channel.id
        self.save_level_up_channels()
        await ctx.send(f"✅ Канал для сообщений уровня на этом сервере установлен: {channel.mention}")

def setup(bot):
    bot.add_cog(ChannelManagement(bot))