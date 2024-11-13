import disnake
from disnake.ext import commands
import random
import os
from config import user_data, exp_range, calculate_level


class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Загружаем данные о пользователях из файла при старте бота
        self.load_user_data()

    def save_user_data(self):
        with open("lvl.txt", "w", encoding="utf-8") as file:
            for user_id, data in user_data.items():
                file.write(f"{user_id}:{data['level']}:{data['xp']}\n")

    def load_user_data(self):
        if os.path.exists("lvl.txt"):
            with open("lvl.txt", "r", encoding="utf-8") as file:
                for line in file:
                    parts = line.strip().split(":")
                    if len(parts) == 3:
                        user_id, level, xp = parts
                        user_data[int(user_id)] = {"level": int(level), "xp": int(xp)}

    @commands.Cog.listener()
    async def on_message(self, message):
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

        # Сохраняем данные после каждого изменения
        self.save_user_data()

    @commands.slash_command(description="Показывает ваш уровень и XP")
    async def rank(self, inter: disnake.ApplicationCommandInteraction):
        user_id = inter.author.id
        if user_id in user_data:
            level = user_data[user_id]["level"]
            xp = user_data[user_id]["xp"]
            await inter.response.send_message(f"{inter.author.mention}, ваш уровень: {level}, XP: {xp}")
        else:
            await inter.response.send_message(f"{inter.author.mention}, у вас пока нет XP. Начните писать сообщения, чтобы зарабатывать XP!")

    @commands.slash_command(description="Настраивает диапазон случайного получения опыта за сообщения")
    @commands.has_permissions(administrator=True)
    async def set_exp_range(self, inter: disnake.ApplicationCommandInteraction, min_exp: int, max_exp: int):
        if min_exp < 0 or max_exp < 0:
            await inter.response.send_message("Минимальный и максимальный опыт не могут быть отрицательными числами.", ephemeral=True)
            return

        if min_exp > max_exp:
            await inter.response.send_message("Минимальное значение опыта не может быть больше максимального.", ephemeral=True)
            return

        exp_range["min"] = min_exp
        exp_range["max"] = max_exp
        await inter.response.send_message(f"Диапазон получения опыта установлен: от {min_exp} до {max_exp} за сообщение.")

    def cog_unload(self):
        self.save_user_data()


def setup(bot):
    bot.add_cog(Leveling(bot))