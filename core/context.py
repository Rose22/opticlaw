import core

class Context:
    def __init__(self, channel):
        self.channel = channel

        # UI-agnostic chat history system - save/load context windows from save file!
        self.chat = core.chat.Chat(self.channel)

    async def build(self, system_prompt=True, end_prompt=True):
        """builds the full context window using system prompt + message history + end prompt"""

        # context = system prompt + message history
        context = []

        # always insert system prompt at start of context
        if system_prompt:
            context = context+[{"role": "system", "content": await self.channel.manager.get_system_prompt()}]

        # insert message history
        context = context+(await self.chat.get())

        if end_prompt:
            histend = await self.channel.manager.get_end_prompt()
            # for some reason, it won't accept a 2nd system prompt. so we add it as user
            # maybe theres a better way to do this..
            context = context+[{"role": "user", "content": histend}]

        return context

    def _insert_blank_user_msg(self, next_msg_role: str):
        messages = chat.get()

        if (
            # if we have anything at all in the messages array
            messages and
            # and the last message was not a user or tool response message
            messages[-1].get("role") not in ("user", "tool") and
            # and the last message was also not an assistant message with toolcalls
            not messages[-1].get("tool_calls") and
            # and the message we're about to post isn't by the user role
            next_msg_role != "user"
        ):
            # ensure message turn order is correct
            # assistants are allowed to output after a tool role message
            # but not after their own message..
            self.chat.add({"role": "user", "content": "[SYSTEM_TICK]"})
        return True

    def _convert_message(self, role: str, content: str):
        # we need to make sure the chain is always system -> user -> assistant -> user -> ... because some models are REALLY particular about it and it's really annoying

        # Convert special roles to valid API roles with prefixes
        if role.startswith('announce_'):
            # announce_info, announce_error, announce_important, announce_schedule
            ann_type = role[9:]  # 'announce_info' -> 'info'
            content = f"[System {ann_type.title()}]: {content}"
            role = 'assistant'
        elif role == 'command':
            # User commands stay as user role
            role = 'user'
        elif role == 'command_response':
            # Command responses appear as assistant
            content = f"[Command Output]: {content}"
            role = 'assistant'

        # insert blank user message if applicable
        self._insert_blank_user_msg(role)

        return {"role": role, "content": content}

    async def get_size(self):
        message_history = await self.build(system_prompt=False)
        sysprompt = await self.channel.manager.get_system_prompt()
        histend = await self.channel.manager.get_end_prompt()
        sysprompt_size_tokens = await self.chat.count_tokens([{"role": "system", "content": sysprompt}])
        sysprompt_size_words = len(str(sysprompt).split())
        message_hist_size_tokens = await self.chat.count_tokens(await self.chat.get())
        message_hist_size_words = len(str(message_history).split())
        histend_size_tokens = await self.chat.count_tokens([{"role": "user", "content": histend}])
        histend_size_words = len(str(histend).split())

        combined_size_words = message_hist_size_words+sysprompt_size_words+histend_size_words

        token_usage = await self.chat.count_tokens(await self.build(system_prompt=True))

        return {
            "system prompt size": f"{sysprompt_size_tokens} tokens | {sysprompt_size_words} words",
            "message history size": f"{message_hist_size_tokens} tokens | {message_hist_size_words} words",
            "end prompt size": f"{histend_size_tokens} tokens | {histend_size_words} words",
            "total size": f"{token_usage} tokens | {combined_size_words} words",
        }
