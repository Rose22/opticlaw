import core

class Channel:
    """example channel class"""
    def __init__(self, manager):
        self.name = self.__class__.__name__
        self.manager = manager

    async def send(self, role: str, message: str):
        """sends a message to the AI from within the current channel"""
        response = self.manager.AI.send(role, message, stream=False)
        return await self.manager.AI.recv(response, self)

    async def send_stream(self, role: str, message: str):
        """sends a message to the AI from within the current channel, streaming version"""
        response = self.manager.AI.send(role, message, stream=True)
        async for token in self.manager.AI.recv_stream(response, self):
            yield token

    async def announce(self, message: str):
        """called externally to announce things in this channel, such as a reminder sent by the AI"""
        raise NotImplementedError
