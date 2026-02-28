import core
import prompt_toolkit
import prompt_toolkit.patch_stdout

class ChannelCli(core.channel.Channel):
    async def run(self):
        core.log("init", "Welcome to opticlaw!")

        with prompt_toolkit.patch_stdout.patch_stdout():
            prompt_session = prompt_toolkit.PromptSession()
            while True:
                msg = await prompt_session.prompt_async("> ")
                async for token in self.send_stream("user", msg):
                    print(token, end="", flush=True)
                print()

    async def announce(self, message: str):
        core.log("cli", message)
