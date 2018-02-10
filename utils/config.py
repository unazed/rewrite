import json


with open("config.json", "r") as f:
    config = json.load(f)

# default bot settings
defaults = config["defaults"]
default_prefix = defaults["prefix"]

commands_dir = config["commands_dir"]
token = config["token"]
owners = config["owners"]
