import disnake
from disnake.ext import commands
from config import user_data, calculate_level
from utils import load_roles, save_roles


class RoleManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.role_assignments = load_roles()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_roles(self, ctx, check_role_id: int, level: int, assign_role_id: int):
        """
        Настраивает привязку роли, которая будет выдаваться при достижении определенного уровня,
        если у пользователя есть определенная роль.
        :param check_role_id: ID роли, наличие которой проверяется.
        :param level: Уровень, при достижении которого выдается новая роль.
        :param assign_role_id: ID роли, которую нужно выдать.
        """

        # Если роли нет в конфигурации, создаем новую запись
        if str(check_role_id) not in self.role_assignments:
            self.role_assignments[str(check_role_id)] = {}

        # Привязываем роль к уровню
        self.role_assignments[str(check_role_id)][str(level)] = str(assign_role_id)
        save_roles(self.role_assignments)

        await ctx.send(
            f"Настроена выдача роли с ID {assign_role_id} при наличии роли {check_role_id} и достижении уровня {level}.")

    @commands.command()
    async def edit_rank(self, ctx, user: disnake.Member, level: int = None, xp: int = None):
        """Команда для изменения уровня и опыта пользователя"""
        # Проверка и обновление данных пользователя
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

        # Проверка и выдача новой роли на основе привязок
        user_roles = [role.id for role in user.roles]
        assigned_role = None

        for check_role_id, levels in self.role_assignments.items():
            if int(check_role_id) in user_roles:  # Проверка на наличие нужной роли
                assign_role_id = levels.get(str(new_level))
                if assign_role_id:
                    role = disnake.utils.get(ctx.guild.roles, id=int(assign_role_id))
                    if role and role not in user.roles:
                        await user.add_roles(role)
                        assigned_role = role
                        await ctx.send(f"{user.mention} получил роль: {role.name}.")

        if not assigned_role:
            await ctx.send(f"Для {user.mention} не найдено подходящей роли на уровне {new_level}.")

        await ctx.send(f"Уровень и опыт {user.mention} обновлены: Уровень — {new_level}, XP — {new_xp}.")


def setup(bot):
    bot.add_cog(RoleManagement(bot))