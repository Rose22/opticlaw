import core

class Model(core.module.Module):
    """makes the AI aware of what model it's using!"""
    async def on_system_prompt(self):
        model = self.manager.API.get_model()
        return f"AI model in use: {model}"
