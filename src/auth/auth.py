"""
Модуль авторизации для AI HR Assistant
"""

import os
import bcrypt
import chainlit as cl
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class User:
    """Класс пользователя"""

    username: str
    hashed_password: str
    role: str
    metadata: Optional[Dict[str, Any]] = None


class AuthManager:
    """Менеджер авторизации"""

    def __init__(self):
        self._users = {}
        self._load_users_from_env()

    def _load_users_from_env(self):
        """Загружаем пользователей из переменных окружения"""
        username = os.getenv("CHAINLIT_USER_NAME", "admin")
        password = os.getenv("CHAINLIT_USER_PASSWORD", "admin")

        # Хешируем пароль
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        # Добавляем пользователя
        self._users[username] = User(
            username=username,
            hashed_password=hashed_password,
            role="admin",
            metadata={"provider": "credentials"},
        )

    def verify_password(self, plain_password: str, hashed_password: bytes) -> bool:
        """Проверяем пароль"""
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password)

    def authenticate(self, username: str, password: str) -> Optional[cl.User]:
        """Аутентификация пользователя"""
        user = self._users.get(username)
        if user and self.verify_password(password, user.hashed_password):
            return cl.User(
                identifier=user.username,
                metadata={"role": user.role, "provider": "credentials"},
            )
        return None

    def add_user(self, username: str, password: str, role: str = "user") -> bool:
        """Добавляем нового пользователя"""
        if username in self._users:
            return False

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        self._users[username] = User(
            username=username, hashed_password=hashed_password, role=role
        )
        return True

    def get_user(self, username: str) -> Optional[User]:
        """Получаем пользователя по имени"""
        return self._users.get(username)


# Создаем глобальный экземпляр менеджера авторизации
auth_manager = AuthManager()
