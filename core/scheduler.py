import core
import asyncio
import datetime

class Scheduler:
    def __init__(self):
        self._tasks = []

    def add(self,
            func,
            func_args: tuple = (),
            func_kwargs: dict = {},

            days: int = 0,
            hours: int = 0,
            minutes: int = 0,
            seconds: int = 0,
            repeat = False
    ):
        """add a task to the schedule. will call target function when the time has come."""

        self._tasks.append({
            "date_added": datetime.datetime.now(),
            "schedule": {"days": days, "hours": hours, "minutes": minutes, "seconds": seconds},
            "repeat": repeat,
            "func": func,
            "func_args": func_args,
            "func_kwargs": func_kwargs
        })

        return True

    def delete(self, index):
        """removes a task from the schedule by index"""
        if index <= len(self._tasks):
            return self._tasks.pop(index)
        return False

    async def run(self):
        """main loop"""
        while True:
            for task in self._tasks:
                # get datetime in the future that the task should be triggered
                trigger_time = task.get("date_added") + datetime.timedelta(**task.get("schedule"))
                # if we hit that datetime,
                if datetime.datetime.now() >= trigger_time:
                    # extract the function object from the scheduled task and call it
                    func_to_call = task.get("func")
                    if func_to_call:
                        await func_to_call(*task.get("func_args"), **task.get("func_kwargs"))

                        self._tasks.remove(task)
                        # if the task is set to repeat, just re-add it
                        if task.get("repeat"):
                            self.add(func_to_call, func_args=task.get("func_args"), func_kwargs=task.get("func_kwargs"), **task.get("schedule"), repeat=task.get("repeat"))

            # wait a few milliseconds per loop run.
            # ensures the program doesn't consume an insane amount of CPU
            await asyncio.sleep(0.10)
