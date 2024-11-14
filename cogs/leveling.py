import disnake
from disnake.ext import commands
from config import user_data, calculate_level
from utils import load_roles

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.role_assignments = load_roles()

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

    @commands.slash_command(description="Показывает ваш уровень, XP и время в голосе")
    async def rank(self, inter: disnake.ApplicationCommandInteraction):
        user_id = inter.author.id
        user_data_entry = user_data.get(user_id)

        if user_data_entry:
            level = user_data_entry["level"]
            xp = user_data_entry["xp"]
            xp_needed_for_next_level = (level + 1) ** 3
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
            embed.add_field(name="🌟 Всего XP для следующего уровня", value=f"**{xp_needed_for_next_level}**", inline=True)

            await inter.response.send_message(embed=embed)
        else:
            await inter.response.send_message(
                f"{inter.author.mention}, у вас пока нет XP. Начните писать сообщения, чтобы зарабатывать XP!")

def setup(bot):
    bot.add_cog(Leveling(bot))