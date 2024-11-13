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
                "`!set_roles <ID роли для проверки> <Уровень> <ID выдаваемой роли>`\n\n"
                "**Пример:** `!set_roles 1306206217110290485 5 1306207277438472202`"
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
            f"🎖️ Для проверки всех ролей напишите команду `!show_roles`"
        )

    @commands.command()
    async def edit_rank(self, ctx, user: disnake.Member = None, level: int = None, xp: int = None):

        # Проверка на наличие обязательного аргумента `user`
        if not user:
            await ctx.send(
                "⚠️ **Ошибка:** Укажите пользователя. Пример команды: `!edit_rank @User 10` или `!edit_rank @User xp=200`.")
            return

        if user.id not in user_data:
            user_data[user.id] = {"xp": 0, "level": 1}

        if level is not None:
            if level <= 0:
                await ctx.send("⚠️ **Ошибка:** Уровень должен быть положительным целым числом.")
                return
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

        user_roles = [role.id for role in user.roles]
        assigned_role = None

        for check_role_id, levels in self.role_assignments.items():
            if int(check_role_id) in user_roles:  # Проверка наличия нужной роли
                assign_role_id = levels.get(str(new_level))
                if assign_role_id:
                    role = disnake.utils.get(ctx.guild.roles, id=int(assign_role_id))
                    if role and role not in user.roles:
                        await user.add_roles(role)
                        assigned_role = role
                        await ctx.send(f"✅ {user.mention} теперь получил роль: **{role.name}** на уровне {new_level}!")

        if not assigned_role:
            await ctx.send(f"ℹ️ Для {user.mention} не найдено подходящей роли на уровне {new_level}.")

        await ctx.send(
            f"📈 **Уровень и опыт обновлены:**\n"
            f"{user.mention} — **Уровень:** {new_level}, **XP:** {new_xp}"
        )

    @commands.command()
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

        # Добавление привязок ролей и уровней с улучшенным оформлением
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