import disnake
from disnake.ext import commands

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help', help='Выводит справочную информацию о командах бота')
    async def help(self, ctx):
        embed = disnake.Embed(
            title="Справка по командам бота",
            description="Ниже перечислены команды, доступные для использования. Команды разделены по категориям:",
            color=disnake.Color.blue()
        )

        embed.set_thumbnail(url=self.bot.user.avatar.url)

        embed.add_field(
            name="HelpCommand",
            value=(
                "`sl.help` - Выводит справочную информацию о командах бота.\n"
            ),
            inline=False
        )

        embed.add_field(
            name="Leveling",
            value=(
                "`sl.set_channel` - Настроить канал для отправки сообщений о достижении уровня.\n"
                "`sl.set_exp_range` - Настроить диапазон получения опыта. Только для администраторов.\n"
            ),
            inline=False
        )

        embed.add_field(
            name="RoleManagement",
            value=(
                "`sl.edit_rank` - Изменить уровень и опыт пользователя, обновить привязанные роли.\n"
                "`sl.set_roles` - Привязать роли, выдаваемые при достижении уровня.\n"
                "`sl.show_roles` - Показать список ролей и уровней в виде таблицы.\n"
            ),
            inline=False
        )

        embed.set_footer(
            text="Для получения дополнительной информации обратитесь к администратору."
        )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(HelpCommand(bot))