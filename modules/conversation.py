import core

class Conversation(core.module.Module):
    @core.commands.command("conversations")
    async def list(self, args: list):
        """list conversations"""

        if not self.channel.conversations:
            return self.result("No saved conversations found.", False)

        result = "Saved conversations:\n"
        for conv in self.channel.conversations[:20]: # only the last 20 to avoid overwhelming the AI
            result += f"- [{conv.get('id')}] {conv.get('title', 'Untitled')}\n"

        return result

    @core.commands.command("conversation")
    async def load(self, args: list):
        """load conversation using ID"""
        if not args:
            return "please provide a conversation ID"

        conv_id = args[0]

        for conv in self.channel.conversations:
            if conv.get('id') == conv_id:
                messages = conv.get('messages', [])

                # Push messages to backend
                self.channel.context.set_messages(messages)

                # Track active conversation
                self.channel.current_conversation_id = conv_id
