from discord.ext.commands import Bot
from discord import Intents
from os import chdir, listdir, getenv
from os.path import dirname, abspath

# entry point of program
if(__name__ == "__main__"):
    client = Bot(command_prefix = '!', intents = Intents.default())

    # loads cogs
    chdir(dirname(abspath(__file__)))
    for filename in listdir('./cogs'):
        if filename.endswith('.py'):
            client.load_extension(f'cogs.{filename[:-3]}')

    client.run(getenv('ACMBOT_API_KEY'))