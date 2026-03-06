import core

class Character(core.module.Module):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.characters = core.storage.StorageDict("characters", type="json")
        self.active_character = core.storage.StorageText("current_char")
        self._header = "Your identity"

    def _list_characters(self):
        # collect categories
        sorted_by_cat = {}
        for character_name, character in self.characters.items():
            category = character.get("category", None)
            if category:
                if category not in sorted_by_cat.keys():
                    sorted_by_cat[category] = []

                sorted_by_cat[category].append(character_name)
            else:
                if "unsorted" not in sorted_by_cat.keys():
                    sorted_by_cat["unsorted"] = []

                sorted_by_cat["unsorted"].append(character_name)

        char_list = []
        for category_name, category in sorted_by_cat.items():
            characters = ", ".join(category)
            char_list.append(f"{category_name}: {characters}")

        characters = "\n".join(char_list)
        return characters

    async def on_system_prompt(self):
        curr_char = self.characters.get(self.active_character.get())
        character_text = ""
        if curr_char:
            character_text = self.characters.get(self.active_character.get(), None).get("identity", "")

        return f"{character_text}\n\nYou can switch between identities using character_switch(). User can switch characters using the `/character` command. Characters available to switch yourself to:\n{self._list_characters()}"

    async def on_command(self, cmd: str):
        name = " ".join(cmd)
        if not name:
            return "please provide a character name."
        elif name == "list":
            return self._list_characters()

        if self.manager.channel:
            response = await self.switch(name)
            #await self.manager.channel.send("user", f"Hi {name}")
            return f"character switched to {name}"

    async def on_command_help(self):
        return """
/character <name>       switches to that character
/character list         lists all characters
"""

    async def switch(self, name: str):
        """Switches you to a different character. This will change your personality! Use this if user requests it."""
        name = self._find_character(name)
        if not name:
            return self.result("character not found", False)
        self.active_character.set(name)
        return self.result(f"You are now {name}. Write your next reply as {name}")

    def _case_insensitive_replace(self, text, old, new):
        """
        Replaces all occurrences of 'old' with 'new' in 'text',
        ignoring case.
        """
        if not old:
            return text

        # Convert both text and old substring to lowercase for searching
        lower_text = text.lower()
        lower_old = old.lower()

        result_parts = []
        index = 0
        old_len = len(old)

        while True:
            # Find the next occurrence of the lowercase substring
            found_index = lower_text.find(lower_old, index)

            if found_index == -1:
                # No more matches, append the rest of the string
                result_parts.append(text[index:])
                break

            # Append the text segment before the match (preserving original case)
            result_parts.append(text[index:found_index])
            # Append the new replacement
            result_parts.append(new)

            # Move the index forward to continue searching
            index = found_index + old_len

        return "".join(result_parts)

    def _find_character(self, name: str):
        """searches for a character, case insensitive"""

        for character_name in self.characters.keys():
            if character_name.lower().strip() == name.lower().strip():
                return character_name
        return None

    def _rewrite_character(self, name: str, character: str):
        """rewrites a character to automatically port over character cards"""
        replacement_map = {
            "{{char}}": name,
            "{char}": name,
            "{{user}}": "user",
            "{user}": "user",
            "you are": f"{name} is",
            "you should": f"{name} should",
            "you must": f"{name} must",
            "you want": f"{name} wants",
            "you have": f"{name} has"
        }

        for word, replacement in replacement_map.items():
            character = self._case_insensitive_replace(character, word, replacement)

        return character

    async def add(self, name: str, character: str, category: str):
        """
        Adds a new character to your character storage.

        Defines who you are as an AI. Also defines your writing style, so save style writing details to the character.

        ALWAYS use your name to refer to yourself.
        ALWAYS use the word user to refer to the user.

        For the category, look at available categories and if one exists that fits the character, use that category. Otherwise, use a new category.

        Example:
            Assistant is a helpful AI. Assistant writes in a casual, concise, clear style.
        """
        name = self._find_character(name)
        if name:
            return self.result("character already exists", False)

        self.characters[name] = {
            "identity": self._rewrite_character(name, character),
            "category": category.lower()
        }
        self.characters.save()
        return self.result("character added")

    async def edit(self, name: str, category: str = None, character: str = None):
        """
        Edits an existing character.
        Use ONLY if user explicitely requests it.
        """
        name = self._find_character(name)
        if not name:
            return self.result("character doesn't exist!", False)

        if character:
            self.characters[name]["identity"] = character
        if category:
            self.characters[name]["category"] = category.lower()

        self.characters.save()
        return self.result("character edited.")

    async def delete(self, name: str):
        """
        Deletes an character.
        Use ONLY if user explicitely requests it.
        """
        name = self._find_character(name)
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
