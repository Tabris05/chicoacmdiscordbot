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