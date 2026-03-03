import core
import os
import sys
import time
import json

class Channel:
    """Base class for channels"""

    def __init__(self, manager):
        self.name = self.__class__.__name__
        self.manager = manager
        self._help = """
/new            start a new session (clears context window)
/clear          same as /new
/sysprompt      show current system prompt
/context        show current context window
/tools          list tools available to the AI

/status         show status info
/modules        list modules
/module         enable/disable a module by name

/models         list available models
/model          switch model

/restart        restarts the server
/stop           stops the AI in it's tracks
/help           this help
""".strip()


    async def _process_input(self, message: str):
        """processes user input and detects special commands that control opticlaw"""
        message = message.strip().lower()
        cmd_prefix = core.config.get("cmd_prefix", "/")
        if not message.startswith(cmd_prefix):
            return None

        cmd = message.split(cmd_prefix)[1].split()

        match cmd[0]:
            case "new":
                self.manager.API._turns = []
                return "New session started."
            case "clear":
                # alias for "new"
                self.manager.API._turns = []
                return "New session started."
            case "help":
                return self._help
            case "status":
                return "\n".join(await self.manager.get_status())
            case "models":
                return "not implemented yet"
            case "model":
                return "not implemented yet"
            case "modules":
                # TODO: also get disabled modules
                modules_str = "\n".join(core.config.get("modules"))
                modules_disabled_str = "\n".join(core.config.get("modules_disabled"))
                modules_loaded_str = "\n".join(self.manager.modules.keys())

                return f"Loaded:\n{modules_loaded_str}\n\nDisabled in config:\n{modules_disabled_str}\n"
            case "module":
                return "not implemented yet"
            case "tools":
                tool_list = []
                for tool in self.manager.tools:
                    tool_list.append(tool.get("function").get("name"))
                return "\n".join(tool_list)
            case "sysprompt":
                if not core.config.get("context_window"):
                    return "CONTEXT DISABLED"

                sysprompt = await self.manager.get_system_prompt()
                disabled_prompts = core.config.get("modules_disable_prompts")
                if disabled_prompts:
                    sysprompt += "\n\n== disabled prompts ==\n"
                    sysprompt += "\n".join([mod_name for mod_name in disabled_prompts])

                return sysprompt if sysprompt else "BLANK"
            case "context":
                if not core.config.get("context_window"):
                    return "CONTEXT DISABLED"

                context = await self.manager.API.build_context(system_prompt=True)
                if not context:
                    return "BLANK"

                context_display = []

                for turn in context:
                    context_display.append(f"== {turn.get('role')} ==\n{turn.get('content')}")

                context_display.append("---")

                disabled_prompts = core.config.get("modules_disable_prompts")
                if disabled_prompts:
                    disabled_prompts_str = "\n".join([mod_name for mod_name in disabled_prompts])
                    context_display.append(f"== disabled prompts ==\n{disabled_prompts_str}")

                ctx_string = ""
                context_size = await self.manager.API.get_context_size()
                for key, value in context_size.items():
                    ctx_string += f"{key}: {value}\n"
                context_display.append(f"== context size ==\n{ctx_string}")

                return "\n\n".join(context_display)
            case "restart":
                await self.announce_all("restarting server..")
                time.sleep(0.1)
                os.execv(sys.argv[0], sys.argv)
            case "stop":
                # just use restart for now until i figure out how to kill the asyncio tasks
                await self.announce_all("stopping..")
                time.sleep(0.1)
                os.execv(sys.argv[0], sys.argv)
            case _:
                return self._help

    async def send(self, role: str, message: str, **kwargs):
        """sends a message to the AI from within the current channel"""
        cmd_process = await self._process_input(message)
        if cmd_process:
            return cmd_process

        return await self.manager.API.send(role, message, channel=self, stream=False, **kwargs)

    async def send_stream(self, role: str, message: str, **kwargs):
        """sends a message to the AI from within the current channel, streaming version"""
        cmd_process = await self._process_input(message)
        if cmd_process:
            for word in cmd_process:
                yield word
            return

        async for token in self.manager.API.send_stream(role, message, channel=self, **kwargs):
            yield token

    async def announce(self, message: str):
        """called externally to announce things in this channel, such as a reminder sent by the AI"""
        raise NotImplementedError

    async def announce_all(self, message: str):
        """announces a message across all channels. useful for very important notifications!"""
        for channel_name, channel in self.manager.channels.items():
            await channel.announce(message)
        return

    async def ask(self, message: str):
        """sends a message in the channel and then intercepts communication for one turn so that user can be asked for input without that input being sent to the LLM. useful for menus."""
        pass
