from discord.ext.commands import Bot
from discord import Intents
from os import chdir, listdir, getenv
from os.path import dirname, abspath
from asyncio import run


client = Bot(command_prefix = '!', intents = Intents.default())

# Find the problems forum and store it as a member variable
@client.event
async def on_ready():
    for channel in client.guilds[0].channels:
        if(channel.name == 'problems'):
            client.problems_forum = channel
            break

# async generator that yields all active and inactive threads in the problems forum
async def get_all_problem_threads():
    for thread in (client.problems_forum.threads + [thread async for thread in client.problems_forum.archived_threads()]):
        yield thread
client.get_all_problem_threads = get_all_problem_threads

# entry point of program
async def main():
    # loads cogs
    chdir(dirname(abspath(__file__)))
    for filename in listdir('./cogs'):
        if filename.endswith('.py'):
            await client.load_extension(f'cogs.{filename[:-3]}')
    await client.start(getenv('ACMBOT_API_KEY'))

if(__name__ == "__main__"):
    run(main())