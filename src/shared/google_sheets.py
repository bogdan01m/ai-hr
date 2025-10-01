import os
import gspread
from datetime import datetime
from typing import Optional
import logfire

from .schemas import CandidateProfile


class GoogleSheetsManager:
    """Менеджер для работы с Google Sheets"""

    def __init__(self, spreadsheet_id: str, credentials_path: Optional[str] = None):
        self.spreadsheet_id = spreadsheet_id
        self.credentials_path = credentials_path or os.getenv("GOOGLE_CREDENTIALS_PATH")
        self._client: Optional[gspread.Client] = None
        self._sheet: Optional[gspread.Worksheet] = None

    def _get_client(self) -> gspread.Client:
        """Получить клиент gspread"""
        if self._client is None:
            if self.credentials_path and os.path.exists(self.credentials_path):
                # Использование service account
                self._client = gspread.service_account(filename=self.credentials_path)
            else:
                # Fallback на OAuth (требует настройки)
                self._client = gspread.oauth()
        return self._client

    def _get_sheet(self, worksheet_name: str = "Лист1") -> gspread.Worksheet:
        """Получить лист таблицы"""
        if self._sheet is None:
            client = self._get_client()
            spreadsheet = client.open_by_key(self.spreadsheet_id)
            try:
                self._sheet = spreadsheet.worksheet(worksheet_name)
            except gspread.WorksheetNotFound:
                # Создать лист если не существует
                self._sheet = spreadsheet.add_worksheet(
                    title=worksheet_name, rows=1000, cols=10
                )
                # Добавить заголовки
                headers = [
                    "ID профиля",
                    "Дата создания",
                    "Позиция",
                    "Hard skills",
                    "Soft skills",
                    "Условия работы",
                ]
                self._sheet.append_row(headers)
        return self._sheet

    def save_profile(self, profile: CandidateProfile, profile_id: str) -> bool:
        """
        Сохранить профиль в Google Sheets

        Args:
            profile: Профиль кандидата
            profile_id: Уникальный ID профиля

        Returns:
            bool: True если успешно сохранено
        """
        try:
            sheet = self._get_sheet()

            # Форматирование данных
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Позиция
            position_text = f"{profile.position.title or 'Не указано'} ({profile.position.experience_years or 0} лет опыта, {profile.position.company_field or 'Не указано'})"

            # Hard skills
            hard_skills_parts = []
            if profile.hard_skills.programming_languages:
                hard_skills_parts.append(
                    f"Языки: {', '.join(profile.hard_skills.programming_languages)}"
                )
            if profile.hard_skills.frameworks:
                hard_skills_parts.append(
                    f"Фреймворки: {', '.join(profile.hard_skills.frameworks)}"
                )
            if profile.hard_skills.tools:
                hard_skills_parts.append(
                    f"Инструменты: {', '.join(profile.hard_skills.tools)}"
                )
            if profile.hard_skills.certifications:
                hard_skills_parts.append(
                    f"Сертификации: {', '.join(profile.hard_skills.certifications)}"
                )
            hard_skills_text = (
                "; ".join(hard_skills_parts) if hard_skills_parts else "Не указано"
            )

            # Soft skills
            soft_skills_parts = []
            if profile.soft_skills.personal_qualities:
                soft_skills_parts.append(
                    f"Качества: {', '.join(profile.soft_skills.personal_qualities)}"
                )
            if profile.soft_skills.communication_skills:
                soft_skills_parts.append(
                    f"Коммуникация: {', '.join(profile.soft_skills.communication_skills)}"
                )
            if profile.soft_skills.team_skills:
                soft_skills_parts.append(
                    f"Команда: {', '.join(profile.soft_skills.team_skills)}"
                )
            if profile.soft_skills.leadership_skills:
                soft_skills_parts.append(
                    f"Лидерство: {', '.join(profile.soft_skills.leadership_skills)}"
                )
            soft_skills_text = (
                "; ".join(soft_skills_parts) if soft_skills_parts else "Не указано"
            )

            # Условия работы
            work_conditions_parts = []
            if profile.work_conditions.work_format:
                work_conditions_parts.append(
                    f"Формат: {profile.work_conditions.work_format}"
                )
            if profile.work_conditions.salary_expectations:
                work_conditions_parts.append(
                    f"ЗП: {profile.work_conditions.salary_expectations}"
                )
            if profile.work_conditions.benefits:
                work_conditions_parts.append(
                    f"Бенефиты: {', '.join(profile.work_conditions.benefits)}"
                )
            if profile.work_conditions.travel_readiness is not None:
                travel_text = (
                    "Да" if profile.work_conditions.travel_readiness else "Нет"
                )
                work_conditions_parts.append(f"Командировки: {travel_text}")
            work_conditions_text = (
                "; ".join(work_conditions_parts)
                if work_conditions_parts
                else "Не указано"
            )

            # Добавить строку
            row_data = [
                profile_id,
                current_date,
                position_text,
                hard_skills_text,
                soft_skills_text,
                work_conditions_text,
            ]

            sheet.append_row(row_data)
            logfire.info(f"Profile {profile_id} saved to Google Sheets successfully")
            return True

        except Exception as e:
            logfire.error(f"Failed to save profile to Google Sheets: {e}")
            return False


# Глобальный экземпляр менеджера
_sheets_manager = None


def get_sheets_manager() -> Optional[GoogleSheetsManager]:
    """Получить экземпляр менеджера Google Sheets"""
    global _sheets_manager

    if _sheets_manager is None:
        spreadsheet_id = os.getenv("GOOGLE_SPREADSHEET_ID")
        if spreadsheet_id:
            _sheets_manager = GoogleSheetsManager(spreadsheet_id)

    return _sheets_manager
