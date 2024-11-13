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

role_assignments = {
    "duty_guard": {
        5: "Дозорный 5 уровня",
        10: "Дозорный 10 уровня",
    },
    "pirate": {
        5: "Пират 5 уровня",
        10: "Пират 10 уровня",
    }
}

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

        # Проверяем, какую роль уже имеет пользователь
        roles = message.author.roles
        role_to_check = None

        # Проверяем, есть ли у пользователя роль "Дозорный" или "Пират"
        if any(role.name == "Дозорный" for role in roles):
            role_to_check = "duty_guard"
        elif any(role.name == "Пират" for role in roles):
            role_to_check = "pirate"

        # Если такая роль есть, то назначаем роль по уровню
        if role_to_check:
            role_for_level = role_assignments.get(role_to_check, {}).get(new_level)
            if role_for_level:
                role = disnake.utils.get(message.guild.roles, name=role_for_level)
                if role:
                    await message.author.add_roles(role)
                    await message.channel.send(f"{message.author.mention} получил роль: {role_for_level}.")

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
        xp_for_level = level ** 3
        user_data[user.id]["level"] = level
        user_data[user.id]["xp"] = xp_for_level
    elif xp is not None:
        user_data[user.id]["xp"] = xp
        user_data[user.id]["level"] = calculate_level(xp)

    new_level = user_data[user.id]["level"]
    new_xp = user_data[user.id]["xp"]

    await inter.response.send_message(
        f"Уровень и опыт {user.mention} обновлены: Уровень — {new_level}, XP — {new_xp}."
    )

    roles = user.roles
    role_to_check = None

    if any(role.name == "Дозорный" for role in roles):
        role_to_check = "duty_guard"
    elif any(role.name == "Пират" for role in roles):
        role_to_check = "pirate"
    else:
        inter.channel.send(f"{user.mention} нету ролей.")

    if role_to_check:
        role_for_level = role_assignments.get(role_to_check, {}).get(new_level)
        if role_for_level:
            role = disnake.utils.get(inter.guild.roles, name=role_for_level)
            if role and role not in roles:
                await user.add_roles(role)
                await inter.channel.send(f"{user.mention} получил роль: {role_for_level}.")
            else:
                await inter.channel.send(f"{user.mention} уже имеет роль: {role_for_level}.")

@bot.slash_command(description="Редактирует привязку ролей к уровням")
@commands.has_permissions(administrator=True)
async def set_roles(inter: disnake.ApplicationCommandInteraction, role_category: str, level: int, role_name: str):
    if role_category not in role_assignments:
        role_assignments[role_category] = {}

    role_assignments[role_category][level] = role_name
    await inter.response.send_message(f"Роль для категории {role_category} на уровне {level} обновлена на {role_name}.")

@bot.slash_command(description="Отправляет приветственное сообщение")
async def hello(inter: disnake.ApplicationCommandInteraction):
    await inter.response.send_message("Привет")

bot.run(TOKEN)