import datetime
import asyncio
import core

class Tools(core.tools.Tools):
    async def add_scheduled_item(self, title: str, instructions_to_ai: str, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0, recurring: bool = False):
        """
        adds a scheduled job to the scheduler. it will execute at a time from now in days, hours, minutes and seconds.

        example:
            minutes: 1
            instructions_to_ai: "i have to remind user to drink water now"
        """
        async def scheduled_event(instructions: str):
            try:
                message = await self.manager.AI.recv(
                    self.channel.send("system", f"This is a scheduled event! Please follow these instructions:\n{instructions_to_ai}", add_to_ctx=False, stream=False)
                )
            except Exception as e:
                return await self.channel.announce(f"error: {e}")

            await self.channel.announce(message)

        try:
            self.manager.scheduler.add(title, scheduled_event, func_args=(instructions_to_ai,), days=days, hours=hours, minutes=minutes, seconds=seconds, repeat=recurring)
            print("reminder set.")
        except Exception as e:
            core.log("error", e)
        return True

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
