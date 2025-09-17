# ToolsOpenVerse

![OpenVerse Logo](https://raw.githubusercontent.com/Javicle/OpenVerse/main/assets/logo.png)

## 🚀 Описание
**ToolsOpenVerse** — это набор утилит и библиотек для микросервисной архитектуры OpenVerse. Проект предоставляет удобные инструменты для работы с пользователями, аутентификацией, конфигурацией, логированием и взаимодействием с API.

---

## 📦 Основные возможности
- Типобезопасные маршруты и запросы к API
- Гибкая работа с конфигами через Pydantic
- Асинхронная поддержка Redis
- Удобные модели для FastAPI
- Расширяемая архитектура

---

## 🛠️ Установка

```bash
git clone https://github.com/Javicle/OpenVerse.git
cd OpenVerse/_Tools
poetry install
```

---

## 📚 Структура проекта

```
tools_openverse/
	common/
		config.py        # Конфигурация и настройки
		logger_.py       # Логирование
		request.py       # API-клиент
		models.py        # Pydantic-модели
		dep.py           # Зависимости
		types.py         # Типы ответов
		...
```

---

## 📄 Лицензия
MIT License © Javicle
