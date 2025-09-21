import os
import logfire
from dotenv import load_dotenv

load_dotenv()

def setup_logfire():
    """Настройка логирования через Logfire"""
    logfire_token = os.getenv("LOGFIRE_TOKEN")

    if logfire_token:
        logfire.configure(
            token=logfire_token,
            project_name=os.getenv("LOGFIRE_PROJECT_NAME", "ai-hr"),
            service_name=os.getenv("LOGFIRE_SERVICE_NAME", "hr-chatbot"),
            environment=os.getenv("LOGFIRE_ENV", "development"),
        )
        logfire.info("Logfire настроен успешно")
        return True
    else:
        print("LOGFIRE_TOKEN не найден. Логирование в Logfire отключено.")
        return False

def log_user_message(session_id: str, message: str, profile_context: dict = None):
    """Логирование пользовательского сообщения"""
    logfire.info(
        "User message received",
        session_id=session_id,
        message=message,
        profile_context=profile_context
    )

def log_agent_response(session_id: str, response: str, profile_context: dict = None):
    """Логирование ответа агента"""
    logfire.info(
        "Agent response sent",
        session_id=session_id,
        response=response,
        profile_context=profile_context
    )

def log_database_operation(operation: str, session_id: str, success: bool, error: str = None):
    """Логирование операций с базой данных"""
    if success:
        logfire.info(
            f"Database operation: {operation}",
            session_id=session_id,
            operation=operation,
            success=success
        )
    else:
        logfire.error(
            f"Database operation failed: {operation}",
            session_id=session_id,
            operation=operation,
            success=success,
            error=error
        )

def log_profile_update(session_id: str, stage: str, update_type: str, data: dict = None):
    """Логирование обновлений профиля"""
    logfire.info(
        "Profile updated",
        session_id=session_id,
        current_stage=stage,
        update_type=update_type,
        data=data
    )