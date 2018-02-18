from discord.ext.commands import CheckFailure


class CustomCheckFailure(CheckFailure):
    def __init__(self, msg):
        self.msg = msg
