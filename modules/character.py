import core

class Character(core.module.Module):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.characters = core.storage.StorageDict("characters", type="json")
        self.active_character = core.storage.StorageText("current_char")
        self._header = "Your identity"

    async def on_system_prompt(self):
        character_text = self.characters.get(self.active_character.get(), None)
        characters = ", ".join(self.characters.keys())
        return f"{character_text}\n\nYou can switch between identities using character_switch(). Characters available to switch yourself to: {characters}"
    async def switch(self, name: str):
        """Switches you to a different character. This will change your personality! Use this if user requests it."""
        if name not in self.characters.keys():
            return self.result("character not found", False)
        self.active_character.set(name)
        return self.result(f"character switched!")

    async def add(self, name: str, character: str):
        """
        Adds a new character to your character storage.

        Defines who you are as an AI. Also defines your writing style, so save style writing details to the character.

        ALWAYS write the character in third person, using the name provided.

        Start with "{name} is "

        Example:
            Assistant is a helpful AI. Assistant writes in a casual, concise, clear style.
        """
        if name in self.characters.keys():
            return self.result("character already exists", False)
        self.characters[name] = character
        self.characters.save()
        return self.result("character added")

    async def edit(self, name: str, character: str):
        """
        Edits an existing character.
        Use ONLY if user explicitely requests it.
        """
        if name not in self.characters.keys():
            return self.result("character doesn't exist!", False)
        self.characters[name] = character
        self.characters.save()

    async def delete(self, name: str):
        """
        Deletes an character.
        Use ONLY if user explicitely requests it.
        """
        if name in self.characters.keys():
            self.characters.pop(name, None)
            self.characters.save()
            return self.result(f"character {name} deleted")
        return self.result("character doesn't exist!", False)

    # async def list(self):
    #     """
    #     Returns a list of all your characters.
    #     """
    #     return self.result(self.characters)
