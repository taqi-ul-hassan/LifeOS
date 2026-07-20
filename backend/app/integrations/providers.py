class Connector:
    version = "1.0"
    enabled = True

    def __init__(self, name):
        self.name = name

    def connect(self, credentials):
        return {"status": "connected"}

    def disconnect(self):
        return {"status": "disconnected"}

    def health(self):
        return {"status": "healthy"}

    def sync(self, mode, cursor=None):
        return {"status": "completed", "cursor": cursor}

    def publish(self, event):
        return {"accepted": True}

    def receive(self, payload):
        return payload

    def refresh(self, credentials):
        return credentials

    def metadata(self):
        return {"name": self.name, "version": self.version}
