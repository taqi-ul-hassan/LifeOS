from .encryption import decrypt, encrypt


class CredentialStore:
    def seal(self, value: dict) -> str:
        return encrypt(value)

    def open(self, value: str) -> dict:
        return decrypt(value)
