import core
import openai
import asyncio
import json
import inspect

class OpenAIClient():
    """
    wrapper around the openAI API to make sending/receiving messages easier to work with
    """
    def __init__(self, manager, model: str, *args, **kwargs):
        # store a reference to the manager
        self.manager = manager

        # initialize connection to the API
        self._AI = openai.OpenAI(*args, **kwargs)

        self._model = model
        self._context = []

    def insert_context(self, role: str, content: str):
        """inserts something into context as specified role"""

        return self._context.append({"role": role, "content": content})

    def trim_context(self, max_turns: int):
        """trims context to keep token consumption low"""
        if len(self._context) > max_turns:
            self._context.pop(0)
            return True
        return False

    def _request(self, context, **kwargs):
        """send a request to the LLM and return the response object"""

        response = self._AI.chat.completions.create(
            model=self._model,
            messages=context,
            tools=self.manager.tools if kwargs.get("tools") else None,
            stream=kwargs.get("stream", False)
        )

        return response

    def send(self, role: str, content: str, stream=True, include_tools=True, add_to_context=True):
        """send a message to the LLM. returns a chat completions response object"""

        prompt = self._context+[{"role": role, "content": content}] # context plus current message
        if add_to_context:
        # response = self._AI.chat.completions.create(
        #     model=self._model,
        #     messages=self._context,
        #     tools=self.manager.tools if include_tools else None,
        #     stream=stream
        # )
            self.insert_context(role, content)

        return self._request(prompt, tools=include_tools, stream=stream)

    async def recv(self, response, channel=None, use_tools=True):
        """takes a response object and extracts the message from it, handling tool calls if needed"""

        final_content = None

        # normal non-streaming mode
        response_main = response.choices[0]

        # extract message content
        final_content = response_main.message.content

        # handle tool calls, if any
        if response_main.message.tool_calls and use_tools:
            final_content += await self._handle_tool_calls(response_main.message.tool_calls, channel)

        # add it to context
        self.insert_context("assistant", final_content)
        self.trim_context(core.config.get("max_context", 20))

        return final_content

    async def recv_stream(self, response, channel=None, use_tools=True):
        """takes a response object and extracts the message from it, handling tool calls if needed. streaming version"""
        final_content = ""
        final_tool_calls = []

        chunks = []
        tool_call_buffer = {}
        for chunk in response:
            streamed_token = chunk.choices[0].delta

            # yield the current token in the stream
            if streamed_token.content:
                chunks.append(streamed_token.content)
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
                for word in await self._handle_tool_calls(final_tool_calls, channel):
                    yield word

        self.trim_context(core.config.get("max_context", 20))

    async def _handle_tool_calls(self, tool_calls, channel=None):
        results = []

        # call any tool calls based on the stored tool call function
        for tool_call in tool_calls:
            # does the method exist within any of the loaded classes?
            toolclass_instance = None
            for class_obj in self.manager.tool_classes:
                if hasattr(class_obj, tool_call.function.name):
                    toolclass_instance = class_obj(self.manager)
                    # store a reference to the channel used to send the message
                    if channel:
                        toolclass_instance.channel = channel
                    else:
                        core.log("warning", "channel was not used")

            if toolclass_instance:
                # get the class method object
                func_callable = getattr(toolclass_instance, tool_call.function.name)

                # format its arguments in a JSON format the llm will understand
                arg_obj = json.loads(tool_call.function.arguments)
                arg_display = []
                for arg_name, arg_value in arg_obj.items():
                    arg_display.append(str(arg_value))
                arg_display = ", ".join(arg_display)
                core.log("toolcall", f"calling tool {tool_call.function.name}({arg_display})")

                # call the class method
                self._context.append({"role": "tool", "tool_call_id": tool_call.id, "arguments": tool_call.function.arguments, "content": ""})
                try:
                    func_response = await func_callable(**arg_obj)
                    # and add the method's return value to the LLM's context window as a tool call response
                    self._context.append({"role": "tool_response", "tool_call_id": tool_call.id, "content": json.dumps(str(func_response))})
                except Exception as e:
                    self._context.append({"role": "tool_response", "tool_call_id": tool_call.id, "content": f"error: {str(e)}"})
            else:
                core.log("toolcall", f"tried to call tool {tool_call.function.name} but couldnt find it?!")

        return await self.recv(
            self._request(self._context+[{"role": "system", "content": "tell user the results of the tool calls. look at tool_response"}]),
            use_tools=False
        )

