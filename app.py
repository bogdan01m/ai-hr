
import chainlit as cl
from typing import Optional
from pathlib import Path
from src.hr_agent.agent import agent
from src.shared.schemas import ProfileContext
from src.shared.chat_history import ChatHistoryManager
from src.shared.pdf_processor import PDFProcessor
from src.shared.logger_config import (
    setup_logfire,
    log_user_message,
    log_agent_response,
    log_database_operation,
    log_pdf_operation
)
from src.auth import auth_manager
# Инициализация logfire
setup_logfire()

# Используем встроенный Chainlit SQLAlchemy data layer для сессий
@cl.data_layer
def get_data_layer():
    from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
    from src.shared.database_url import get_database_url

    conninfo = get_database_url()
    return SQLAlchemyDataLayer(conninfo=conninfo)

@cl.password_auth_callback
def auth_callback(username: str, password: str) -> Optional[cl.User]:
    """Callback для авторизации Chainlit"""
    # Валидация входных данных
    if not username or not password:
        return None

    if len(username.strip()) == 0 or len(password.strip()) == 0:
        return None

    # Проверка силы пароля (минимум 4 символа для простоты)
    if len(password) < 4:
        return None

    return auth_manager.authenticate(username.strip(), password.strip())

@cl.on_chat_start
async def start():
    # Создаем контекст профиля для сессии
    profile_context = ProfileContext()
    cl.user_session.set("profile_context", profile_context)

    # Инициализируем менеджер истории чата
    chat_manager = ChatHistoryManager()
    cl.user_session.set("chat_manager", chat_manager)

    # Инициализируем пустую историю сообщений для новой сессии
    cl.user_session.set("message_history", [])

    welcome_message = """👋 Здравствуйте! Я помогу вам создать профиль идеального кандидата для вашей вакансии.

📎 **Дополнительно**: Вы можете прикрепить PDF файл с информацией о вашей компании (до 100,000 токенов) используя кнопку прикрепления файлов. Это поможет мне лучше понять специфику бизнеса и адаптировать вопросы под вашу организацию.

Мы последовательно пройдем через несколько разделов:
1. **Информация о позиции** - название, требуемый опыт и сфера деятельности
2. **Hard Skills** - профессиональные/технические навыки и инструменты
3. **Soft Skills** - личностные качества и навыки коммуникации
4. **Условия работы** - формат, зарплата, бенефиты

Давайте начнем! На какую позицию вы ищете кандидата? Укажите название должности и сколько лет опыта должно быть у кандидата."""

    await cl.Message(content=welcome_message).send()



