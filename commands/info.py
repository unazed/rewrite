import discord
import time
import psutil  # System info
from discord.ext import commands

from core.bot import Bot


class Info:
    def __init__(self, bot):
        self.bot = bot # flamekong was here xdddddddddddddd
        self.process = psutil.Process()  # Later for RAM usage

    @commands.command()
    async def ping(self, ctx):
        t1 = time.perf_counter()
        await ctx.channel.trigger_typing()
        t2 = time.perf_counter()
        # Singles quotes to match my relationship status
        fmt = '\U0001f3d3 **Pong!** `{}ms`'.format(str(round((t2 - t1) * 100)))
        # An embed for 7 letters, yes
        em = discord.Embed(description=fmt, color=Bot.COLOR)
        await ctx.send(embed=em)

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(title="Himebot - The only music bot you'll ever need",
                              description="For extra support, join [Hime's support server](https://discord.gg/BCAF7rH)",
                              colour=Bot.COLOR)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(name="Commands",
                        value="Hime's complete commands list could be"
                              " found over at [Hime's website](https://himebot.xyz/features_and_commands.html)")
        embed.add_field(name="Getting Started",
                        value="To get started using the Hime, join a voice channel and then use the play command: `.pl"
                              "ay [song name]`the bot will then join the channel and play the requested song!")
        embed.set_footer(text=f"Created by init0#8366, flamekong#0009 & repyh#2900 using discord.py")
        await ctx.send(embed=embed)

    @commands.command(aliases=["botinfo", "stats"])
    async def info(self, ctx):
        embed = discord.Embed(title="Himebot - Statistics", colour=Bot.COLOR)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(name="Playing on", value=f"{1} servers", inline=True)  # placeholder
        embed.add_field(name="Server Count", value=f"{len(self.bot.guilds)}", inline=True)
        embed.add_field(name="User Count", value=f"{len(self.bot.users)}", inline=True)
        embed.add_field(name="Uptime", value="placeholder", inline=True)  # Do this later
        embed.add_field(name="CPU Usage", value=f"{psutil.cpu_percent()}%", inline=True)
        embed.add_field(name="Memory Used", value="placeholder", inline=True)  # psutil
        embed.add_field(name="Total Memory", value="placeholder", inline=True)  # psutil
        embed.add_field(name="Shard", value="placeholder", inline=True)
        await ctx.send(embed=embed)

    @commands.command(aliases=["invite"])
    async def links(self, ctx):
        e = discord.Embed(description=
                          ("[Add to your server](https://discordapp.com/oauth2/authorize"
                           "?client_id=232916519594491906&scope=bot&permissions=40)\n"
                           "[Join Hime's server](https://discord.gg/tfAMfX4)\n"
                           "[Hime's Website](https://himebot.xyz/)\n"
                           "[Hime's Patreon](https://www.patreon.com/himebot)"),
                          colour=Bot.COLOR)
        e.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Info(bot))
