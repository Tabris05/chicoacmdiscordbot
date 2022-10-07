from discord.ext.commands import Cog
from aiohttp import ClientSession

# a cog that creates a thread in the problems forum for each problem on the site
class ProblemPublisher(Cog):
    def __init__(self, client):
        self.client = client # reference to the bot object

    # finds the problems forum and creates threads for any problems that do not have one already
    @Cog.listener()
    async def on_ready(self):
        for channel in self.client.guilds[0].channels:
            if(channel.name == 'problems'):
                archived_threads = []
                async for thread in channel.archived_threads():
                    archived_threads.append(thread)
                self.client.problem_threads = channel.threads + archived_threads
                break
        thread_dict = {}
        for thread in self.client.problem_threads:
            thread_dict[thread.name] = True
        async with ClientSession() as s:
            async with s.get("https://api.meters.sh/problems") as r:
                problems = await r.json()
        for problem in problems:
            if(not(thread_dict.get(problem['title'], False))):
                await self.publish_problem(problem)

    # creates a thread in the problems forum for the passed in problem
    async def publish_problem(self, problem):
        return (await self.forum.create_thread(name = problem['title'], content = f"https://chicoacm.org/problems/{problem['id']}")).thread

# loads the cog
async def setup(client):
    await client.add_cog(ProblemPublisher(client))
