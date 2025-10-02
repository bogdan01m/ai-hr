import os
import json
import tempfile
import gspread
from datetime import datetime
from typing import Optional
import logfire

from .schemas import CandidateProfile


class GoogleSheetsManager:
    """Менеджер для работы с Google Sheets"""

    def __init__(self, spreadsheet_id: str):
        self.spreadsheet_id = spreadsheet_id
        self._client: Optional[gspread.Client] = None
        self._sheet: Optional[gspread.Worksheet] = None

    def _get_client(self) -> gspread.Client:
        """Получить клиент gspread"""
        if self._client is None:
            # Попробовать собрать credentials из отдельных переменных окружения
            google_type = os.getenv("GOOGLE_TYPE", "service_account")
            project_id = os.getenv("GOOGLE_PROJECT_ID")
            private_key_id = os.getenv("GOOGLE_PRIVATE_KEY_ID")
            private_key = os.getenv("GOOGLE_PRIVATE_KEY")
            client_email = os.getenv("GOOGLE_CLIENT_EMAIL")
            client_id = os.getenv("GOOGLE_CLIENT_ID")
            auth_uri = os.getenv(
                "GOOGLE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"
            )
            token_uri = os.getenv(
                "GOOGLE_TOKEN_URI", "https://oauth2.googleapis.com/token"
            )
            auth_provider_x509_cert_url = os.getenv(
                "GOOGLE_AUTH_PROVIDER_X509_CERT_URL",
                "https://www.googleapis.com/oauth2/v1/certs",
            )
            client_x509_cert_url = os.getenv("GOOGLE_CLIENT_X509_CERT_URL")
            universe_domain = os.getenv("GOOGLE_UNIVERSE_DOMAIN", "googleapis.com")

            if all([project_id, private_key_id, private_key, client_email, client_id]):
                try:
                    # Собрать JSON из отдельных переменных
                    credentials_data = {
                        "type": google_type,
                        "project_id": project_id,
                        "private_key_id": private_key_id,
                        "private_key": private_key,
                        "client_email": client_email,
                        "client_id": client_id,
                        "auth_uri": auth_uri,
                        "token_uri": token_uri,
                        "auth_provider_x509_cert_url": auth_provider_x509_cert_url,
                        "client_x509_cert_url": client_x509_cert_url
                        or (
                            f"https://www.googleapis.com/robot/v1/metadata/x509/{client_email.replace('@', '%40')}"
                            if client_email
                            else None
                        ),
                        "universe_domain": universe_domain,
                    }

                    # Создать временный файл с credentials
                    with tempfile.NamedTemporaryFile(
                        mode="w", suffix=".json", delete=False
                    ) as temp_file:
                        json.dump(credentials_data, temp_file)
                        temp_path = temp_file.name

                    self._client = gspread.service_account(filename=temp_path)
                    # Удалить временный файл
                    os.unlink(temp_path)
                    logfire.info(
                        "Google Sheets client initialized from environment variables"
                    )
                except Exception as e:
                    logfire.error(
                        f"Failed to create credentials from environment variables: {e}"
                    )
                    # Fallback на OAuth
                    self._client = gspread.oauth()
                    logfire.info(
                        "Google Sheets client initialized with OAuth (fallback)"
                    )
            else:
                # Fallback на OAuth (требует настройки)
                self._client = gspread.oauth()
                logfire.info("Google Sheets client initialized with OAuth")
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
