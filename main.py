import disnake
from disnake.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = disnake.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="sl.", intents=intents, help_command=None)

bot.load_extension("cogs.leveling")
bot.load_extension("cogs.role_management")
bot.load_extension("cogs.voice_experience")
bot.load_extension("cogs.help")

@bot.event
async def on_ready():
    print(f'Бот {bot.user} подключен и готов к работе!')

bot.run(TOKEN)