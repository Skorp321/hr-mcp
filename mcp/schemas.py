"""Pydantic-схемы для валидации контрактов MCP-инструментов."""

from typing import Optional

from pydantic import BaseModel, Field


# --- Входные схемы ---


class HrRagSearchInput(BaseModel):
    """Входные данные для RAG-поиска по HR-документам."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Поисковый запрос на естественном языке",
    )
    n_results: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Максимальное количество документов в ответе",
    )


class GetPersonalDaysInput(BaseModel):
    """Входные данные для получения персональных дней."""

    login: Optional[str] = Field(
        default=None,
        pattern=r"^[a-z][a-z0-9_]{0,49}$",
        description="Логин пользователя (латиница, цифры, подчёркивание) или None для всех",
    )


class GetRemainingVacationDaysInput(BaseModel):
    """Входные данные для получения оставшихся дней отпуска."""

    login: str = Field(
        ...,
        min_length=1,
        max_length=50,
        pattern=r"^[a-z][a-z0-9_]*$",
        description="Логин пользователя (латиница, цифры, подчёркивание)",
    )


# --- Выходные схемы ---


class RagDocumentResult(BaseModel):
    """Один документ в результатах RAG-поиска."""

    text: str = Field(..., description="Текст документа")
    relevance: float = Field(..., ge=0, le=1, description="Релевантность (0-1)")
    topic: str = Field(..., description="Тема документа")


class HrRagSearchOutput(BaseModel):
    """Результат RAG-поиска по HR-документам."""

    query: str = Field(..., description="Исходный запрос")
    results: list[RagDocumentResult] = Field(
        default_factory=list,
        description="Найденные документы",
    )


class PersonalDayItem(BaseModel):
    """Один персональный день."""

    date: str = Field(..., description="Дата в формате YYYY-MM-DD")
    reason: str = Field(..., description="Причина (день рождения, годовщина и т.д.)")
    used: bool = Field(..., description="Использован ли день")


class EmployeePersonalDays(BaseModel):
    """Персональные дни сотрудника."""

    employee_id: str = Field(..., description="ID сотрудника")
    login: str = Field(..., description="Логин")
    employee_name: str = Field(..., description="ФИО")
    personal_days: list[PersonalDayItem] = Field(
        default_factory=list,
        description="Список персональных дней",
    )
    total_available: int = Field(..., ge=0, description="Всего доступно")
    used_count: Optional[int] = Field(default=None, ge=0, description="Использовано")


class GetPersonalDaysOutput(BaseModel):
    """Результат получения персональных дней."""

    items: list[EmployeePersonalDays] = Field(
        default_factory=list,
        description="Персональные дни по сотрудникам",
    )


class VacationDaysRecord(BaseModel):
    """Запись об отпуске сотрудника."""

    employee_id: str = Field(..., description="ID сотрудника")
    login: str = Field(..., description="Логин")
    employee_name: str = Field(..., description="ФИО")
    year: int = Field(..., description="Год")
    total_days: int = Field(..., ge=0, description="Всего дней отпуска")
    used_days: int = Field(..., ge=0, description="Использовано")
    remaining_days: int = Field(..., ge=0, description="Осталось")
    planned_days: int = Field(..., ge=0, description="Запланировано")
    carry_over_from_prev_year: int = Field(
        0,
        ge=0,
        description="Перенос с прошлого года",
    )


class GetRemainingVacationDaysOutput(BaseModel):
    """Результат получения оставшихся дней отпуска."""

    items: list[VacationDaysRecord] = Field(
        default_factory=list,
        description="Данные по отпуску",
    )


class ValidationErrorOutput(BaseModel):
    """Ошибка валидации."""

    error: str = Field("ValidationError", description="Тип ошибки")
    details: list[str] = Field(default_factory=list, description="Детали ошибок")
