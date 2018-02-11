from discord.ext import commands
import time

class PingCommand:

    @commands.command()
    async def ping(self, ctx):
        t1 = time.perf_counter()
        await ctx.channel.trigger_typing()
        t2 = time.perf_counter()
        # Singles quotes to match my relationship status
        fmt = '\U0001f3d3 **Pong!** `{}ms`'.format(str(round((t2 - t1) * 100)))
        # An embed for 7 letters, yes
        em = discord.Embed(description=fmt,
                            color=0xff3f3f)
        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(PingCommand())
