from typing import Generic, TypeVar
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import Goal, Task, User

T = TypeVar("T")


class Repository(Generic[T]):
    def __init__(self, session: Session, model: type[T]):
        self.session, self.model = (session, model)

    def get(self, record_id: str) -> T | None:
        return self.session.get(self.model, record_id)

    def list_for_user(self, user_id: str) -> list[T]:
        return list(
            self.session.scalars(
                select(self.model).where(self.model.user_id == user_id)
            )
        )

    def add(self, record: T) -> T:
        self.session.add(record)
        self.session.flush()
        return record


class UserRepository(Repository[User]):
    def __init__(self, session: Session):
        super().__init__(session, User)

    def by_email(self, email: str) -> User | None:
        return self.session.scalar(select(User).where(User.email == email.lower()))


class TaskRepository(Repository[Task]):
    def __init__(self, session: Session):
        super().__init__(session, Task)


class GoalRepository(Repository[Goal]):
    def __init__(self, session: Session):
        super().__init__(session, Goal)
