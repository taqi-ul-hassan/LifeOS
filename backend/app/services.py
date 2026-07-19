from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from .events import event_bus
from .models import Goal, Profile, Task, User
from .repositories import GoalRepository, TaskRepository, UserRepository
from .schemas import GoalCreate, RegisterRequest, TaskCreate, TaskUpdate
from .security import hash_password, verify_password

class AuthService:
    def __init__(self, session: Session): self.session, self.users = session, UserRepository(session)
    def register(self, data: RegisterRequest) -> User:
        if self.users.by_email(str(data.email)): raise HTTPException(status_code=409, detail="Email already registered")
        user = self.users.add(User(email=str(data.email).lower(), password_hash=hash_password(data.password)))
        self.session.add(Profile(user_id=user.id, display_name=data.display_name)); self.session.commit(); self.session.refresh(user); return user
    def authenticate(self, email: str, password: str) -> User:
        user = self.users.by_email(email)
        if not user or not user.password_hash or not verify_password(password, user.password_hash): raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return user

class TaskService:
    def __init__(self, session: Session): self.session, self.repo = session, TaskRepository(session)
    def create(self, user_id: str, data: TaskCreate) -> Task:
        task = self.repo.add(Task(user_id=user_id, **data.model_dump())); self.session.commit(); self.session.refresh(task); event_bus.publish("task.created", user_id, task.id, {"title": task.title}); return task
    def update(self, user_id: str, task_id: str, data: TaskUpdate) -> Task:
        task = self.repo.get(task_id)
        if not task or task.user_id != user_id: raise HTTPException(status_code=404, detail="Task not found")
        for key, value in data.model_dump(exclude_unset=True).items(): setattr(task, key, value)
        if task.status == "completed" and task.completed_at is None: task.completed_at = datetime.now(timezone.utc)
        self.session.commit(); self.session.refresh(task); event_bus.publish("task.updated", user_id, task.id, {"status": task.status}); return task

class GoalService:
    def __init__(self, session: Session): self.session, self.repo = session, GoalRepository(session)
    def create(self, user_id: str, data: GoalCreate) -> Goal:
        goal = self.repo.add(Goal(user_id=user_id, **data.model_dump())); self.session.commit(); self.session.refresh(goal); event_bus.publish("goal.created", user_id, goal.id, {"title": goal.title}); return goal
