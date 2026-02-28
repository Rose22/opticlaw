import core
import openai
import asyncio
import json
import inspect

class APIClient():
    """
    wrapper around the openAI API to make sending/receiving messages easier to work with
    """
    def __init__(self, manager, model: str, *args, **kwargs):
        # store a reference to the manager
        self.manager = manager

        # initialize connection to the API
        self._AI = openai.OpenAI(*args, **kwargs)

        self._model = model
        self._turns = []

    def insert_turn(self, role: str, content: str):
        """inserts a turn (message with role and content) into context, trimming when needed"""

        self.trim_turns()
        return self._turns.append({"role": role, "content": content})

    def trim_turns(self, max_turns: int = None):
        """trims context to keep token consumption low"""

        if not max_turns:
            max_turns = core.config.get("max_turns", 20)

        while len(self._turns) > max_turns:
            self._turns.pop(0)
        return len(self._turns) <= max_turns

    def _request(self, context, **kwargs):
        """send a request to the LLM and return the response object"""

        response = self._AI.chat.completions.create(
            model=self._model,
            messages=context,
            tools=kwargs.get("tools", None),
            stream=kwargs.get("stream", False)
        )

        return response

    def build_context(self, system_prompt=True):
        # context = system prompt + turn history
        context = []

        # always insert system prompt at start of context
        if core.config.get("system_prompt") and system_prompt:
            context = context+[{"role": "system", "content": core.config.get("system_prompt")}]

        # insert turn history
        context = context+self._turns

        return context

    def send(self, role: str, content: str, system_prompt=True, stream=True, use_context=True, use_tools=True, add_turn=True, **kwargs):
        """send a message to the LLM. returns a chat completions response object"""

        context = []
        if use_context:
            if add_turn:
                self.insert_turn(role, content)
            context = self.build_context(system_prompt=system_prompt)
        else:
            context = [{"role": role, "content": content}]

        return self._request(context, tools=(self.manager.tools if use_tools else None), stream=stream, **kwargs)

    async def recv(self, response, channel=None, add_turn=True, **kwargs):
        """takes a response object and extracts the message from it, handling tool calls if needed"""

        final_content = None

        # normal non-streaming mode
        response_main = response.choices[0]

        # extract message content
        final_content = response_main.message.content

        # handle tool calls, if any
        if response_main.message.tool_calls:
            final_content += await self.manager.handle_tool_calls(response_main.message.tool_calls, channel)

        # add it to context
        if add_turn:
            self.insert_turn("assistant", final_content)

        return final_content

    async def recv_stream(self, response, channel=None, use_tools=True, add_turn=True):
        """takes a response object and extracts the message from it, handling tool calls if needed. streaming version"""
        final_tool_calls = []
        tool_call_buffer = {}
        tokens = []

        for chunk in response:
            streamed_token = chunk.choices[0].delta

            # yield the current token in the stream
            if streamed_token.content:
                tokens.append(streamed_token.content)
                yield streamed_token.content

            # extract tool calls, if any
            if streamed_token.tool_calls and use_tools:
                # take the streamed tool call bits and mesh them together into a completed tool call array
                for tool_call in streamed_token.tool_calls:
                    index = tool_call.index

                    if index not in tool_call_buffer:
                        tool_call_buffer[index] = tool_call

                    tool_call_buffer[index].function.arguments += tool_call.function.arguments

        if use_tools:
            for index, tool_call in tool_call_buffer.items():
                final_tool_calls.append(tool_call)

            # handle tool calls, if any
            if final_tool_calls:
                tokens.append("\n")
                for word in await self.manager.handle_tool_calls(final_tool_calls, channel):
                    tokens.append(word)
                    yield word

        # add it to context
        if add_turn:
            final_content = "".join(tokens)
            self.insert_turn("assistant", final_content)

