import core
import requests

class ToolTests(core.tool.Tool):
    name = "tests"

    async def hug(self, target: str):
        """
        hugs the user
        Args:
            target: the target of the hug
        """
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
        return requests.get(url).text
