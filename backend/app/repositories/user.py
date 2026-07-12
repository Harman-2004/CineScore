# user.py
# Data repository module encapsulating database operations for the User model.

from sqlalchemy.orm import Session
from app.models.user import User
from typing import Optional

class UserRepository:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        Retrieves a user profile by database ID.
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """
        Finds a user profile by email address.
        """
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        """
        Finds a user profile by username.
        """
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_by_username_or_email(db: Session, username_or_email: str) -> Optional[User]:
        """
        Finds a user profile by matching either username or email.
        """
        return db.query(User).filter(
            (User.email == username_or_email) | (User.username == username_or_email)
        ).first()

    @staticmethod
    def create(db: Session, user: User) -> User:
        """
        Persists a new user record.
        """
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
