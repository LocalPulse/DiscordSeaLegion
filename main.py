import disnake
from disnake.ext import commands
import random
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = disnake.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

user_data = {}
exp_range = {"min": 5, "max": 15}

def calculate_level(xp):
    return int(xp ** (1/3))

@bot.event
async def on_ready():
    print(f'Бот {bot.user} подключен и готов к работе!')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id
    if user_id not in user_data:
        user_data[user_id] = {"xp": 0, "level": 1}

    xp_gained = random.randint(exp_range["min"], exp_range["max"])
    user_data[user_id]["xp"] += xp_gained

    new_level = calculate_level(user_data[user_id]["xp"])
    if new_level > user_data[user_id]["level"]:
        user_data[user_id]["level"] = new_level
        await message.channel.send(f"{message.author.mention} достиг {new_level} уровня! 🎉")

    await bot.process_commands(message)

@bot.slash_command(description="Показывает ваш уровень и XP")
async def rank(inter: disnake.ApplicationCommandInteraction):
    user_id = inter.author.id
    if user_id in user_data:
        level = user_data[user_id]["level"]
        xp = user_data[user_id]["xp"]
        await inter.response.send_message(f"{inter.author.mention}, ваш уровень: {level}, XP: {xp}")
    else:
        await inter.response.send_message(f"{inter.author.mention}, у вас пока нет XP. Начните писать сообщения, чтобы зарабатывать XP!")

@bot.slash_command(description="Настраивает диапазон случайного получения опыта за сообщения")
@commands.has_permissions(administrator=True)
async def set_exp_range(
    inter: disnake.ApplicationCommandInteraction,
    min_exp: int,
    max_exp: int
):
    if min_exp < 0 or max_exp < 0:
        await inter.response.send_message("Минимальный и максимальный опыт не могут быть отрицательными числами.", ephemeral=True)
        return

    if min_exp > max_exp:
        await inter.response.send_message("Минимальное значение опыта не может быть больше максимального.", ephemeral=True)
        return

    exp_range["min"] = min_exp
    exp_range["max"] = max_exp
    await inter.response.send_message(f"Диапазон получения опыта установлен: от {min_exp} до {max_exp} за сообщение.")

@bot.slash_command(description="Изменяет уровень и опыт пользователя")
@commands.has_permissions(administrator=True)
async def edit_rank(
    inter: disnake.ApplicationCommandInteraction,
    user: disnake.Member,
    level: int = None,
    xp: int = None
):
    if user.id not in user_data:
        user_data[user.id] = {"xp": 0, "level": 1}

    if level is not None:
        user_data[user.id]["level"] = level
    if xp is not None:
        user_data[user.id]["xp"] = xp

    new_level = calculate_level(user_data[user.id]["xp"])
    if new_level != user_data[user.id]["level"]:
        user_data[user.id]["level"] = new_level

    await inter.response.send_message(
        f"Уровень и опыт {user.mention} обновлены: Уровень — {user_data[user.id]['level']}, XP — {user_data[user.id]['xp']}."
    )

@bot.slash_command(description="Отправляет приветственное сообщение")
async def hello(inter: disnake.ApplicationCommandInteraction):
    await inter.response.send_message("Привет")

bot.run(TOKEN)