
import chainlit as cl
from src.hr_agent.agent import agent
from src.shared.schemas import ProfileContext
from src.shared.chat_history import ChatHistoryManager
from src.shared.logger_config import (
    setup_logfire,
    log_user_message,
    log_agent_response,
    log_database_operation
)
from src.database.data_layer import get_data_layer

# Инициализация logfire
setup_logfire()

# Инициализация Chainlit data layer
# @cl.data_layer
# async def init_data_layer():
#     return await get_data_layer()

@cl.on_chat_start
async def start():
    # Создаем контекст профиля для сессии
    profile_context = ProfileContext()
    cl.user_session.set("profile_context", profile_context)

    # Инициализируем менеджер истории чата
    chat_manager = ChatHistoryManager()
    cl.user_session.set("chat_manager", chat_manager)

    welcome_message = """👋 Здравствуйте! Я помогу вам создать профиль идеального кандидата для вашей вакансии.

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

    # Логируем пользовательское сообщение
    log_user_message(
        session_id=session_id,
        message=message.content,
        profile_context=profile_context.model_dump() if profile_context else None
    )

    # Сохраняем пользовательское сообщение
    try:
        await chat_manager.save_message(
            session_id=session_id,
            message_type="user",
            content=message.content,
            profile_context=profile_context
        )
        log_database_operation("save_user_message", session_id, True)
    except Exception as e:
        log_database_operation("save_user_message", session_id, False, str(e))

    # Формируем сообщение с историей для агента
    message_with_history = await chat_manager.format_history_for_agent(
        session_id=session_id,
        current_message=message.content
    )

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

    # Сохраняем ответ агента
    try:
        await chat_manager.save_message(
            session_id=session_id,
            message_type="assistant",
            content=result.output,
            profile_context=profile_context
        )
        log_database_operation("save_agent_response", session_id, True)
    except Exception as e:
        log_database_operation("save_agent_response", session_id, False, str(e))

    await cl.Message(content=result.output).send()
