from contextlib import redirect_stdout
from discord.ext import commands
from utils.misc import (cleanup_code, get_syntax_error)
import inspect
import io
import traceback


class Eval(object):
    def __init__(self, bot):
        self.bot = bot
        self.context = { "bot": self.bot, "phm": self.bot.player_handler_manager, "lava": self.bot.lavalink }
        self.last_result = None
    
    @commands.command(aliases=["e"])
    @commands.is_owner()
    async def eval(self, ctx, *, code: str):
        code = cleanup_code(code)
        stdout = io.StringIO()
        result = ""

        self.context.update({
            "ctx": ctx,
            "ch": ctx.channel,
            "author": ctx.author,
            "srv": ctx.guild,
            "msg": ctx.message,
            "_": self.last_result
        })

        try:
            with redirect_stdout(stdout):
                for executor in (eval, exec):
                    try:
                        result = executor(code, self.context)
                        if inspect.isawaitable(result):
                            result = await result
                        break
                    except SyntaxError as e:
                        result = get_syntax_error(e)
        except:
            result = stdout.getvalue() + traceback.format_exc()
        finally:
            if not result:
                result = stdout.getvalue()
            
            self.last_result = result
        
        await ctx.send(f"```py\n{result}\n```")


def setup(bot):
    bot.add_cog(Eval(bot))
