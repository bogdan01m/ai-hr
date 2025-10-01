import os
from typing import Optional
import logfire
from dotenv import load_dotenv

load_dotenv()


def setup_logfire():
    """Настройка логирования через Logfire"""
    logfire_token = os.getenv("LOGFIRE_TOKEN")

    # Всегда настраиваем logfire, но отправляем на сервер только при наличии токена
    logfire.configure(
        token=logfire_token,  # Может быть None
        service_name=os.getenv("LOGFIRE_SERVICE_NAME", "hr-chatbot"),
        environment=os.getenv("LOGFIRE_ENV", "development"),
        send_to_logfire="if-token-present",  # Отправляет только при наличии токена
    )

    if logfire_token:
        logfire.info("Logfire настроен с отправкой на сервер")
        return True
    else:
        logfire.info(
            "Logfire настроен только для локального логирования (токен не найден)"
        )
        return False


def log_user_message(
    session_id: str, message: str, profile_context: Optional[dict] = None
):
    """Логирование пользовательского сообщения"""
    logfire.info(
        "User message received",
        session_id=session_id,
        message=message,
        profile_context=profile_context,
    )


def log_agent_response(
    session_id: str, response: str, profile_context: Optional[dict] = None
):
    """Логирование ответа агента"""
    logfire.info(
        "Agent response sent",
        session_id=session_id,
        response=response,
        profile_context=profile_context,
    )


def log_database_operation(
    operation: str, session_id: str, success: bool, error: Optional[str] = None
):
    """Логирование операций с базой данных"""
    if success:
        logfire.info(
            f"Database operation: {operation}",
            session_id=session_id,
            operation=operation,
            success=success,
        )
    else:
        logfire.error(
            f"Database operation failed: {operation}",
            session_id=session_id,
            operation=operation,
            success=success,
            error=error,
        )


def log_profile_update(
    session_id: str, stage: str, update_type: str, data: Optional[dict] = None
):
    """Логирование обновлений профиля"""
    logfire.info(
        "Profile updated",
        session_id=session_id,
        current_stage=stage,
        update_type=update_type,
        data=data,
    )
