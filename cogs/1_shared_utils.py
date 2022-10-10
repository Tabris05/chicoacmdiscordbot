from discord.ext.commands import Cog

# a cog that contains member variabls and functions that are useful to multiple other cogs
class SharedUtils(Cog):
    def __init__(self, client):
        self.client = client # reference to the bot object
        self.problems_forum = None # reference to the channel object for the problems forum
    
    # finds the problems forum channel and stores it as a member variable
    @Cog.listener()
    async def on_ready(self):
        for channel in self.client.guilds[0].channels:
            if(channel.name == 'problems'):
                self.problems_forum = channel
                break
    
    # returns a list of all active and inactive threads in the problems forum channel
    async def get_all_problem_threads(self):
        return self.problems_forum.threads + [thread async for thread in self.problems_forum.archived_threads()]

# loads the cog
async def setup(client):
    await client.add_cog(SharedUtils(client))