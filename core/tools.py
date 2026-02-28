class Tools:
    """tools base class"""
    def __init__(self, manager):
        self.channel = None # somehow get current channel
        self.manager = manager

    async def _send_to_channel(self, channel_key: str, message: str):
        if channel_key not in self.manager.channels.keys():
            return False

        return await self.manager.channels.get(channel_key).send(message)

    async def _send_to_all_channels(self, message: str):
        for channel_name, channel in self.manager.channels.items():
            await channel.send(message)
