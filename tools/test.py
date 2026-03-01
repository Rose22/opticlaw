import core
import requests

class TestTool(core.tool.Tool):
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
        return self.result(f"{target} hugged")
    async def punch(self, target: str):
        """punches the user"""
        await self.channel.announce("The AI has punched you. Ow!")
        return self.result(f"{target} punched")
    async def fetch_website(self, url: str):
        """fetches a website"""
        await self.channel.announce("fetched website")
        return self.result(requests.get(url).text)
