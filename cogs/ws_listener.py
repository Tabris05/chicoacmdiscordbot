from discord.ext.commands import Cog
from discord.ext.tasks import loop
from websockets import connect, ConnectionClosed
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
        try:
            async with connect('ws://api.meters.sh/ws') as ws:
                for key, value in loads(await ws.recv()).items():
                    if(key == "NewCompletion" or key == "NewStar"):
                        await self.client.get_cog("SolutionPublisher").publish_solution(value)
        except ConnectionClosed as e:
            print(f"WARN: function 'listen' raised: {e}\n(this means the connection to the websocket server is unstable)")

    # cleanup
    def cog_unload(self):
        self.listen.cancel()


# loads the cog
def setup(client):
    client.add_cog(WebsocketListener(client))