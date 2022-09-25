from discord.ext.commands import Cog
from requests import get

# a cog that creates a thread in the problems forum for each problem on the site
class ProblemPublisher(Cog):
    def __init__(self, client):
        self.client = client # reference to the bot object
        self.forum = None # forum with threads for every problem on the site

    # finds the problems forum and creates threads for any problems that do not have one already
    @Cog.listener()
    async def on_ready(self):
        for forum in self.client.guilds[0].channels:
            if(forum.name == 'problems'):
                self.forum = forum
                break
        thread_dict = {}
        for thread in self.forum.threads:
            thread_dict[thread.name] = True
        for problem in get("https://api.meters.sh/problems").json():
            if(not(thread_dict.get(problem['title'], False))):
                await self.publish_problem(problem)

    
    # creates a thread in the problems forum for the passed in problem
    async def publish_problem(self, problem):
        return (await self.forum.create_thread(name = problem['title'], content = f"https://chicoacm.org/problems/{problem['id']}")).thread

# loads the cog
async def setup(client):
    await client.add_cog(ProblemPublisher(client))
