import core
import os
import sys
import platform
import datetime
import asyncio
import json
import inspect
import re
import tools

class Manager:
    """the central class that manages everything"""

    # --- main ---
    def __init__(self):
        self.API = None # connect later with .connect()
        self.scheduler = core.scheduler.Scheduler()
        self.channels = {}
        self.tool_classes = []
        self.tools = []
        self.memory = core.memory.Memory()

    def connect(self, *args, **kwargs):
        args = (self,)+args
        try:
            self.API = core.api_client.APIClient(*args, **kwargs)
        except Exception as e:
            core.log("error", f"error connecting to API: {e}")
            exit(1)

        # Retrieve specific model details
        #model_info = self.API._AI.models.retrieve(model_id)

        return self.API

    async def run(self):
        """main loop"""
        tasks = []

        # start scheduler
        tasks.append(asyncio.create_task(self.scheduler.run()))

        # load channels
        core.log("init", "loading channels")
        import channels
        for channel in channels.get_all():
            chan = channel(self)
            self.channels[chan.name] = chan

        # start channels
        for channel_name, channel in self.channels.items():
            tasks.append(asyncio.create_task(channel.run()))
            core.log("init", f"started channel {channel.name}")

        core.log("init", "loading tools")
        # load tools
        for tool in tools.get_all():
            self.add_tool_class(tool)
        core.log("init", "loaded tools")

        # run everything
        await asyncio.gather(*tasks)

    def get_system_prompt(self):
        system_prompt = core.config.get("system_prompt", "")

        details = {
            "current time": datetime.datetime.now().isoformat(),
            "OS": sys.platform,
            "OS release": platform.release(),
            "platform": platform.platform(),
            "architecture": platform.machine() if platform.machine() else "unknown",
            "hostname": platform.node(),
            "home dir": os.path.expanduser("~"),
            "working directory": os.getcwd()
        }

        details_string = ""
        for key, value in details.items():
            details_string += f"{key}: {value}\n"

        full_prompt = "\n".join([
            "# Session context",
            details_string,
            "# Important memories",
            self.memory.get_persistent_memories(),
            "# Your identity",
            system_prompt
        ])

        return full_prompt

    # --- tools ---
    def parse_tool_docstring(self, docstring):
        """
        Parses Google-style docstring to extract param descriptions
        and returns a cleaned docstring without the Args/Returns sections.
        """
        if not docstring:
            return {}, ""

        descriptions = {}
        lines = docstring.split("\n")
        clean_lines = []

        skip_section = False
        section_headers = {"Args:", "Returns:", "Raises:", "Note:", "Example:"}

        for line in lines:
            stripped = line.strip()

            # Check if we're entering a section to skip
            if any(stripped.startswith(header) for header in section_headers):
                skip_section = True
                continue

            # Check if we're still in a skip section (indented line)
            if skip_section:
                # Empty line or unindented line means end of section
                if stripped == "" or (line and not line[0].isspace() and stripped):
                    # But if it's another section header, stay in skip mode
                    if not any(stripped.startswith(h) for h in section_headers):
                        skip_section = False
                        if stripped:
                            clean_lines.append(line)
                continue

            clean_lines.append(line)

        # Now parse Args section separately for descriptions
        in_args = False
        current_param = None
        current_desc = []

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("Args:"):
                in_args = True
                continue

            if in_args:
                if any(stripped.startswith(h) for h in {"Returns:", "Raises:", "Note:", "Example:"}):
                    if current_param and current_desc:
                        descriptions[current_param] = " ".join(current_desc)
                    break

                if not stripped:
                    continue

                # Match: "param_name: description" or "param_name (type): description"
                match = re.match(r"(\w+)(?:\s*\([^)]*\))?\s*:\s*(.+)", stripped)
                if match:
                    # Save previous param if exists
                    if current_param and current_desc:
                        descriptions[current_param] = " ".join(current_desc)

                    current_param = match.group(1)
                    current_desc = [match.group(2)]
                elif current_param and stripped:
                    # Continuation of previous param description
                    current_desc.append(stripped)

        # Save last param
        if current_param and current_desc:
            descriptions[current_param] = " ".join(current_desc)

        # Clean up the description (remove leading/trailing whitespace, empty lines)
        clean_doc = "\n".join(clean_lines).strip()

        return descriptions, clean_doc

    def add_tool_class(self, toolclass):
        """
        Adds tools to the manager based on a class with functions.
        To make tools, just make a class like so:
        class MyToolClass(core.tools.Tools):
            def search_web(query: str):
                self.channel.send(your_websearch(query))
        """

        self.tool_classes.append(toolclass)

        for func_name in dir(toolclass):
            if func_name.startswith("_"):
                # skip private methods and other private properties
                continue

            if func_name == "result":
                # builtin result function
                continue

            try:
                func_obj = getattr(toolclass, func_name)
            except:
                continue

            if not callable(func_obj):
                continue

            # if there's a docstring, make sure to pass that on to the LLM
            docstring = ""
            if "__doc__" in dir(func_obj):
                param_descriptions, docstring = self.parse_tool_docstring(func_obj.__doc__)

            # dynamically load class methods from classes
            func_params = dict(inspect.signature(func_obj).parameters)
            # remove "self" arg from func
            del(func_params["self"])

            func_params_translated = {}
            # add method arguments (parameters) to the tool call object
            for param_name, param in func_params.items():
                # translate parameter type name to the correct format
                param_split = str(param).split(":")
                param_name = param_split[0].strip()
                param_type = "str"
                if len(param_split) > 1:
                    param_type = param_split[1].split()[0].strip()

                param_type_map = {
                    "str": "string",
                    "int": "integer",
                    "list": "array",
                    "bool": "boolean"
                    # TODO: support more types
                }

                for word, replacement in param_type_map.items():
                    if param_type == word:
                        param_type = replacement

                func_params_translated[param_name] = {"type": param_type, "description": param_descriptions.get(param_name)}

            # build toolcall object
            tool = {
                "type": "function",
                "function": {
                    "name": func_name,
                    "description": docstring,
                    "parameters": {
                        "type": "object",
                        "properties": func_params_translated,
                        "required": [key for key in func_params.keys()],
                        "additionalProperties": False,
                    },
                    "strict": True,
                },
            }

            self.tools.append(tool)

    async def handle_tool_calls(self, tool_calls, channel=None):
        results = []

        # add toolcalls to context
        tools_called = {
            "role": "assistant",
            "tool_calls": [tool_call.to_dict() for tool_call in tool_calls]
        }
        self.API._turns.append(tools_called)

        # call any tool calls based on the stored tool call function
        for tool_call in tool_calls:
            # does the method exist within any of the loaded classes?
            toolclass_instance = None
            for class_obj in self.tool_classes:
                if hasattr(class_obj, tool_call.function.name):
                    toolclass_instance = class_obj(self)
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
                try:
                    func_response = await func_callable(**arg_obj)
                    # and add the method's return value to the LLM's context window as a tool call response
                    tool_response = {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(str(func_response))}
                except Exception as e:
                    tool_response = {"role": "tool", "tool_call_id": tool_call.id, "content": f"error: {str(e)}"}

                self.API._turns.append(tool_response)
            else:
                core.log("toolcall", f"tried to call tool {tool_call.function.name} but couldnt find it?!")

        # get user's last request from turns
        user_last_turn = {}
        for turn in self.API._turns:
            if turn.get("role") == "user":
                user_last_turn = turn

        self.API.trim_turns()

        prompt = self.API._turns+[{"role": "system", "content": "If the tool response provides sufficient answers, tell the user the results. If not, consider if you need to use another tool? If so, call it."}]

        try:
            return await self.API.recv(
                self.API._request(prompt, tools=self.tools),
                channel=channel,
                use_tools=True,
                add_turn=True
            )
        except Exception as e:
            core.log_error(f"error while processing tool results", e)
