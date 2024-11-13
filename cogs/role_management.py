import disnake
from disnake.ext import commands
from config import user_data, calculate_level
from utils import load_roles, save_roles

class RoleManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.role_assignments = load_roles()

    @commands.command(description="Изменяет уровень и опыт пользователя")
    @commands.has_permissions(administrator=True)
    async def edit_rank(self, ctx, user: disnake.Member, level: int = None, xp: int = None):
        """Команда для изменения уровня и XP пользователя"""
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
            await ctx.send(f"{user.mention} не имеет ролей.")

        if role_to_check:
            role_for_level = self.role_assignments.get(role_to_check, {}).get(new_level)

            # Удаляем более высокие уровни ролей, если они есть
            for role in roles:
                if role.name.startswith("Дозорный") or role.name.startswith("Пират"):
                    level_in_role = int(role.name.split()[-1])
                    if level_in_role > new_level:
                        await user.remove_roles(role)
                        await ctx.send(f"{user.mention} потерял роль: {role.name}.")

            if not role_for_level:
                previous_levels = sorted([lvl for lvl in self.role_assignments.get(role_to_check, {}).keys() if lvl < new_level], reverse=True)

                if previous_levels:
                    closest_level = previous_levels[0]
                    role_for_level = self.role_assignments[role_to_check].get(closest_level)

            if role_for_level:
                role = disnake.utils.get(ctx.guild.roles, name=role_for_level)
                if role and role not in roles:
                    await user.add_roles(role)
                    await ctx.send(f"{user.mention} получил роль: {role_for_level}.")
                else:
                    await ctx.send(f"{user.mention} уже имеет роль: {role_for_level}.")

        await ctx.send(f"Уровень и опыт {user.mention} обновлены: Уровень — {new_level}, XP — {new_xp}.")

    @commands.command(description="Редактирует привязку ролей к уровням")
    @commands.has_permissions(administrator=True)
    async def set_roles(self, ctx, role_category: str, level: int, role_name: str):
        """Команда для настройки привязки ролей к уровням"""
        if role_category not in self.role_assignments:
            self.role_assignments[role_category] = {}

        self.role_assignments[role_category][level] = role_name
        save_roles(self.role_assignments)

        await ctx.send(f"Роль для категории {role_category} на уровне {level} обновлена на {role_name}.")

def setup(bot):
    bot.add_cog(RoleManagement(bot))