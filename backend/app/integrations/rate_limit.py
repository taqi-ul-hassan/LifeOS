class RateLimiter:
    def __init__(self, limit=60):
        self.limit, self.count = limit, {}

    def allow(self, key):
        self.count[key] = self.count.get(key, 0) + 1
        return self.count[key] <= self.limit
