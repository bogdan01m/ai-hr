from pydantic_ai import Agent, RunContext
from typing import List
from dotenv import load_dotenv

from schemas import ProfileContext, WorkFormat
from prompt import SYSTEM_PROMPT
from logger_config import log_profile_update

load_dotenv()

agent = Agent(
    'openai:gpt-5-mini',
    system_prompt=SYSTEM_PROMPT,
    deps_type=ProfileContext,
    instrument=True
)

@agent.tool
def update_position_info(ctx: RunContext[ProfileContext], title: str = None,
                        experience_years: int = None, company_field: str = None) -> str:
    """Обновляет информацию о позиции в профиле кандидата"""
    updates = {}
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

@agent.tool
def update_hard_skills(ctx: RunContext[ProfileContext], programming_languages: List[str] = None,
                      frameworks: List[str] = None, tools: List[str] = None,
                      certifications: List[str] = None) -> str:
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

@agent.tool
def update_soft_skills(ctx: RunContext[ProfileContext], personal_qualities: List[str] = None,
                      communication_skills: List[str] = None, team_skills: List[str] = None,
                      leadership_skills: List[str] = None) -> str:
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

@agent.tool
def update_work_conditions(ctx: RunContext[ProfileContext], work_format: str = None,
                          salary_expectations: str = None, benefits: List[str] = None,
                          travel_readiness: bool = None) -> str:
    """Обновляет условия работы в профиле кандидата"""
    if work_format:
        ctx.deps.profile.work_conditions.work_format = WorkFormat(work_format.lower())
    if salary_expectations:
        ctx.deps.profile.work_conditions.salary_expectations = salary_expectations
    if benefits:
        ctx.deps.profile.work_conditions.benefits = benefits
    if travel_readiness is not None:
        ctx.deps.profile.work_conditions.travel_readiness = travel_readiness

    return f"Условия работы обновлены. Текущий этап: {ctx.deps.get_current_stage()}"

@agent.tool
def get_profile_status(ctx: RunContext[ProfileContext]) -> str:
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
