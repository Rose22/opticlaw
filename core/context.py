class Context:
    def __init__(self, manager):
        self.manager = manager
        self.messages = []

    def get_messages(self):
        return self.messages
    def set_messages(self, messages: list):
        self.messages = messages

    def _insert_blank_user_msg(self, next_msg_role: str):
        if (
            # if we have anything at all in the messages array
            self.messages and
            # and the last message was not a user or tool response message
            self.messages[-1].get("role") not in ("user", "tool") and
            # and the last message was also not an assistant message with toolcalls
            not self.messages[-1].get("tool_calls") and
            # and the message we're about to post isn't by the user role
            next_msg_role != "user"
        ):
            # ensure message turn order is correct
            # assistants are allowed to output after a tool role message
            # but not after their own message..
            self.messages.append({"role": "user", "content": "[SYSTEM_TICK]"})
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

    async def insert_message(self, role: str, content: str, num_tokens=None):
        """inserts a message (dict with role and content) into context, trimming when needed"""
        if not core.config.get("context_window", False):
            # allow completely turning off context
            return

        await self.trim_messages(num_tokens=num_tokens)
        return self.messages.append(self._convert_message(role, content))

    async def trim_messages(self, max_messages: int = None, max_tokens: int = None, num_tokens: int = None):
        """trims context to keep token consumption low"""

        if not max_messages:
            max_messages = core.config.get("max_messages", 200)
        if not max_tokens:
            # TODO: find a way to get max tokens. also count tokens instead of words
            max_tokens = core.config.get("max_context", 8192)

        if not num_tokens:
            # fall back to counting messages list using tiktoken
            num_tokens = self.manager.API.count_tokens_local(self.messages)

        request_too_big = False
        context_trimmed = False
        tokens_exceeded = (num_tokens >= max_tokens)
        message_count_exceeded = (len(self.messages) >= max_messages)
        num_tokens = self.manager.API.count_tokens_local(self.messages)

        # need to recalculate it cuz this is a while loop
        while len(self.messages) >= max_messages or num_tokens >= max_tokens:
            self.messages.pop(0)
            if not self.messages:
                request_too_big = True
                # we've exhausted all messages. handle it later in this function
                break

            # keep recalculating tokens
            num_tokens = self.manager.API.count_tokens_local(self.messages)

        if self.manager.channel:
            if request_too_big:
                # the entire thing was too big including user's input! inform them
                await self.manager.channel.announce("Your request exceeds the max amount of tokens allowed. Please send a smaller request!", "error")
            elif message_count_exceeded:
                await self.manager.channel.announce(f"You exceeded the max amount of messages set in your settings! Context size trimmed.\n\nAmount of messages: {len(self.messages)}\nMax messages allowed: {max_messages}", "error")
            elif context_trimmed:
                await self.manager.channel.announce("Input was too large! Context size trimmed.\n\nSent tokens: {num_tokens}\nMax allowed tokens: {max_tokens}", "error")
        return len(self.messages) <= max_messages

    async def build_context(self, system_prompt=True, end_prompt=True):
        # context = system prompt + message history
        context = []

        # always insert system prompt at start of context
        if system_prompt:
            context = context+[{"role": "system", "content": await self.manager.get_system_prompt()}]

        # insert message history
        context = context+self._messages

        if end_prompt:
            histend = await self.manager.get_end_prompt()
            # for some reason, it won't accept a 2nd system prompt. so we add it as user
            # maybe theres a better way to do this..
            context = context+[{"role": "user", "content": histend}]

        return context

    async def get_context_size(self):
        message_history = await self.build_context(system_prompt=False)
        sysprompt = await self.manager.get_system_prompt()
        histend = await self.manager.get_end_prompt()
        sysprompt_size_tokens = self.count_tokens_local([{"role": "system", "content": sysprompt}])
        sysprompt_size_words = len(str(sysprompt).split())
        message_hist_size_tokens = self.count_tokens_local(self._messages)
        message_hist_size_words = len(str(message_history).split())
        histend_size_tokens = self.count_tokens_local([{"role": "user", "content": histend}])
        histend_size_words = len(str(histend).split())

        combined_size_words = message_hist_size_words+sysprompt_size_words+histend_size_words

        token_usage = self.count_tokens_local(await self.build_context(system_prompt=True))

        return {
            "system prompt size": f"{sysprompt_size_tokens} tokens | {sysprompt_size_words} words",
            "message history size": f"{message_hist_size_tokens} tokens | {message_hist_size_words} words",
            "end prompt size": f"{histend_size_tokens} tokens | {histend_size_words} words",
            "total size": f"{token_usage} tokens | {combined_size_words} words",
        }
