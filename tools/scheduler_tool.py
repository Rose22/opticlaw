import datetime
import asyncio
import core

class ToolScheduler(core.tool.Tool):
    async def add_scheduled_item(self, title: str, instructions_to_ai: str, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0, recurring: bool = False):
        """
        adds a scheduled job to the scheduler. it will execute at a time from now in days, hours, minutes and seconds.

        example:
            minutes: 1
            instructions_to_ai: "i have to remind user to drink water now"
        """
        async def scheduled_event(instructions: str):
            try:
                message = await self.channel.send("system", f"This is a scheduled event! Please follow these instructions:\n{instructions_to_ai}", use_context=False, use_tools=True)
            except Exception as e:
                return await self.channel.announce(f"error: {e}")

            await self.channel.announce(message)

        try:
            self.manager.scheduler.add(title, scheduled_event, func_args=(instructions_to_ai,), days=days, hours=hours, minutes=minutes, seconds=seconds, repeat=recurring)
            print("reminder set.")
        except Exception as e:
            core.log("error", e)
        return True
