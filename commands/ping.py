from discord.ext import commands


class PingCommand:

    @commands.command()
    async def ping(self, ctx):
        print(ctx)
        await ctx.send("Pong!")


def setup(bot):
    bot.add_cog(PingCommand())
