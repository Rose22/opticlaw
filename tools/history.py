import core

class HistoryTool(core.tool.Tool):
    async def get_history(self, from_days_ago: int = 30, to_days_ago: int = 0):
        """
        Retrieves information about events from the past. This is your ONLY source of past information about previous conversations - DO NOT assume you know anything from previous conversations unless you call this first.

        Information stored includes:
        - Past events and conversations

        Args:
            from_days_ago (int, optional): Number of days to remember from, relative to today
                if None, defaults to 30 days ago.
            to_days_ago (int, optional): Number of days to remember up to, relative to today
                if None, defaults to today.

        Examples:
            - get_memories(30, 0) → Last 30 days
            - get_memories(30, 1) → Last 30 days up until yesterday
            - get_memories(30, 7) → Last 30 days up until 7 days before today
            - get_memories(1, 1) → Only yesterday
            - get_memories(365, 0) → A whole year up until today
            - get_memories(730, 365) → Last year (730 days = 2 years ago, 365 days = 1 year ago)
            - get_memories(7, 7) → Exactly 7 days ago, without any other days included
        """
        mem_filtered = []

        max_date_in_past = datetime.date.today() - datetime.timedelta(days=from_days_ago)
        min_date_in_past = datetime.date.today() - datetime.timedelta(days=to_days_ago)

        for memory in self.manager.history:
            # filter non-persistent memories by date
            memory_date = datetime.date.fromisoformat(memory.get("date"))
            if max_date_in_past <= memory_date <= min_date_in_past:
                mem_filtered.append(memory)

        return self.result(mem_filtered)
