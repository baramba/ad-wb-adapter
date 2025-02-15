tags = [
    {
        "name": "campaigns",
        "description": "Управление рекламными кампаниями.",
    },
    {
        "name": "jobs",
        "description": "Работа с задачами.",
    },
    {
        "name": "supplier",
        "description": "Методы для работы с данными пользователей wildberries.",
    },
    {
        "name": "stake",
        "description": "Методы для работы со ставками.",
    },
    {
        "name": "about",
        "description": "Информация о сервисе.",
    },
]

description: str = """
# Сервис wb-adapter получает задание на выполнение операций на стороне wildberries.

## Реализованные следующие методы:
  - создать рекламную кампанию;
  - получить результат выполнения задания по job_id;
  - получить access wb_token;
  - методы для управления ставками на торгах;
"""
