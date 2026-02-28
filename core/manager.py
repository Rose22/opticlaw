import core
import tools
import asyncio
import inspect

class Manager:
    """the central class that manages everything"""

    # --- main ---
    def __init__(self):
        self.AI = None # connect later with .connect()
        self.scheduler = core.scheduler.Scheduler()
        self.channels = {}
        self.tool_classes = []
        self.tools = []

    def connect(self, *args, **kwargs):
        args = (self,)+args
        try:
            self.AI = core.openai_api.OpenAIClient(*args, **kwargs)
        except Exception as e:
            core.log("error", f"error connecting to API: {e}")
            exit(1)
        return self.AI

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

    # --- tools ---
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

            try:
                func_obj = getattr(toolclass, func_name)
            except:
                continue

            if not callable(func_obj):
                continue

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

                func_params_translated[param_name] = {"type": param_type, "description": ""}

            # if there's a docstring, make sure to pass that on to the LLM
            docstring = ""
            if "__doc__" in dir(func_obj):
                docstring = func_obj.__doc__

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
