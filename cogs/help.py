import disnake
from disnake.ext import commands

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='bothelp', help='Выводит справочную информацию о командах бота')
    async def help(self, ctx):
        embed = disnake.Embed(
            title="Справка по командам бота",
            description="Вот список доступных команд, которые вы можете использовать:",
            color=disnake.Color.blue()
        )

        embed.add_field(name="!help", value="Выводит список всех команд бота", inline=False)
        embed.add_field(name="!set_channel", value="Настроить канал для сообщений о достижении уровня", inline=False)
        embed.add_field(name="!set_channel #канал", value="Укажите текстовый канал для сообщений о достижении уровня", inline=False)

        embed.set_footer(text="Для более подробной информации воспользуйтесь документацией бота или напишите админу.")

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(HelpCommand(bot))