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
        # loads cogs (needs to be in order since they depend on each other, probably bad architecture but whatever)
        chdir(dirname(abspath(__file__)))
        await client.load_extension(f'cogs.shared_utils')
        await client.load_extension(f'cogs.problem_publisher')
        await client.load_extension(f'cogs.solution_publisher')
        await client.load_extension(f'cogs.ws_listener')
        
        setup_logging(level=logging.INFO)
        await client.start(getenv('ACMBOT_API_KEY'))

if(__name__ == "__main__"):
    run(main())
