from discord.ext.commands import Cog
from discord.ext.tasks import loop
from websockets import connect
from json import loads

# a cog that manages a websocket listener and passes off the data it recieves to other cogs for processing
class WebsocketListener(Cog):
    def __init__(self, client):
        self.client = client # reference to the bot object
    
    # adds the websocket listener to the Discord event loop
    @Cog.listener()
    async def on_ready(self):
        value = {'id': 549, 'problem_id': 1, 'user_id': 1, 'success': True, 'runtime': 5020158, 'error': None, 'time': '2022-10-21T09:28:13', 'code': '#include <iostream>\n\nusing namespace std;\n\nvoid fizzBuzz(int n) {\n  for (int i = 1; i <= n; i++) {\n    if (i % 3 == 0&& i % 5 == 0) {\n      cout << "FizzBuzz" << endl;\n    } else if (i % 3 == 0) {\n      cout << "Fizz" << endl;\n    }else if (i % 5 == 0) {\n      cout << "Buzz" << endl;\n    } else {\n      cout << i << endl;\n    }\n  }\n}'}
        await self.client.get_cog("SolutionPublisher").publish_solution(value)
        self.listen.start()
    
    # listens for incoming data from the websocket and hands it off to the appropriate cog
    @loop()
    async def listen(self):
        async with connect('wss://api.chicoacm.org/ws') as ws:
            for key, value in loads(await ws.recv()).items():
                if(key == "NewCompletion" or key == "NewStar"):
                    await self.client.get_cog("SolutionPublisher").publish_solution(value)
                elif(key == "NewProblem"):
                    await self.client.get_cog("ProblemPublisher").publish_problem(value)

    # cleanup
    def cog_unload(self):
        self.listen.cancel()


# loads the cog
async def setup(client):
    await client.add_cog(WebsocketListener(client))