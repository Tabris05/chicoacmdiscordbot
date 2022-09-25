from collections import namedtuple
from discord.ext.commands import Cog
from discord import NotFound
from requests import get

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

    # formats the solution code with Discord markdown and breaks it up into 2000 character or less chunks to comply with Discord's message limit
    def format_code(self, solution_code):
        solution_code = solution_code.replace("```", "").split('\n') # the replace sanatizes any triple backticks in the original code which would mess up the code formatting
        code_messages = []
        cur_message = "```cpp\n"
        msg_length = 11 # formatting characters such as the ```cpp and \n are counted in Discord's message limit so we have to take them into account
        for line in solution_code:
            if(len(line) + 11 >= 2000): # the message must be 2000 characters including the 11 minimum formatting characters
                code_messages = [f"`Can't display solution in a coherent manner (line {solution_code.index(line) + 1} alone goes over the Discord message character limit)`"]
                break
            if(msg_length + len(line) >= 2000):
                code_messages.append(f"{cur_message}```")
                msg_length = len(line) + 11 # 11 required formatting characters in addition to line length
                cur_message = f"```cpp\n{line}\n"
            else:
                msg_length += len(line) + 1 # line length plus the newline character
                cur_message += f"{line}\n"
        else:
            code_messages.append(f"{cur_message}```")
        return code_messages


    # parses solution json data and publishes it to the solutions channel
    async def publish_solution(self, solution):
        thread = await self.find_thread(solution['problem_id'])
        user_data = get(f"https://api.meters.sh/user/id/{solution['user_id']}").json()
        username = (await self.client.fetch_user(int(user_data['discord_id']))).mention
        code_messages = self.format_code(solution['code'])
        await thread.send(f"Submission by {username} (ran in {solution['runtime']}ms)")
        for message in code_messages:
            await thread.send(message)

# loads the cog
async def setup(client):
    await client.add_cog(SolutionPublisher(client))