@cl.on_message
async def main(message: cl.Message):
    # Получаем контекст профиля и менеджер истории из сессии
    profile_context = cl.user_session.get("profile_context")
    chat_manager = cl.user_session.get("chat_manager")

    if profile_context is None:
        profile_context = ProfileContext()
        cl.user_session.set("profile_context", profile_context)

    if chat_manager is None:
        chat_manager = ChatHistoryManager()
        cl.user_session.set("chat_manager", chat_manager)

    # Получаем session_id для Chainlit
    session_id = cl.context.session.id

    # Обрабатываем прикрепленные файлы
    pdf_status_message = None
    if message.elements:
        for element in message.elements:
            if isinstance(element, cl.File) and element.name.lower().endswith('.pdf'):
                try:
                    # Инициализируем PDF процессор
                    pdf_processor = PDFProcessor()

                    # Обрабатываем PDF
                    pdf_path = Path(element.path)
                    text_content, status_message = pdf_processor.process_pdf(pdf_path)

                    if text_content:
                        # Сохраняем содержимое PDF в контекст профиля
                        profile_context.company_info_pdf = text_content
                        cl.user_session.set("profile_context", profile_context)

                        log_pdf_operation(
                            "file_uploaded",
                            success=True,
                            pdf_path=str(pdf_path),
                            session_id=session_id
                        )

                        pdf_status_message = f"✅ {status_message}"
                    else:
                        log_pdf_operation(
                            "file_uploaded",
                            success=False,
                            pdf_path=str(pdf_path),
                            error=status_message,
                            session_id=session_id
                        )

                        pdf_status_message = f"❌ {status_message}"

                except Exception as e:
                    error_msg = f"Ошибка при обработке файла: {str(e)}"
                    log_pdf_operation(
                        "file_uploaded",
                        success=False,
                        pdf_path=element.path,
                        error=error_msg,
                        session_id=session_id
                    )

                    pdf_status_message = f"❌ {error_msg}"

    # Логируем пользовательское сообщение
    log_user_message(
        session_id=session_id,
        message=message.content,
        profile_context=profile_context.model_dump() if profile_context else None
    )

    # Формируем сообщение с историей для агента
    message_with_history = await chat_manager.format_history_for_agent(
        session_id=session_id,
        current_message=message.content,
        profile_context=profile_context
    )

    # Обновляем историю в user_session для следующих сообщений (Chainlit автоматически сохраняет в UI)
    message_history = cl.user_session.get("message_history", [])
    message_history.append({
        "type": "user",
        "content": message.content,
        "timestamp": None
    })
    cl.user_session.set("message_history", message_history)

    # Запускаем агент с контекстом и историей
    result = await agent.run(
        message_with_history,
        deps=profile_context
    )

    # Логируем ответ агента
    log_agent_response(
        session_id=session_id,
        response=result.output,
        profile_context=profile_context.model_dump() if profile_context else None
    )

    # Обновляем историю в user_session для следующих сообщений (Chainlit автоматически сохраняет в UI)
    message_history = cl.user_session.get("message_history", [])
    message_history.append({
        "type": "assistant",
        "content": result.output,
        "timestamp": None
    })
    cl.user_session.set("message_history", message_history)

    # Обновляем ProfileContext в user session (будет автоматически сохранен Chainlit)
    await chat_manager.update_profile_context(profile_context)

    # Добавляем информацию о PDF к ответу агента, если был загружен файл
    final_response = result.output
    if pdf_status_message:
        final_response = f"{pdf_status_message}\n\n{result.output}"

    await cl.Message(content=final_response).send()

from chainlit.types import ThreadDict

@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    print("The user resumed a previous chat session!")

    # Получаем session_id из thread
    session_id = thread["id"]

    # Инициализируем менеджер истории чата
    chat_manager = ChatHistoryManager()
    cl.user_session.set("chat_manager", chat_manager)

    # Восстанавливаем историю сообщений из ThreadDict (Chainlit's built-in persistence)
    message_history = []
    if "steps" in thread:
        for step in sorted(thread["steps"], key=lambda x: x.get("createdAt", "")):
            if step.get("type") == "user_message" and step.get("input"):
                message_history.append({
                    "type": "user",
                    "content": step["input"],
                    "timestamp": step.get("createdAt")
                })
            elif step.get("type") == "assistant_message" and step.get("output"):
                message_history.append({
                    "type": "assistant",
                    "content": step["output"],
                    "timestamp": step.get("createdAt")
                })

    # Сохраняем восстановленную историю в user_session для использования агентом
    cl.user_session.set("message_history", message_history)

    # Восстанавливаем контекст профиля из метаданных thread
    profile_context = await chat_manager.profile_saver.get_profile_context(session_id)

    if profile_context:
        cl.user_session.set("profile_context", profile_context)

        # Логируем восстановление контекста
        from src.shared.logger_config import log_database_operation
        log_database_operation("restore_profile_context", session_id, True)

        print(f"Restored profile context for session {session_id}")
        print(f"Current stage: {profile_context.current_stage}")
        print(f"Profile completion: {profile_context.get_completion_percentage():.1f}%")
    else:
        # Создаем новый контекст если не найден
        profile_context = ProfileContext()
        cl.user_session.set("profile_context", profile_context)
        print(f"Created new profile context for session {session_id}")

    print(f"Restored {len(message_history)} messages from chat history")

@cl.on_chat_end
def on_chat_end():
    print("The user disconnected!")
