import core
import asyncio
import prompt_toolkit
import prompt_toolkit.patch_stdout

class Cli(core.channel.Channel):
    async def _spawn_stream(self, msg):
        partial_msg = ""
        async for token in self.send_stream("user", msg):
            print(token, end="", flush=True)
        print()

    async def _status_indicator(self):
        while True:
            interval = 0.1
            print(".     ", end="\r", flush=True)
            await asyncio.sleep(interval)
            print("..    ", end="\r", flush=True)
            await asyncio.sleep(interval)
            print("...   ", end="\r", flush=True)
            await asyncio.sleep(interval)
            print("....  ", end="\r", flush=True)
            await asyncio.sleep(interval)
            print("..... ", end="\r", flush=True)
            await asyncio.sleep(interval)
            print("......", end="\r", flush=True)
            await asyncio.sleep(interval)
            print(" .....", end="\r", flush=True)
            await asyncio.sleep(interval)
            print("  ....", end="\r", flush=True)
            await asyncio.sleep(interval)
            print("   ...", end="\r", flush=True)
            await asyncio.sleep(interval)
            print("    ..", end="\r", flush=True)
            await asyncio.sleep(interval)
            print("     .", end="\r", flush=True)
            await asyncio.sleep(interval)
            print("      ", end="\r", flush=True)
            await asyncio.sleep(interval)

    async def _spawn(self, msg):
        status_task = asyncio.create_task(self._status_indicator())
        print(await self.send("user", msg))
        status_task.cancel()

    async def run(self):
        await self.announce("Welcome to opticlaw!")

        with prompt_toolkit.patch_stdout.patch_stdout():
            prompt_session = prompt_toolkit.PromptSession()
            while True:
                msg = await prompt_session.prompt_async("> ")
                message_state = None
                async for token in self.send_stream("user", msg):
                    if token.get("type") == "reasoning" and not message_state:
                        print("Reasoning:")
                        message_state = "reasoning"

                    if token.get("type") == "content" and message_state == "reasoning":
                        print()
                        print("Conclusion:")
                        message_state = "final output"

                    print(token.get("text"), end="", flush=True)
                #await self._spawn(msg)
                print()

    async def _announce(self, message: str, type: str = None):
        core.log("cli", message)
