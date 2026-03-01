import core
import datetime

class Memory(core.storage.Storage):
    """manages the AI's memory"""

    def _filter_memory_content(self, content):
        # replace common phrases in memory content

        replacement_map = {
            "today": "on this day",
            "yesterday": "the day before this day",
            "now": "at the time",
            "tomorrow": "the day after this day",
            "last week": "a week before this day",
            "next week": "a week after this day"
        }

        for orig, replacement in replacement_map.items():
            # case insensitive replace
            content = re.sub(orig, replacement, content, flags=re.IGNORECASE)

        return content

    def store(self, content: str, persistent: bool = False):
        """stores a memory"""
        content = self._filter_memory_content(content)

        # Generate new ID
        highest_id = max([m.get("id", 0) for m in self], default=0) + 1

        new_mem = {
            "id": highest_id,
            "date": datetime.date.today().isoformat(),
            "content": content
        }

        if persistent:
            new_mem["persistent"] = True

        self.append(new_mem)
        self.save()

        return self.result(f"id: {highest_id}")

    def edit(self, id: int, content: str, persistent: bool = None):
        """edits a memory"""
        content = _filter_memory_content(content)

        # Check if memory exists
        for index, memory in enumerate(self):
            if memory.get("id") == id:
                memory["content"] = content
                if persistent != None:
                    memory["persistent"] = persistent
                self[index] = memory
                self.save()

                return id

    def delete(self, id: int) -> dict:
        """deletes a memory"""

        # Check if memory exists
        for index, memory in enumerate(self):
            if memory.get("id") == id:
                del self[index]
                self.save()
                return id

    def get_persistent(self):
        persistent_mem = []
        for memory in self:
            if memory.get("persistent"):
                persistent_mem.append(memory)

        return persistent_mem

    def get_history(self, from_days_ago: int = 30, to_days_ago: int = 0):
        """retrieves all history logs stored in memory"""
        mem_filtered = []

        max_date_in_past = datetime.date.today() - datetime.timedelta(days=from_days_ago)
        min_date_in_past = datetime.date.today() - datetime.timedelta(days=to_days_ago)

        for memory in self:
            # if memory.get("persistent", False):
            #     # include persistent memories if no date range was set
            #     if from_days_ago == 30 and not to_days_ago:
            #         mem_filtered.append(memory)
            #     continue

            if memory.get("persistent"):
                continue

            # filter non-persistent memories by date
            memory_date = datetime.date.fromisoformat(memory.get("date"))
            if max_date_in_past <= memory_date <= min_date_in_past:
                mem_filtered.append(memory)

        return mem_filtered
