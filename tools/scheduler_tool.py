import datetime
import asyncio
import core

class ToolScheduler(core.tool.Tool):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schedule = core.storage.Storage("schedule")

    async def add_scheduled_item(self, title: str, instructions_to_ai: str, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0, recurring: bool = False):
        """
        adds a scheduled job to the scheduler. it will execute at a time from now in days, hours, minutes and seconds.

        Args:
            instructions_to_ai: instructions to the AI on what to do when the event triggers. example: "remind user to drink water"
            days: days from now that the event should trigger
            hours: hours from now that the event should trigger
            minutes: minutes from now that the event should trigger
            seconds: seconds from now that the event should trigger
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
