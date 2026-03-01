import core
import os
import sys
import subprocess
import tempfile

class ShellUnsafeTool(core.tool.Tool):
    """enables the AI to run shell commands. extremely dangerous! enable at your own risk"""

    async def unsafe_exec(self, cmd: str):
        """executes commands in an unsandboxed shell. careful!"""

        result = subprocess.run(cmd.split(), capture_output=True, shell=True, text=True)
        return result
