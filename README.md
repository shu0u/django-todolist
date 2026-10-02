# Django Task Manager Service

Веб-сервис для управления задачами на базе архитектурного паттерна MVT (Model-View-Template) фреймворка Django.

Проект демонстрирует реализацию полного цикла **CRUD-операций**, работу с реляционной СУБД через Django ORM, безопасную обработку HTTP-запросов и динамическую маршрутизацию.

## Технологический стек
* **Language:** Python 3.11+
* **Framework:** Django 5.x
* **Database:** SQLite (Django ORM)
* **Frontend:** HTML5, CSS3 (Django Template Engine)
* **VCS:** Git / GitHub

## Архитектура и функциональность
* **CRUD-логика:** Создание, чтение, параметризованное редактирование и удаление записей по первичному ключу (`id`).
* **Безопасность:** Интеграция токенов валидации для защиты от CSRF-атак (`{% csrf_token %}`).
* **Маршрутизация:** Использование типизированных конвертеров URL (`<int:task_id>`) и разделение обработчиков GET/POST запросов.
* **Администрирование:** Настройка встроенной панели Django Admin для управления объектами модели `Task`.

## Быстрый запуск

```bash
# 1. Клонирование репозитория
git clone https://github.com/shu0u/django-todolist.git
cd django-todolist

# 2. Настройка виртуального окружения
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

# 3. Установка зависимостей и привязка БД
pip install django
python manage.py migrate

# 4. Запуск сервера разработки
python manage.py runserver
