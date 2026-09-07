# Тесты tajik-fire

Папка `tests/` содержит все тесты платформы, разделённые по уровням.

## Структура

```
tests/
├── conftest.py                       # общие фикстуры (db, client, auth_token)
├── unit/                             # unit-тесты (быстрые, без БД/сети)
│   ├── test_password_service.py      #   валидация пароля
│   ├── test_verifiers.py             #   сравнение вывода судьи
│   ├── test_email_service.py         #   генерация кодов и email
│   └── test_config.py                #   конфигурация
├── integration/                      # интеграционные тесты API
│   ├── test_auth_api.py              #   регистрация, логин, refresh, me
│   ├── test_problems_api.py          #   задачи, категории, сабмиты
│   ├── test_tasks_api.py             #   CRUD личных задач
│   ├── test_messenger_api.py         #   чаты, сообщения
│   ├── test_friends_api.py           #   друзья, заявки
│   ├── test_judger_api.py            #   полный пайплайн судьи
│   ├── test_ai_assistant_api.py      #   AI ассистент (placeholder)
│   └── test_stats_api.py             #   дашборд, рейтинг, фид
├── e2e/                              # E2E через Playwright (UI)
│   └── test_user_journey.py          #   пользовательский путь
└── load/                             # нагрузочные тесты
    └── locustfile.py                 #   Locust-сценарии
```

## Запуск

### Установка зависимостей

```bash
pip install pytest pytest-asyncio httpx
# для E2E:
pip install playwright
python -m playwright install chromium
# для load:
pip install locust
```

### Все unit + integration тесты

```bash
cd tajik-fire.github.io
pytest tests/unit tests/integration -v
```

### Только unit-тесты

```bash
pytest tests/unit -v
```

### Только интеграционные

```bash
pytest tests/integration -v
```

### E2E (нужен запущенный backend)

```bash
# Терминал 1:
cd fastapi_app && uvicorn main:app --reload

# Терминал 2:
pytest tests/e2e -v
```

### Нагрузочные (Locust)

```bash
# Терминал 1:
cd fastapi_app && uvicorn main:app --reload

# Терминал 2:
cd tests/load && locust -f locustfile.py --host=http://localhost:8000
# Откройте http://localhost:8089 для настройки
```

## Покрытие

| Уровень      | Что проверяет                                            |
|--------------|----------------------------------------------------------|
| unit         | изолированные функции: пароль, вердикт, email, конфиг   |
| integration  | каждый эндпоинт API: статус-коды, ошибки, бизнес-логика |
| e2e          | UI пользовательский путь в реальном браузере           |
| load         | поведение под нагрузкой: RPS, латентность, ошибки       |

## Чему посвящены тесты

- **Аутентификация** — слабые пароли отклоняются, дубли не проходят,
  JWT валидируется, неавторизованные запросы блокируются.
- **Судья** — корректный код получает `accepted`, неправильный —
  `wrong_answer`, полный пайплайн от submit до verdict.
- **Мессенджер** — нельзя отправить сообщение без получателя,
  нельзя открыть чужой чат, можно увидеть онлайн-пользователей.
- **Друзья** — нельзя добавить себя в друзья, заявка несуществующему
  пользователю возвращает 404.
- **AI ассистент** — `/status` говорит, что AI пока не доступен,
  `/chat` возвращает заглушку на правильном языке.
- **Статистика** — дашборд отдаёт корректные счётчики, leaderboard
  отсортирован, фид живой.
- **E2E** — главная рендерится, навбар присутствует, переключатель
  языка доступен, AI-кнопка видна, логин с демо-аккаунтом работает.
