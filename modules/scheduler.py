import datetime
import relative_datetime
import asyncio
import core

async def schedule_callback(module, instructions: str):
    if not module.manager.channel:
        return False

    try:
        # remove scheduler tool from the available tools so that it doesn't add another event
        tools = module.manager.tools.copy()
        for index, tool_obj in enumerate(tools):
            if tool_obj.get("function", {}).get("name") == "add_job":
                del(tools[index])

        message = await module.manager.channel.send("system", f"# An event has triggered!\nPlease follow these instructions:\n{instructions}\nUse tools if needed. For simple reminders, do not use tools.", use_context=False, use_tools=True, tools=tools)
    except Exception as e:
        core.log("scheduler", f"error: {e}")

    await module.manager.channel.announce(message)

class Scheduler(core.module.Module):
    async def on_ready(self):
        self._schedule = core.storage.StorageList("schedule", type="json")

        # load from stored schedule
        if self._schedule:
            for index, item in enumerate(self._schedule):
                self.manager.scheduler.add(schedule_callback, func_args=(self, item.get("action")), days=item.get("days"), hours=item.get("hours"), minutes=item.get("minutes"), seconds=item.get("seconds"), repeat=item.get("recurring"))

    async def on_system_prompt(self):
        if self._schedule:
            return f"Your scheduler system will trigger these events at the specified times:\n{self._get()}"

    def _get(self):
        result = []
        for id, job in enumerate(self._schedule):
            time_due = "every "
            if job.get("recurring"):
                time_due_list = []
                for key in job.keys():
                    if key in ("action", "recurring"):
                        continue
                
                    if int(job[key]) > 0:
                        time_due_list.append(f"{job[key]} {key}")
                time_due += ", ".join(time_due_list)
            else:
                # calculate time until trigger
                time_until_trigger = datetime.datetime.now() + datetime.timedelta(days=job.get("days"), hours=job.get("hours"), minutes=job.get("minutes"), seconds=job.get("seconds"))
                relative_time = relative_datetime.DateTimeUtils.relative_datetime(time_until_trigger)[0]
                time_due = f"one-time, {relative_time} from now"
            result.append(f"{id}: {time_due}: {job['action']}")
        return "\n".join(result)
    async def get(self):
        return self.result(self._get())

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
            self._schedule.append({
                "action": action,
                "days": days,
                "hours": hours,
                "minutes": minutes,
                "seconds": seconds,
                "recurring": recurring
            })
            self._schedule.save()
            self.manager.scheduler.add(schedule_callback, func_args=(self, action), days=days, hours=hours, minutes=minutes, seconds=seconds, repeat=recurring)

        except Exception as e:
            core.log("error", e)
        return self.result("job successfully added!")

    async def edit_job(self, id: int, action: str, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0, recurring: bool = False):
        """
        Edits a job in the scheduler.

        ONLY use this if:
            - You're sure you have the ID (call get_schedule() if you can't see the ID)
            - You've verified the ID
            - User explicitely requested editing of the job
        """
        if id > len(self._schedule) or id < 0:
            return self.result(False)

        self._schedule[id] = {
            "action": action,
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "recurring": recurring
        }
        self._schedule.save()
        return self.result("job edited")

    async def remove_job(self, id: int):
        """
        Removes a scheduled job from the scheduler.

        ONLY use this if:
            - You're sure you have the ID (call get_schedule() if you can't see the ID)
            - You've verified the ID
            - User explicitely requested deletion of the job
        """
        if id > len(self._schedule) or id < 0:
            return self.result(False)
        self._schedule.pop(id)
        self.manager.scheduler.delete(id)
        self._schedule.save()
        return self.result("job deleted")
