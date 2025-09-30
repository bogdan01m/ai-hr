from pydantic_ai import RunContext
from typing import List, Optional, Any, Dict

from ..shared.schemas import ProfileContext
from ..shared.logger_config import log_profile_update


async def update_position_info(
    ctx: RunContext[ProfileContext],
    title: Optional[str] = None,
    experience_years: Optional[int] = None,
    company_field: Optional[str] = None,
) -> str:
    """Обновляет информацию о позиции в профиле кандидата"""
    updates: Dict[str, Any] = {}
    if title:
        ctx.deps.profile.position.title = title
        updates["title"] = title
    if experience_years is not None:
        ctx.deps.profile.position.experience_years = experience_years
        updates["experience_years"] = experience_years
    if company_field:
        ctx.deps.profile.position.company_field = company_field
        updates["company_field"] = company_field

    stage = ctx.deps.get_current_stage()
    log_profile_update("unknown", stage, "position_info", updates)

    return f"Информация о позиции обновлена. Текущий этап: {stage}"


async def update_hard_skills(
    ctx: RunContext[ProfileContext],
    programming_languages: Optional[List[str]] = None,
    frameworks: Optional[List[str]] = None,
    tools: Optional[List[str]] = None,
    certifications: Optional[List[str]] = None,
) -> str:
    """Обновляет технические навыки в профиле кандидата"""
    if programming_languages:
        ctx.deps.profile.hard_skills.programming_languages = programming_languages
    if frameworks:
        ctx.deps.profile.hard_skills.frameworks = frameworks
    if tools:
        ctx.deps.profile.hard_skills.tools = tools
    if certifications:
        ctx.deps.profile.hard_skills.certifications = certifications

    return f"Технические навыки обновлены. Текущий этап: {ctx.deps.get_current_stage()}"


async def update_soft_skills(
    ctx: RunContext[ProfileContext],
    personal_qualities: Optional[List[str]] = None,
    communication_skills: Optional[List[str]] = None,
    team_skills: Optional[List[str]] = None,
    leadership_skills: Optional[List[str]] = None,
) -> str:
    """Обновляет личностные навыки в профиле кандидата"""
    if personal_qualities:
        ctx.deps.profile.soft_skills.personal_qualities = personal_qualities
    if communication_skills:
        ctx.deps.profile.soft_skills.communication_skills = communication_skills
    if team_skills:
        ctx.deps.profile.soft_skills.team_skills = team_skills
    if leadership_skills:
        ctx.deps.profile.soft_skills.leadership_skills = leadership_skills

    return f"Личностные навыки обновлены. Текущий этап: {ctx.deps.get_current_stage()}"


async def update_work_conditions(
    ctx: RunContext[ProfileContext],
    work_format: Optional[str] = None,
    salary_expectations: Optional[str] = None,
    benefits: Optional[List[str]] = None,
    travel_readiness: Optional[bool] = None,
) -> str:
    """Обновляет условия работы в профиле кандидата"""
    if work_format:
        ctx.deps.profile.work_conditions.work_format = work_format
    if salary_expectations:
        ctx.deps.profile.work_conditions.salary_expectations = salary_expectations
    if benefits:
        ctx.deps.profile.work_conditions.benefits = benefits
    if travel_readiness is not None:
        ctx.deps.profile.work_conditions.travel_readiness = travel_readiness

    return f"Условия работы обновлены. Текущий этап: {ctx.deps.get_current_stage()}"


async def get_profile_status(ctx: RunContext[ProfileContext]) -> str:
    """Получает текущий статус заполнения профиля"""
    stage = ctx.deps.get_current_stage()
    profile = ctx.deps.profile

    if stage == "complete":
        return f"""
ПРОФИЛЬ КАНДИДАТА ЗАВЕРШЕН:

ПОЗИЦИЯ:
- Название: {profile.position.title}
- Опыт: {profile.position.experience_years} лет
- Сфера: {profile.position.company_field}

ТЕХНИЧЕСКИЕ НАВЫКИ:
- Языки: {profile.hard_skills.programming_languages or 'Не указано'}
- Фреймворки: {profile.hard_skills.frameworks or 'Не указано'}
- Инструменты: {profile.hard_skills.tools or 'Не указано'}
- Сертификации: {profile.hard_skills.certifications or 'Не указано'}

ЛИЧНОСТНЫЕ НАВЫКИ:
- Качества: {profile.soft_skills.personal_qualities or 'Не указано'}
- Коммуникация: {profile.soft_skills.communication_skills or 'Не указано'}
- Работа в команде: {profile.soft_skills.team_skills or 'Не указано'}
- Лидерство: {profile.soft_skills.leadership_skills or 'Не указано'}

УСЛОВИЯ РАБОТЫ:
- Формат: {profile.work_conditions.work_format}
- Зарплата: {profile.work_conditions.salary_expectations}
- Бенефиты: {profile.work_conditions.benefits or 'Не указано'}
- Готовность к командировкам: {profile.work_conditions.travel_readiness}
"""
    else:
        return f"Текущий этап: {stage}. Профиль заполнен не полностью."
