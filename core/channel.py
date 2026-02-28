import core

class Channel:
    """Base class for channels"""

    def __init__(self, manager):
        self.name = self.__class__.__name__
        self.manager = manager

    async def send(self, role: str, message: str, **kwargs):
        """sends a message to the AI from within the current channel"""
        response = self.manager.AI.send(role, message, stream=False, **kwargs)
        return await self.manager.AI.recv(response, self, **kwargs)

    async def send_stream(self, role: str, message: str, **kwargs):
        """sends a message to the AI from within the current channel, streaming version"""
        response = self.manager.AI.send(role, message, stream=True, **kwargs)
        async for token in self.manager.AI.recv_stream(response, self, **kwargs):
            yield token

    async def announce(self, message: str):
        """called externally to announce things in this channel, such as a reminder sent by the AI"""
        raise NotImplementedError
