import core

class ToolTests(core.tool.Tool):
    async def hug(self, target: str):
        """hugs the user"""
        try:
            await self.channel.announce("The AI has hugged you!")
        except Exception as e:
            core.log("error", e)
        return True
    async def punch(self, target: str):
        """punches the user"""
        await self.channel.announce("The AI has punched you. Ow!")
        return True
    async def fetch_website(self, url: str):
        """fetches a website"""
        await self.channel.announce("fetched website")
        return True
