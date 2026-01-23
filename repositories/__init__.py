"""Repository pattern package for data access layer."""

from repositories.base import BaseRepository
from repositories.user import UserRepository

__all__ = ["BaseRepository", "UserRepository"]

