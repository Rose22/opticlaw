import datetime
import asyncio
import core

async def schedule_callback(tool, instructions: str):
    try:
        # remove scheduler tool from the available tools so that it doesn't add another event
        tools = tool.manager.tools.copy()
        for index, tool_obj in enumerate(tools):
            if tool_obj.get("function", {}).get("name") == "add_job":
                del(tools[index])

        message = await tool.channel.send("system", f"# An event has triggered!\nPlease follow these instructions:\n{instructions}\nUse tools if needed. For simple reminders, do not use tools.", use_context=False, use_tools=True, tools=tools)
    except Exception as e:
        return await tool.channel.announce(f"error: {e}")

    await tool.channel.announce(message)

class SchedulerTool(core.tool.Tool):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._schedule = core.storage.Storage("schedule")

        # load from stored schedule
        if self._schedule:
            for item in self._schedule:
                self.manager.scheduler.add(schedule_callback, func_args=(self, item.get("instructions_to_ai")), days=item.get("days"), hours=item.get("hours"), minutes=item.get("minutes"), seconds=item.get("seconds"), repeat=item.get("recurring"))

    async def add_job(self, action: str, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0, recurring: bool = False):
        """
        Adds a scheduled job to the scheduler. It will trigger at a time from now in days, hours, minutes and seconds.
        NEVER add a job more than once!

        Args:
            action: what to do once the event triggers. ALWAYS use the word "user" to refer to the user.
            days: days from now that the event should trigger
            hours: hours from now that the event should trigger
            minutes: minutes from now that the event should trigger
            seconds: seconds from now that the event should trigger
        """

        try:
            self.manager.scheduler.add(schedule_callback, func_args=(self, action), days=days, hours=hours, minutes=minutes, seconds=seconds, repeat=recurring)
        except Exception as e:
            core.log("error", e)
        return self.result("job successfully added!")
