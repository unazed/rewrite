import inspect
import io
import textwrap
import traceback
from contextlib import redirect_stdout

from discord.ext import commands

from utils.visual import SUCCESS
from utils.misc import cleanup_code, get_syntax_error


class Eval:

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()

    @commands.command(aliases=["e"])
    @commands.is_owner()
    async def eval(self, ctx, *, body: str):
        env = {
            "bot": self.bot,
            "phm": self.bot.player_handler_manager,
            "lava": self.bot.lavalink,
            "ctx": ctx,
            "ch": ctx.channel,
            "author": ctx.author,
            "srv": ctx.guild,
            "msg": ctx.message,
            "_": self._last_result,
        }
        env.update(globals())
        body = cleanup_code(body)
        stdout = io.StringIO()
        executor = eval
        try:
            code = compile(body, "<debug session>", "eval")
        except SyntaxError:
            executor = exec
            try:
                code = compile(body, '<repl session>', 'exec')
            except SyntaxError as e:
                await ctx.send(get_syntax_error(e))
                return
        try:
            with redirect_stdout(stdout):
                result = executor(code, env)
                if inspect.isawaitable(result):
                    result = await result
                self._last_result = result
        except:
            value = stdout.getvalue()
            await ctx.send("```py\n{}{}\n```".format(value, traceback.format_exc()))
            return
        await ctx.send(f"```py\n{result}\n```")


def setup(bot):
    bot.add_cog(Eval(bot))
