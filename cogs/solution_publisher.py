from collections import namedtuple
from datetime import datetime
from discord.ext.commands import Cog
from discord.ext.tasks import loop
from discord import NotFound
from requests import get

# a cog that handles grabbing solution data from the website and posting it to the solutions channel
class SolutionPublisher(Cog):
    def __init__(self, client):
        self.client = client # pointer to the bot object
        self.channel = None  # which channel to send the solution messages to
        self.last_called = datetime.utcnow().isoformat() # time elapsed since the last get request
        self.Solution = namedtuple("solution", "username problem_title problem_id code") # tuple containing all relevent parsed solution data

    # cleanup
    def cog_unload(self):
        self.publish_solutions.cancel()

    # async function that queries the website's api for any successful solutions submitted since the last iteration of the event loop
    async def parse_get(self):
        data = get('https://api.meters.sh/submissions/new-completions', params = {'since': self.last_called}).json()
        self.last_called = datetime.utcnow().isoformat()
        for item in data:
            problem_data = get(f"https://api.meters.sh/problems/{item['problem_id']}").json()
            user_data = get(f"https://api.meters.sh/user/id/{item['user_id']}").json()

            # it is possible, though unlikely, that the submitter is not a member of the discord server, in which case we default to their website username
            username = user_data['username']
            try:
                username = (await self.client.fetch_user(int(user_data['discord_id']))).mention
            except NotFound as e:
                print(f"WARN: function 'parse_get' raised: {e}\n(this probably just means someone submitted a succesful solution who is not in the discord server)")
            yield self.Solution(username, problem_data['title'], problem_data['id'], item['code'])
    
    # async function that takes a parsed solution and sends a message in the solutions channel with the username of the submitter and the name of the problem they solved
    # followed by as many messages of code as are required to send the whole solution given Discord's 2000 character message limit
    async def print_solution(self, solution):
        await self.channel.send(f"{solution.username} has successfully completed {solution.problem_title} (https://chicoacm.org/problems/{solution.problem_id}) with the following solution:")
        solution_code = solution.code.split('\n') # the translate sanatizes any triple backticks in the original code which would mess up the code formatting
        code_messages = []
        cur_message = "```cpp\n"
        msg_length = 7 # formatting characters such as the ```cpp and \n are counted in Discord's message limit so we have to take them into account
        for line in solution_code:
            if(len(line) + 11 >= 2000): # the message must be 2000 characters including the 11 minimum formatting characters
                code_messages = [f"`Can't display solution in a coherent manner (line {solution_code.index(line) + 1} alone goes over the Discord message character limit)`"]
                break
            if(msg_length + len(line) + 3 >= 2000): # at this point the first 8 required formatting characters are already accounted for, so we only need to add 3 more
                code_messages.append(f"{cur_message}```")
                msg_length = len(line) + 8 # 8 required formatting characters in addition to line length
                cur_message = f"```cpp\n{line}\n"
            else:
                msg_length += len(line) + 1 # line length plus the newline character
                cur_message += f"{line}\n"
        else:
            code_messages.append(f"{cur_message}```")
        for message in code_messages:
            await self.channel.send(message)

    # async function that gets all the successful solutions since it was last called and submits each to self.channel, called once every three seconds
    @loop(seconds=3.0)
    async def publish_solutions(self):
            async for solution in self.parse_get():
                await self.print_solution(solution)

    # find the solutions channel and start the publish_solutions coroutine
    @Cog.listener()
    async def on_ready(self):
        for channel in self.client.guilds[0].text_channels:
            if(channel.name == 'solutions'):
                self.channel = channel
                break
        self.publish_solutions.start()

# loads the cog
def setup(client):
    client.add_cog(SolutionPublisher(client))
