from discord.ext.commands import Cog
from discord.ext.tasks import loop
from websockets import connect
from json import loads
from os import getenv
import logging

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
            async with connect('wss://api.chicoacm.org/ws', extra_headers = {'Cookie': f"token={getenv('ACMBOT_COOKIE_TOKEN')}"}, max_size = 2**128) as ws:
                for key, value in loads(await ws.recv()).items():
                    logging.info(f"received message of type {key}:\n{value}")
                    if(key == "NewCompletion" or key == "NewStar"):
                        await self.client.get_cog("SolutionPublisher").publish_solution(value)
                    elif(key == "NewProblem"):
                        await self.client.get_cog("ProblemPublisher").publish_problem(value)
        except Exception as e:
            logging.error(f"websocket connection threw {type(e).__name__}: {str(e)}")

    # cleanup
    def cog_unload(self):
        self.listen.cancel()


# loads the cog
async def setup(client):
    await client.add_cog(WebsocketListener(client))
