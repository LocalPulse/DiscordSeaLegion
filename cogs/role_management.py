import disnake
from disnake.ext import commands
from config import user_data, role_assignments, calculate_level


class RoleManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Изменяет уровень и опыт пользователя")
    @commands.has_permissions(administrator=True)
    async def edit_rank(self, inter: disnake.ApplicationCommandInteraction, user: disnake.Member, level: int = None, xp: int = None):
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

        roles = user.roles
        role_to_check = None

        if any(role.name == "Дозорный" for role in roles):
            role_to_check = "duty_guard"
        elif any(role.name == "Пират" for role in roles):
            role_to_check = "pirate"
        else:
            await inter.channel.send(f"{user.mention} нету ролей.")

        if role_to_check:
            await inter.channel.send("1")
            role_for_level = role_assignments.get(role_to_check, {}).get(new_level)
            if role_for_level:
                await inter.channel.send("2")
                role = disnake.utils.get(inter.guild.roles, name=role_for_level)
                if role and role not in roles:
                    await user.add_roles(role)
                    await inter.channel.send(f"{user.mention} получил роль: {role_for_level}.")
                else:
                    await inter.channel.send(f"{user.mention} уже имеет роль: {role_for_level}.")

        await inter.response.send_message(f"Уровень и опыт {user.mention} обновлены: Уровень — {new_level}, XP — {new_xp}.")

    @commands.slash_command(description="Редактирует привязку ролей к уровням")
    @commands.has_permissions(administrator=True)
    async def set_roles(self, inter: disnake.ApplicationCommandInteraction, role_category: str, level: int, role_name: str):
        if role_category not in role_assignments:
            role_assignments[role_category] = {}

        role_assignments[role_category][level] = role_name
        await inter.response.send_message(f"Роль для категории {role_category} на уровне {level} обновлена на {role_name}.")

def setup(bot):
    bot.add_cog(RoleManagement(bot))