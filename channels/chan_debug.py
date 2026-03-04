import core
import prompt_toolkit
import prompt_toolkit.patch_stdout

class Debug(core.channel.Channel):
    async def run(self):
        await self.announce("DEBUG CHANNEL ACTIVATED")

        with prompt_toolkit.patch_stdout.patch_stdout():
            prompt_session = prompt_toolkit.PromptSession()
            while True:
                msg = await prompt_session.prompt_async("> ")
                async for token in self.send_stream("user", msg, debug=True):
                    print(token, end="", flush=True)
                print()

    async def announce(self, message: str, type: str = None):
        core.log("cli", message)
