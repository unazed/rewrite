import discord
from discord.ext import commands

class help:
    def __init__(self, bot):
        self.bot = bot
	
@commands.command()
@commands.guild_only()
async def help(self, ctx, command: str = None):
	if command is None:
		owner = await self.bot.get_user_info("205346839082303488") # get init user info for footer etc
		embed=discord.Embed(title="Himebot - The only music bot you'll ever need", description="For extra support, join [Hime's Support Server](http://discord.gg/sw3dCxN)", colour=0xff3f3f)
		embed.set_thumbnail(url=self.bot.user.avatar_url)
		embed.add_field(name='Commands', value="Hime's complete commands list can be found over at [Hime's Website](https://himebot.xyz/)")
		embed.add_field(name='Getting Started', value='To get started using the hime, join a voice channel and then use the play command: \n`.play [Song Name Here]` the bot will join the channel and begin playing!')
		embed.set_footer(text=f"Created by {owner} & flamekong#0009 using discord.py", icon_url=owner.avatar_url)
		await ctx.send(embed=embed)
	else:
		embed=discord.Embed(description="For information on how to use a command, head over to [Hime's Website](https://himebot.xyz/)", colour=0xff3f3f)
		await ctx.send(embed=embed)
		
@commands.command()
@commands.guild_only()
async def info(self, ctx):
	embed=discord.Embed(title="Himebot - Statistics", colour=0xff3f3f)
	embed.set_thumbnail(url=self.bot.user.avatar_url)
	embed.add_field(name='Playing on', value=f"{'placeholder'} servers", inline=True) #placeholder
	embed.add_field(name='Server Count', value=len(self.bot.guilds), inline=True)
	embed.add_field(name='User Count', value=len(self.bot.users), inline=True)
	embed.add_field(name='Uptime', value='placeholder', inline=True) #Do this later
	embed.add_field(name='Memory Used', value='placeholder', inline=True) #psutil
	embed.add_field(name='Total Memory', value='placeholder', inline=True) #psutil
	embed.add_field(name='Shard', value='placeholder', inline=True)
	embed.add_field(name="Users who've used bot", value='placeholder', inline=True)
	await ctx.send(embed=embed)
	
def setup(bot):
    bot.add_cog(help(bot))