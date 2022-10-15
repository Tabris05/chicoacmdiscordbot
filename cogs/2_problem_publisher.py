from discord.ext.commands import Cog
from aiohttp import ClientSession

# a cog that creates a thread in the problems forum for each problem on the site
class ProblemPublisher(Cog):
    def __init__(self, client):
        self.client = client # reference to the bot object

    # creates threads for any problem on the site that does not already have one
    @Cog.listener()
    async def on_ready(self):
        thread_dict = {}
        threads = await self.client.get_cog("SharedUtils").get_all_problem_threads()
        for thread in threads:
            thread_dict[thread.name] = True
        async with ClientSession() as s:
            async with s.get("https://api.meters.sh/problems") as r:
                problems = await r.json()
        for problem in problems:
            if(not(thread_dict.get(problem['title'], False))):
                await self.publish_problem(problem)

    # creates a thread in the problems forum for the passed in problem and adds it to the list of threads stored by the bot
    async def publish_problem(self, problem):
        return (await self.client.get_cog("SharedUtils").problems_forum.create_thread(name = problem['title'], content = f"https://chicoacm.org/problems/{problem['id']}")).thread

# loads the cog
async def setup(client):
    await client.add_cog(ProblemPublisher(client))
