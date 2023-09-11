﻿from discord.ext.commands import Cog
from discord import Embed
from aiohttp import ClientSession
from datetime import datetime

# a cog that publishes newly posted solution data from the websocket listener to the appropriate forum thread
class SolutionPublisher(Cog):
    def __init__(self, client):
        self.client = client # reference to the bot object
        self.tc_map = { # maps time complexity enum sent from server to appropriate big O formula
            "CONSTANT": "O(1)", 
            "LOG": "O(log(n))",
            "SQRT": "O(√n)",
            "LINEAR": "O(n)",
            "LOG_LINEAR": "O(nlog(n))",
            "QUADRATIC": "O(n²)",
            "EXPONENTIAL": "O(2ⁿ)"
        }

    # finds the forum thread that corresponds to the problem data passed in
    async def find_thread(self, problem_id):
        async with ClientSession() as s:
            async with s.get(f"https://api.chicoacm.org/problems/{problem_id}") as r:
                problem_data = await r.json()
        threads = await self.client.get_cog("SharedUtils").get_all_problem_threads()
        for thread in threads:
            if(thread.name == problem_data['title']):
                return thread
        else:
            return await self.client.get_cog("ProblemPublisher").publish_problem(problem_data)

    # parses solution json data and publishes it to the solutions channel
    async def publish_solution(self, solution):
        thread = await self.find_thread(solution['problem_id'])
        async with ClientSession() as s:
            async with s.get(f"https://api.chicoacm.org/user/id/{solution['user_id']}") as r:
                user_data = await r.json()
        username = (await self.client.fetch_user(int(user_data['discord_id']))).mention
        code = f"(Click to reveal)\n||```cpp\n{solution['code'].replace('```', '')}```||"
        link = f"\n[**View on website**](https://chicoacm.org/submissions/{solution['id']})"
        code = code if len(code) + len(link) <= 4096 else "`Solution length exceeds Discord message limit`"
        code += link
        submission_time = datetime.fromisoformat(f"{solution['time']}+00:00")
        message = Embed(title = "Solution", description = code, timestamp = submission_time)
        message.add_field(name = "Runtime", value = f"{solution['runtime']} fuel")
        if(solution['complexity']):
            message.add_field(name = "Big O (Estimate)", value = f"*{self.tc_map[solution['complexity']]}*")
        message.add_field(name = "Submitted by", value = username)
        await thread.send(embed = message)

# loads the cog
async def setup(client):
    await client.add_cog(SolutionPublisher(client))