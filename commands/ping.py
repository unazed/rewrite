from discord.ext import commands
import functools


class PingCommand:
    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong!")

def setup(bot):
    bot.add_cog(PingCommand())
