class MemorySummarizer:
    def summarize(self, contents: list[str]) -> str:
        unique = list(dict.fromkeys(part.strip() for part in contents if part.strip()))
        return " ".join(unique)[:2_000]
