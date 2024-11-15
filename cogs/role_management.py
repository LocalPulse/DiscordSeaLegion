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
    async def set_roles(self, ctx, check_role_id: int = None, level: int = None, assign_role_id: int = None):
        if not all([check_role_id, level, assign_role_id]):
            await ctx.send(
                "⚠️ **Ошибка:** Все аргументы обязательны. Пожалуйста, используйте команду в формате:\n"
                "`sl.set_roles <ID роли для проверки> <Уровень> <ID выдаваемой роли>`\n\n"
                "**Пример:** `sl.set_roles 1306206217110290485 5 1306207277438472202`"
            )
            return

        if level <= 0:
            await ctx.send("⚠️ **Ошибка:** Уровень должен быть положительным целым числом. Пожалуйста, введите корректный уровень.")
            return

        if str(check_role_id) not in self.role_assignments:
            self.role_assignments[str(check_role_id)] = {}

        self.role_assignments[str(check_role_id)][str(level)] = str(assign_role_id)
        save_roles(self.role_assignments)

        await ctx.send(
            f"✅ **Успешно настроено:** Теперь роль <@&{assign_role_id}> будет выдана при наличии роли <@&{check_role_id}> "
            f"и достижении уровня {level}. \n \n"
            f"🎖️ Для проверки всех ролей напишите команду `sl.show_roles`"
        )

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def edit_rank(self, ctx, user: disnake.Member = None, *, args: str = None):
        """Позволяет администраторам редактировать уровень или XP пользователя."""

        if not user:
            await ctx.send(
                "⚠️ **Ошибка:** Укажите пользователя. Пример команды: `sl.edit_rank @User 10` или `sl.edit_rank @User xp=200`."
            )
            return

        if user.id not in user_data:
            user_data[user.id] = {"xp": 0, "level": 1}

        level = None
        xp = None

        if args:
            arg_parts = args.split()
            for part in arg_parts:
                if part.startswith("xp="):
                    try:
                        xp = int(part.split("=")[1])
                    except ValueError:
                        await ctx.send(f"⚠️ **Ошибка:** Неверное значение для XP: {part.split('=')[1]}.")
                        return
                elif part.isdigit():
                    level = int(part)
                else:
                    await ctx.send(f"⚠️ **Ошибка:** Неверный аргумент: {part}.")
                    return

        if level is not None:
            if level <= 0:
                await ctx.send("⚠️ **Ошибка:** Уровень должен быть положительным целым числом.")
                return
            # Используем куб уровня для плавного увеличения требуемого опыта
            xp_for_level = level ** 3
            user_data[user.id]["level"] = level
            user_data[user.id]["xp"] = xp_for_level
        elif xp is not None:
            if xp < 0:
                await ctx.send("⚠️ **Ошибка:** Опыт должен быть неотрицательным числом.")
                return
            user_data[user.id]["xp"] = xp
            user_data[user.id]["level"] = calculate_level(xp)
        else:
            await ctx.send("⚠️ **Ошибка:** Укажите либо уровень, либо опыт для обновления.")
            return

        new_level = user_data[user.id]["level"]
        new_xp = user_data[user.id]["xp"]

        # Получаем список ролей пользователя
        user_roles = [role.id for role in user.roles]
        assigned_roles = []
        roles_to_remove = []

        # Найдем ближайшую роль ниже или на уровне
        assigned_role = None
        closest_role_id = None
        closest_level = None

        for check_role_id, levels in self.role_assignments.items():
            if int(check_role_id) in user_roles:
                for lvl, assign_role_id in levels.items():
                    lvl = int(lvl)
                    if lvl == new_level:  # Если роль для текущего уровня
                        assigned_role = disnake.utils.get(ctx.guild.roles, id=int(assign_role_id))
                        break
                    elif lvl < new_level:  # Если роль для ближайшего уровня ниже
                        if closest_level is None or lvl > closest_level:
                            closest_level = lvl
                            closest_role_id = assign_role_id

        # Удаление всех ролей ниже уровня
        for check_role_id, levels in self.role_assignments.items():
            if int(check_role_id) in user_roles:
                for lvl, assign_role_id in levels.items():
                    lvl = int(lvl)
                    if lvl < new_level:  # Удаляем роли ниже нового уровня
                        role_to_remove = disnake.utils.get(ctx.guild.roles, id=int(assign_role_id))
                        if role_to_remove and role_to_remove in user.roles:
                            roles_to_remove.append(role_to_remove)

        # Удаляем старые роли, которые ниже или выше нового уровня
        for role in roles_to_remove:
            if role and role in user.roles:
                await user.remove_roles(role)
                await ctx.send(f"❌ Удалена роль: {role.name}")

        # Теперь назначаем роль для текущего уровня или ближайшего
        if assigned_role:
            if assigned_role not in user.roles:
                await user.add_roles(assigned_role)
                await ctx.send(f"✅ {user.mention} получил роль для уровня {new_level}: **{assigned_role.name}**.")
        elif closest_role_id:
            assigned_role = disnake.utils.get(ctx.guild.roles, id=int(closest_role_id))
            if assigned_role and assigned_role not in user.roles:
                await user.add_roles(assigned_role)
                await ctx.send(
                    f"✅ {user.mention} получил роль для ближайшего уровня {closest_level}: **{assigned_role.name}**.")
        else:
            await ctx.send(f"ℹ️ Для {user.mention} не найдено роли для уровня {new_level}.")

        await ctx.send(
            f"📈 **Уровень и опыт обновлены:**\n"
            f"{user.mention} — **Уровень:** {new_level}, **XP:** {new_xp}"
        )

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def show_roles(self, ctx):
        if not self.role_assignments:
            await ctx.send("🎖️ Привязки ролей к уровням не найдены.")
            return

        embed = disnake.Embed(
            title="⚔️ ПРИВЯЗКИ РОЛЕЙ К УРОВНЯМ",
            description="🔹 **Детальная информация по привязке ролей к уровням** 🔹",
            color=disnake.Color.blue()
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)

        for check_role_id, levels in self.role_assignments.items():
            role = disnake.utils.get(ctx.guild.roles, id=int(check_role_id))
            role_name = role.name if role else f"ID: {check_role_id}"

            level_info = ""
            for level, assign_role_id in sorted(levels.items(), key=lambda x: int(x[0])):
                assign_role = disnake.utils.get(ctx.guild.roles, id=int(assign_role_id))
                assign_role_name = assign_role.name if assign_role else f"ID: {assign_role_id}"
                level_info += f" --- **Уровень {level}** → {assign_role_name} *(ID: {assign_role_id})*\n"

            embed.add_field(
                name=f"🎖️ Роль для проверки: **{role_name}** *(ID: {check_role_id})*",
                value=level_info,
                inline=False
            )

        embed.set_footer(text="Привязки ролей к уровням SEA LEGION")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(RoleManagement(bot))