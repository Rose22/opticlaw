import core

class Conversation(core.module.Module):
    @core.commands.command("conversations")
    async def list(self, args: list):
        """list conversations"""

        if not self.manager.conversations:
            return self.result("No saved conversations found.", False)

        result = "Saved conversations:\n"
        for conv in self.manager.conversations[:20]: # only the last 20 to avoid overwhelming the AI
            result += f"- [{conv.get('id')}] {conv.get('title', 'Untitled')}\n"

        return result

    @core.commands.command("conversation")
    async def load(self, args: list):
        """load conversation using ID"""
        if not args:
            return "please provide a conversation ID"

        conv_id = args[0]

        for conv in channel_instance.conversations:
            if conv.get('id') == conv_id:
                messages = conv.get('messages', [])

                # Push messages to backend
                self.manager.API.set_messages(messages)

                # Track active conversation
                self.manager.current_conversation_id = conv_id
