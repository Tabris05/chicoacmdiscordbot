from discord.ext.commands import Bot
from discord.utils import setup_logging
from discord import Intents
from os import chdir, listdir, getenv
from os.path import dirname, abspath
from asyncio import run
from dotenv import load_dotenv
import logging

# entry point of program
async def main():
    load_dotenv()
    async with Bot(command_prefix = '!', intents = Intents.default()) as client:
        # loads cogs
        chdir(dirname(abspath(__file__)))
        await client.load_extension(f'cogs.shared.shared_utils')
        for filename in listdir('./cogs'):
            if filename.endswith('.py'):
                await client.load_extension(f'cogs.{filename[:-3]}')
        setup_logging(level=logging.INFO)
        await client.start(getenv('ACMBOT_API_KEY'))

if(__name__ == "__main__"):
    run(main())
