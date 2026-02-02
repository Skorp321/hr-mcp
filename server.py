#!/usr/bin/env python3
"""MCP HR Server - сервер с RAG и инструментами для HR-данных."""

from typing import Optional

from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError

from mock_data import get_personal_days, get_remaining_vacation_days
from rag import rag_search
from schemas import (
    EmployeePersonalDays,
    GetPersonalDaysInput,
    GetPersonalDaysOutput,
    GetRemainingVacationDaysInput,
    GetRemainingVacationDaysOutput,
    HrRagSearchInput,
    HrRagSearchOutput,
    RagDocumentResult,
    ValidationErrorOutput,
    VacationDaysRecord,
)

mcp = FastMCP(
    name="HR MCP Server",
    json_response=True,
)


def _validation_error_response(exc: ValidationError) -> str:
    """Форматирование ошибок валидации через выходную схему."""
    errors = [".".join(str(x) for x in e["loc"]) + ": " + e["msg"] for e in exc.errors()]
    output = ValidationErrorOutput(details=errors)
    return output.model_dump_json(by_alias=False, exclude_none=True, ensure_ascii=False)


@mcp.tool()
def hr_rag_search(query: str, n_results: int = 5) -> str:
    """
    Поиск по HR-документам и политикам с помощью RAG (Retrieval Augmented Generation).
    
    Использует семантический поиск по базе HR-документов: политики отпусков,
    персональные дни, больничные, удалённая работа, приём на работу,
    командировки и льготы.
    
    Args:
        query: Поисковый запрос на естественном языке (например: "сколько дней отпуска", "как оформить больничный")
        n_results: Максимальное количество документов в ответе (по умолчанию 5)
    
    Returns:
        Релевантные фрагменты документов с указанием степени релевантности
    """
    try:
        validated_input = HrRagSearchInput(query=query, n_results=n_results)
    except ValidationError as e:
        return _validation_error_response(e)
    results = rag_search(query=validated_input.query, n_results=validated_input.n_results)
    output = HrRagSearchOutput(
        query=validated_input.query,
        results=[RagDocumentResult(**r) for r in results],
    )
    return output.model_dump_json(by_alias=False, exclude_none=True, ensure_ascii=False)


@mcp.tool()
def get_personal_days_tool(login: Optional[str] = None) -> str:
    """
    Получить персональные дни сотрудника или всех сотрудников.
    
    Персональные дни - дополнительные выходные (день рождения, годовщина в компании и т.д.)
    
    Args:
        login: Логин пользователя (ivanov, petrova, sidorov) или None для всех сотрудников
    
    Returns:
        Список персональных дней с датами, причинами и статусом использования
    """
    try:
        validated_input = GetPersonalDaysInput(login=login)
    except ValidationError as e:
        return _validation_error_response(e)
    data = get_personal_days(login=validated_input.login)
    items = [EmployeePersonalDays(**item) for item in data]
    output = GetPersonalDaysOutput(items=items)
    return output.model_dump_json(by_alias=False, exclude_none=True, ensure_ascii=False)


@mcp.tool()
def get_remaining_vacation_days_tool(login: str) -> str:
    """
    Получить оставшиеся дни отпуска сотрудника за текущий год.
    
    Args:
        login: Логин пользователя (ivanov, petrova, sidorov)
    
    Returns:
        Информация об отпуске: всего дней, использовано, осталось, запланировано
    """
    try:
        validated_input = GetRemainingVacationDaysInput(login=login)
    except ValidationError as e:
        return _validation_error_response(e)
    data = get_remaining_vacation_days(login=validated_input.login)
    items = [VacationDaysRecord(**item) for item in data]
    output = GetRemainingVacationDaysOutput(items=items)
    return output.model_dump_json(by_alias=False, exclude_none=True, ensure_ascii=False)


def main():
    """Точка входа для запуска сервера."""
    import os
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport == "http":
        # Для общения через curl: MCP_TRANSPORT=http python server.py
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
