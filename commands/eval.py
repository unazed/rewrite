import inspect
import io
import traceback
from contextlib import redirect_stdout

from discord.ext import commands

from utils.DB import SettingsDB
from utils.misc import (cleanup_code, get_syntax_error)


class Eval(object):
    def __init__(self, bot):
        self.bot = bot
        self.context = {"bot": self.bot, "db": SettingsDB.get_instance()}
        self.last_result = None
    
    @commands.command(aliases=["e"])
    @commands.is_owner()
    async def eval(self, ctx, *, code: str):
        code = cleanup_code(code)
        stdout = io.StringIO()
        result = ""

        self.context.update({
            "self": ctx.guild.me,
            "ctx": ctx,
            "ch": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
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
        
        await ctx.send(f"```py\n{str(result)[:1990]}\n```")


def setup(bot):
    bot.add_cog(Eval(bot))
