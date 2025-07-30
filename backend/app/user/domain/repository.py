from abc import ABC, abstractmethod
from app.models.user import User

class UserRepository(ABC):
    @abstractmethod
    async def get_all(self):
        pass
    @abstractmethod
    async def create(self, user: User):
        pass 
