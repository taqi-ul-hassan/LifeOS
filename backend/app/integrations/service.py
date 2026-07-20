from fastapi import HTTPException
from .credentials import CredentialStore
from .models import EncryptedCredential, IntegrationAudit, IntegrationConnection
from .registry import registry
from .repository import IntegrationRepository
from .sync import record


class IntegrationService:
    def __init__(self, session):
        self.session, self.repo, self.credentials = (
            session,
            IntegrationRepository(session),
            CredentialStore(),
        )

    def connect(self, user_id, provider, scopes, credentials):
        connector = registry.get(provider)
        if not connector:
            raise HTTPException(404, "Provider not registered")
        connection = self.repo.get(user_id, provider) or IntegrationConnection(
            user_id=user_id, provider=provider
        )
        connection.status = "connected"
        connection.scopes = scopes
        connection.metadata_ = connector.metadata()
        self.session.add(connection)
        self.session.flush()
        sealed = self.credentials.seal(credentials)
        credential = self.session.query(EncryptedCredential).filter_by(
            connection_id=connection.id
        ).one_or_none() or EncryptedCredential(
            connection_id=connection.id, ciphertext=sealed
        )
        credential.ciphertext = sealed
        self.session.add(credential)
        self.session.add(
            IntegrationAudit(user_id=user_id, provider=provider, action="connect")
        )
        self.session.commit()
        return connection

    def disconnect(self, user_id, provider):
        connection = self.repo.get(user_id, provider)
        if not connection:
            raise HTTPException(404, "Connection not found")
        connection.status = "disconnected"
        credential = (
            self.session.query(EncryptedCredential)
            .filter_by(connection_id=connection.id)
            .one_or_none()
        )
        if credential:
            credential.revoked = True
        self.session.add(
            IntegrationAudit(user_id=user_id, provider=provider, action="disconnect")
        )
        self.session.commit()

    def sync(self, user_id, provider, mode, cursor):
        connection = self.repo.get(user_id, provider)
        connector = registry.get(provider)
        if not connection or connection.status != "connected" or not connector:
            raise HTTPException(404, "Active connection not found")
        result = connector.sync(mode, cursor)
        record(self.session, connection, mode, result)
        self.session.add(
            IntegrationAudit(
                user_id=user_id, provider=provider, action="sync", detail=result
            )
        )
        self.session.commit()
        return result
