import core

class OpticlawManual(core.module.Module):
    async def on_system_prompt(self):
        return """You are running inside OptiClaw, an AI agent framework that lets you act autonomously. User can use /help to get more information on how to use opticlaw."""

    # TODO: add builtin documentation that can be consulted by the AI and explained to the user
