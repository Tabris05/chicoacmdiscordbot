from collections import namedtuple
from discord.ext.commands import Cog
from discord import NotFound
from requests import get

# a cog that publishes newly posted solution data from the websocket listener to the solutions text channel
class SolutionPublisher(Cog):
    def __init__(self, client):
        self.client = client # reference to the bot object
        self.channel = None  # which channel to send the solution messages to
        self.Solution = namedtuple("solution", "username problem_title problem_id code") # tuple containing all relevent parsed solution data
    
    # find the solutions channel
    @Cog.listener()
    async def on_ready(self):
        for channel in self.client.guilds[0].text_channels:
            if(channel.name == 'solutions'):
                self.channel = channel
                break

    # parses solution json data and publishes it to the solutions channel
    async def publish_solution(self, solution):
        parsed_solution = await self.parse_solution(solution)
        await self.print_solution(parsed_solution)

    # extracts relevent information from solution json data and returns it as a tuple
    async def parse_solution(self, solution):
        problem_data = get(f"https://api.meters.sh/problems/{solution['problem_id']}").json()
        user_data = get(f"https://api.meters.sh/user/id/{solution['user_id']}").json()

        # it is possible, though unlikely, that the submitter is not a member of the discord server, in which case we default to their website username
        username = user_data['username']
        try:
            username = (await self.client.fetch_user(int(user_data['discord_id']))).mention
        except NotFound as e:
            print(f"WARN: function 'parse_get' raised: {e}\n(this probably just means someone submitted a succesful solution who is not in the discord server)")
        return self.Solution(username, problem_data['title'], problem_data['id'], solution['code'])
    
    # sends a message containing parsed solution data in the solutions channel
    async def print_solution(self, solution):
        await self.channel.send(f"{solution.username} has successfully completed {solution.problem_title} (https://chicoacm.org/problems/{solution.problem_id}) with the following solution:")
        solution_code = solution.code.replace("```", "").split('\n') # the replace sanatizes any triple backticks in the original code which would mess up the code formatting
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

# loads the cog
def setup(client):
    client.add_cog(SolutionPublisher(client))
