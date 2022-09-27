from discord.ext.commands import Cog
from discord import Embed
from requests import get
from datetime import datetime

# a cog that publishes newly posted solution data from the websocket listener to the appropriate forum thread
class SolutionPublisher(Cog):
    def __init__(self, client):
        self.client = client # reference to the bot object
        self.forum = None  # forum with threads for every problem on the site
    
    # finds the problems forum
    @Cog.listener()
    async def on_ready(self):
        for forum in self.client.guilds[0].channels:
            if(forum.name == 'problems'):
                self.forum = forum
                break

    # finds the forum thread that corresponds to the problem data passed in
    async def find_thread(self, problem_id):
        problem_data = get(f"https://api.meters.sh/problems/{problem_id}").json()
        for thread in self.forum.threads:
            if(thread.name == problem_data['title']):
                return thread

    # parses solution json data and publishes it to the solutions channel
    async def publish_solution(self, solution):
        thread = await self.find_thread(solution['problem_id'])
        user_data = get(f"https://api.meters.sh/user/id/{solution['user_id']}").json()
        username = (await self.client.fetch_user(int(user_data['discord_id']))).mention
        code = f"```cpp\n{solution['code'].replace('```', '')}```"
        code = code if len(code) <= 4096 else "`Solution length exceeds Discord message limit`"
        submission_time = datetime.fromisoformat(f"{solution['time']}+00:00")
        message = Embed(title = "Solution", description = code, timestamp = submission_time)
        message.add_field(name = "Runtime", value = f"{solution['runtime']}ms")
        message.add_field(name = "Submitted by", value = username)
        await thread.send(embed = message)

# loads the cog
async def setup(client):
    await client.add_cog(SolutionPublisher(client))