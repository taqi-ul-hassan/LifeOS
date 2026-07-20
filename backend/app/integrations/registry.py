class ProviderRegistry:
    def __init__(self):
        self.providers = {}

    def register(self, provider):
        self.providers[provider.name] = provider

    def remove(self, name):
        self.providers.pop(name, None)

    def get(self, name):
        return self.providers.get(name)

    def discover(self):
        return [
            {"name": p.name, "version": p.version, "enabled": p.enabled}
            for p in self.providers.values()
        ]


registry = ProviderRegistry()
