from app.models.user import User
from app.user.domain.repository import UserRepository
from app.user.application.schema import UserCreate
from app.user.application.exception import UserNotFoundException

async def get_users(repo: UserRepository):
    users = await repo.get_all()
    if not users:
        raise UserNotFoundException("No users found")
    return users

async def create_user(repo: UserRepository, user_create: UserCreate):
    user = User(username=user_create.username, email=user_create.email)
    return await repo.create(user) 
