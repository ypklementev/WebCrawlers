# Async Web Crawler + FastAPI + WebSockets

Веб-краулер на Python с асинхронностью, отображением прогресса в реальном времени и веб-интерфейсом.

## Возможности

✔ Асинхронный обход сайта  
✔ Live-прогресс через WebSocket  
✔ Группировка URL по HTTP-кодам  
✔ Tailwind + Alpine.js UI  
✔ Не блокирует сервер  
✔ Работает локально

---

## Технологии

- **Python 3.10+**
- **FastAPI** — REST + WebSocket API
- **aiohttp** — асинхронный HTTP-клиент
- **asyncio** — управление задачами
- **BeautifulSoup4** — парсинг HTML
- **Tailwind CSS + Alpine.js** — фронтенд

---

## Установка и запуск

### 1) Клонировать репозиторий

```sh
git clone https://github.com/you/your-repo.git
cd your-repo
```

### 2) Создать виртуальное окружение (по желанию)
```sh
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows
```

### 3) Установить зависимости
```sh
pip install -r requirements.txt
```

### 4) Запустить сервер
```sh
python server.py
```

### Сервер будет доступен на:
```
http://localhost:8000
```

---
## Как это работает

### 1. Клиент отправляет запрос:
```json
POST /crawl
{ "url": "https://example.com" }
```

### Сервер отвечает:
```json
{ "task_id": "..." }
```

### 2. UI подключается к WebSocket:
```
ws://localhost:8000/ws/<task_id>
```

### 3. Во время выполнения WebSocket присылает прогресс:
```json
{ "type": "progress", "processed": 12, "found": 30 }
```

### 4. После завершения:
```json
{
  "type": "finished",
  "results": {
    "200": [...],
    "302": [...],
    "-1": [...]
  }
}
```

---
## Структура проекта

```
.
├── crawler.py          # асинхронный краулер
├── server.py           # FastAPI + WebSockets
├── static/
│   └── index.html      # UI на Tailwind + Alpine.js
├── requirements.txt
└── README.md
```
---
## Ограничения

	•	SPA-сайты (Vue/React) без JS-рендера не анализируются
	•	Нет кнопки остановки crawl
	•	Нет ограничения глубины