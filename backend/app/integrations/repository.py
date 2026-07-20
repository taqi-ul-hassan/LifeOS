from sqlalchemy import select
from .models import IntegrationConnection


class IntegrationRepository:
    def __init__(self, session):
        self.session = session

    def get(self, user_id, provider):
        return self.session.scalar(
            select(IntegrationConnection).where(
                IntegrationConnection.user_id == user_id,
                IntegrationConnection.provider == provider,
            )
        )

    def list(self, user_id):
        return list(
            self.session.scalars(
                select(IntegrationConnection).where(
                    IntegrationConnection.user_id == user_id
                )
            )
        )
