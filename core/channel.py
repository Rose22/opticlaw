import core
import core.commands
import os
import sys
import time
import json
import asyncio

class Channel:
    """Base class for channels"""

    def __init__(self, manager):
        self.name = self.__class__.__name__
        self.manager = manager
        self.commands = core.commands.Commands(self)
        self._last_cmd_was_temporary = False


    async def send(self, role: str, message: str, **kwargs):
        """sends a message to the AI from within the current channel"""
        if self._last_cmd_was_temporary:
            # Remove the last two messages: the command and the command_response
            # We pop twice to ensure both the trigger and the result are gone.
            if len(self.manager.API._messages) >= 2:
                self.manager.API._messages.pop()
                self.manager.API._messages.pop()
                self._last_cmd_was_temporary = False

        cmd = await self.commands.process_input(message)
        if cmd:
            # insert /command into messages so that it gets properly tracked and displayed
            await self.manager.API.insert_message(f"command", message)

            # insert and return the command response without sending it to the AI
            await self.manager.API.insert_message(f"command_response", cmd)
            return cmd
        else:
            # if not a command, send the message to the AI and return it's response (context insertion happens in the API.send() method)
            return await self.manager.API.send(role, message, channel=self, stream=False, **kwargs)

    async def send_stream(self, role: str, message: str, **kwargs):
        """sends a message to the AI from within the current channel, streaming version"""
        if self._last_cmd_was_temporary:
            if len(self.manager.API._messages) >= 2:
                self.manager.API._messages.pop()
                self.manager.API._messages.pop()
                self._last_cmd_was_temporary = False

        cmd = await self.commands.process_input(message)
        if cmd:
            # insert /command into messages so that it gets properly tracked and displayed
            await self.manager.API.insert_message(f"command", message)

            # insert and return the command response without sending it to the AI
            cmd_response = []
            for token in cmd:
                cmd_response.append(token)
                token_data = {"type": "content", "text": token}
                yield token_data
            await self.manager.API.insert_message(f"command_response", "".join(cmd_response))
            return
        else:
            async for token in self.manager.API.send_stream(role, message, channel=self, **kwargs):
                yield token

    async def announce(self, message: str, type=None, insert_message=True):
        """called externally to announce things in this channel, such as a reminder sent by the AI"""
        if not type:
            type = "info"

        # insert announced message into context
        if insert_message:
            await self.manager.API.insert_message(f"announce_{type}", message)

        # Subclass hook
        await self._announce(message, type=type)
    async def _announce(self, message: str, type=None):
        """override this one in subclasses"""
        raise NotImplementedError

    async def announce_all(self, message: str, type=None):
        """announces a message across all channels. useful for very important notifications!"""
        if not type:
            type = "info"

        count = 0
        for channel_name, channel in self.manager.channels.items():
            insert = True if count < 1 else False
            await channel.announce(message, type, insert_message=insert)
            count += 1
        return

    async def ask(self, message: str):
        """sends a message in the channel and then intercepts communication for one message so that user can be asked for input without that input being sent to the LLM. useful for menus."""
        pass
