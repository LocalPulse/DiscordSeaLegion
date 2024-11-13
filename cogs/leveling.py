import disnake
from disnake.ext import commands
import random
import os
import json
from config import user_data, exp_range, calculate_level
from utils import load_roles, save_roles

CHANNELS_FILE = "channels.json"
VOICE_TIME_FILE = "voice_time_data.json"

level_up_channels = {}

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.role_assignments = load_roles()
        self.load_user_data()
        self.load_level_up_channels()

    def save_user_data(self):
        with open("lvl.txt", "w", encoding="utf-8") as file:
            for user_id, data in user_data.items():
                file.write(f"{user_id}:{data['level']}:{data['xp']}\n")

    def load_user_data(self):
        """Загружаем данные пользователей из текстового файла."""
        if os.path.exists("lvl.txt"):
            with open("lvl.txt", "r", encoding="utf-8") as file:
                for line in file:
                    parts = line.strip().split(":")
                    if len(parts) == 3:
                        user_id, level, xp = parts
                        user_data[int(user_id)] = {"level": int(level), "xp": int(xp)}

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

    def load_voice_time_data(self):
        if os.path.exists(VOICE_TIME_FILE):
            try:
                with open(VOICE_TIME_FILE, "r", encoding="utf-8") as file:
                    return json.load(file)
            except json.JSONDecodeError:
                print("[ERROR] Ошибка при чтении JSON файла для голосового времени. Используется пустой словарь.")
                return {}
        else:
            print("[INFO] Файл voice_time_data.json не найден. Создается пустой словарь.")
            return {}

    def save_level_up_channels(self):
        try:
            with open(CHANNELS_FILE, "w", encoding="utf-8") as file:
                json.dump(level_up_channels, file, indent=4)
        except Exception as e:
            print(f"[ERROR] Ошибка при сохранении настроек каналов: {e}")

    def assign_role_based_on_level(self, member, new_level):
        user_roles = [role.id for role in member.roles]
        assigned_role = None

        for check_role_id, levels in self.role_assignments.items():
            if int(check_role_id) in user_roles:
                assign_role_id = levels.get(str(new_level))
                if assign_role_id:
                    role = disnake.utils.get(member.guild.roles, id=int(assign_role_id))
                    if role and role not in member.roles:
                        return role
        return None

    async def send_message_to_channel(self, channel, message):
        try:
            await channel.send(message)
        except Exception as e:
            print(f"[ERROR] Ошибка при отправке сообщения: {e}")

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

            level_up_message = f"🎉 {message.author.mention} достиг {new_level} уровня!"
            role = self.assign_role_based_on_level(message.author, new_level)
            if role:
                level_up_message += f"\n💼 {message.author.mention} получил новую роль: **{role.name}**!"
                await message.author.add_roles(role)

            guild_id = message.guild.id
            if guild_id in level_up_channels:
                level_up_channel = self.bot.get_channel(level_up_channels[guild_id])
                if level_up_channel:
                    await self.send_message_to_channel(level_up_channel, level_up_message)
                else:
                    await self.send_message_to_channel(message.channel, level_up_message)
            else:
                await self.send_message_to_channel(message.channel, level_up_message)

        self.save_user_data()

    @commands.slash_command(description="Показывает ваш уровень, XP и время в голосе")
    async def rank(self, inter: disnake.ApplicationCommandInteraction):
        user_id = inter.author.id
        user_data_entry = user_data.get(user_id)

        voice_time_data = self.load_voice_time_data()
        total_voice_time = voice_time_data.get(str(user_id), 0)

        if user_data_entry:
            level = user_data_entry["level"]
            xp = user_data_entry["xp"]
            xp_needed_for_next_level = (level + 1) ** 100
            xp_progress = xp_needed_for_next_level - xp

            embed = disnake.Embed(
                title="🏅 Ваша Статистика Уровня",
                description=f"Здесь отображены ваши текущие достижения, {inter.author.mention}!",
                color=disnake.Color.blue()
            )
            embed.set_thumbnail(url=inter.author.avatar.url)

            embed.add_field(name="📊 Уровень", value=f"**{level}**", inline=True)
            embed.add_field(name="💠 Текущий XP", value=f"**{xp}**", inline=True)
            embed.add_field(name="🔜 XP до следующего уровня", value=f"**{xp_progress}**", inline=True)
            embed.add_field(name="🌟 Всего XP для следующего уровня", value=f"**{xp_needed_for_next_level}**",
                            inline=True)

            hours, minutes = divmod(total_voice_time, 60)
            embed.add_field(name="🕒 Общее время в голосовом канале", value=f"**{hours} ч {minutes} мин**", inline=True)
            embed.add_field(name="🗓️ Присоединился к серверу", value=inter.author.joined_at.strftime("%Y-%m-%d"),
                            inline=True)
            embed.set_footer(text="Продолжайте общаться, чтобы повышать уровень!", icon_url=self.bot.user.avatar.url)

            await inter.response.send_message(embed=embed)

        else:
            await inter.response.send_message(
                f"{inter.author.mention}, у вас пока нет XP. Начните писать сообщения, чтобы зарабатывать XP!")

    @commands.slash_command(description="Показывает топ-10 пользователей по опыту")
    async def leaderboard(self, inter: disnake.ApplicationCommandInteraction):

        if not user_data:
            await inter.response.send_message("📉 На данный момент нет пользователей с накопленным опытом.")
            return

        sorted_users = sorted(user_data.items(), key=lambda x: x[1]['xp'], reverse=True)

        embed = disnake.Embed(
            title="🏆 Таблица Лидеров по Опыту",
            description="Топ-10 пользователей с наибольшим количеством опыта!",
            color=disnake.Color.gold()
        )

        embed.set_thumbnail(url=self.bot.user.avatar.url)

        for rank, (user_id, data) in enumerate(sorted_users[:10], start=1):
            member = inter.guild.get_member(user_id)
            if member:
                embed.add_field(
                    name=f"{rank}. {member.display_name}",
                    value=f"**Уровень:** {data['level']} | **Опыт (XP):** {data['xp']}",
                    inline=False
                )

        await inter.response.send_message(embed=embed)

    @commands.command(name="leaderboard", description="Показывает топ-10 пользователей по опыту")
    async def leaderboard(self, ctx):
        """Показывает топ-10 пользователей по опыту."""

        if not user_data:
            await ctx.send("📉 На данный момент нет пользователей с накопленным опытом.")
            return

        sorted_users = sorted(user_data.items(), key=lambda x: x[1]['xp'], reverse=True)

        embed = disnake.Embed(
            title="🏆 Таблица Лидеров по Опыту",
            description="Топ-10 пользователей с наибольшим количеством опыта!",
            color=disnake.Color.gold()
        )

        embed.set_thumbnail(url=self.bot.user.avatar.url)

        for rank, (user_id, data) in enumerate(sorted_users[:10], start=1):
            member = ctx.guild.get_member(user_id)
            if member:
                embed.add_field(
                    name=f"{rank}. {member.display_name}",
                    value=f"**Уровень:** {data['level']} | **Опыт (XP):** {data['xp']}",
                    inline=False
                )

        await ctx.send(embed=embed)

    @commands.command(name="set_exp_range")
    @commands.has_permissions(administrator=True)
    async def set_exp_range(self, ctx, min_exp: int = None, max_exp: int = None):
        if min_exp is None or max_exp is None:
            await ctx.send(
                "❌ Неправильный ввод команды! Убедитесь, что вы указали оба значения.\n\n"
                "**Правильный формат команды:** `!set_exp_range <min_exp> <max_exp>`\n"
                "🔹 `min_exp` - минимальное значение опыта (целое положительное число)\n"
                "🔹 `max_exp` - максимальное значение опыта (целое положительное число)"
            )
            return

        if min_exp < 0 or max_exp < 0:
            await ctx.send("❌ Минимальный и максимальный опыт не могут быть отрицательными числами.")
            return

        if min_exp > max_exp:
            await ctx.send("❌ Минимальное значение опыта не может быть больше максимального.")
            return

        exp_range["min"] = min_exp
        exp_range["max"] = max_exp
        await ctx.send(f"🔧 Диапазон получения опыта установлен: от {min_exp} до {max_exp} за сообщение.")

    @commands.command(name="set_channel")
    @commands.has_permissions(administrator=True)
    async def set_channel(self, ctx, channel: disnake.TextChannel = None):
        if channel is None:
            await ctx.send(
                "⚠️ Вы не указали канал. Пожалуйста, укажите текстовый канал, где бот будет отправлять сообщения о достижении уровня.\n"
                "Пример использования: `!set_channel #канал`"
            )
            return

        if not isinstance(channel, disnake.TextChannel):
            await ctx.send(
                "️⚠️ Указанный канал не является текстовым каналом. Пожалуйста, укажите текстовый канал.\n"
                "Пример использования: `!set_channel #канал`"
            )
            return

        guild_id = ctx.guild.id
        level_up_channels[guild_id] = channel.id
        self.save_level_up_channels()

        await ctx.send(f"✅ Канал для сообщений уровня на этом сервере установлен: {channel.mention}")


def setup(bot):
    bot.add_cog(Leveling(bot))