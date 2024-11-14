import disnake
from disnake.ext import commands
import random
from config import user_data, exp_range, calculate_level

class XPManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
            await message.channel.send(level_up_message)

    @commands.command(name="leaderboard", description="Показывает топ-10 пользователей по опыту")
    async def leaderboard(self, ctx):
        if not user_data:
            await ctx.send("📉 На данный момент нет пользователей с накопленным опытом.")
            return

        sorted_users = sorted(user_data.items(), key=lambda x: x[1]['xp'], reverse=True)
        embed = disnake.Embed(
            title="🏆 Таблица Лидеров по Опыту",
            description="Топ-10 пользователей с наибольшим количеством опыта!",
            color=disnake.Color.gold()
        )

        for rank, (user_id, data) in enumerate(sorted_users[:10], start=1):
            member = ctx.guild.get_member(user_id)
            if member:
                embed.add_field(
                    name=f"{rank}. {member.display_name}",
                    value=f"**Уровень:** {data['level']} | **Опыт (XP):** {data['xp']}",
                    inline=False
                )
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(XPManagement(bot))