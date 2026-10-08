# Code review: django-todolist

Глеб, привет! Ниже ревью проекта. Код читается легко, структура понятная, и многое сделано правильно:
каждая задача привязана к пользователю, и чужую задачу нельзя открыть ни в HTML, ни через API
(`get_object_or_404(..., user=request.user)`). Это самая частая ошибка новичков, и у тебя её нет.

Пункты отсортированы по важности. Пункты 1–3 я проверил запуском (`USE_SQLITE=1`, Django test client).

---

## 🔴 Важно: исправить в первую очередь

### 1. Регистрация не работает: 500 ошибка
Файл шаблона назван `registration/singup.html` (опечатка), а view рендерит `registration/signup.html`
(`todo/views.py:100`). Любой GET на `/accounts/signup/` падает с `TemplateDoesNotExist`.

**Как исправить:** переименовать файл:
```bash
git mv todo/templates/registration/singup.html todo/templates/registration/signup.html
```

### 2. Удаление и переключение задачи через GET: уязвимость CSRF
`delete_task` и `toggle_task` срабатывают на обычный переход по ссылке (`<a href="...">`).
CSRF-защита Django проверяет только POST/PUT/DELETE, поэтому любой сторонний сайт может вставить
`<img src="http://your-site/delete/5/">`, и у залогиненного пользователя молча удалится задача.
Плюс браузеры и расширения иногда сами «предзагружают» ссылки.

Правило: **GET никогда не должен менять данные.**

**Как исправить:**
```python
from django.views.decorators.http import require_POST

@login_required
@require_POST
def delete_task(request, task_id):
    ...
```
А в шаблоне вместо ссылки сделать маленькую форму:
```html
<form method="POST" action="{% url 'delete_task' task.id %}" class="d-inline">
    {% csrf_token %}
    <button type="submit" class="btn btn-sm btn-outline-danger">Удалить</button>
</form>
```
Для выхода (`logout`) ты уже так сделал, нужно то же самое для delete и toggle (в `index.html` и `completed.html`).

### 3. Нет проверки длины названия задачи
В модели `title = CharField(max_length=200)`, но `home` и `edit_task` берут значение прямо из
`request.POST` и сохраняют без проверки. На SQLite строка из 500 символов спокойно сохраняется
(проверил), а на PostgreSQL будет `DataError` и 500 ошибка.

**Как исправить (хорошо):** использовать `ModelForm`, она сама проверяет длину и обязательность:
```python
# todo/forms.py
from django import forms
from todo.models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title']
```
```python
form = TaskForm(request.POST)
if form.is_valid():
    task = form.save(commit=False)
    task.user = request.user
    task.save()
```
**Минимум:** добавить `maxlength="200"` в `<input>`, но это защита только для честных пользователей:
сервер всё равно должен проверять сам.

### 4. Секреты в коде
- `SECRET_KEY` захардкожен в `config/settings.py:25` и уже лежит в публичной истории git.
- Пароль БД `todopassword` в `docker-compose.yml` и как значение по умолчанию в `settings.py`.
- `DEBUG = True` всегда.

Для учебного проекта это не катастрофа, но привычку стоит выработать сразу:
```python
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']          # упадёт сразу, если не задан
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost').split(',')
```
А в `docker-compose.yml` использовать `env_file: .env` (`.env` у тебя уже в `.gitignore`, молодец)
и положить рядом `.env.example` без настоящих значений.

---

## 🟡 Стоит поправить

### 5. README устарел и инструкция запуска не работает
README говорит про SQLite, Django 5.x и `pip install django`. На деле:
- нужен ещё `djangorestframework` → правильно `pip install -r requirements.txt`;
- по умолчанию база PostgreSQL на хосте `db`, поэтому `python manage.py migrate` без Docker упадёт.
  Работает только с `USE_SQLITE=1`, но это нигде не написано;
- нет раздела про `docker compose up` и про API (`/api/v1/tasks/`).

### 6. Поле `priority` добавлено, но нигде не используется
Миграция `0003_task_priority` есть, но поля нет ни в сериализаторе, ни в формах, ни в шаблонах,
и сортировки по нему тоже нет. Либо доделать (выбор приоритета + сортировка), либо убрать.
Если оставлять, лучше через `choices`:
```python
class Priority(models.IntegerChoices):
    LOW = 1, 'Низкий'
    MEDIUM = 2, 'Средний'
    HIGH = 3, 'Высокий'

priority = models.IntegerField(choices=Priority.choices, default=Priority.LOW)
```

### 7. Нет ни одного теста
`todo/tests.py` пустой. Пункты 1–3 как раз поймали бы простые тесты. Пример для старта:
```python
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from todo.models import Task

class TaskViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('gleb', password='test-pass-123')
        self.other = User.objects.create_user('other', password='test-pass-123')
        self.client.force_login(self.user)

    def test_signup_page_opens(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse('signup')).status_code, 200)

    def test_cannot_delete_other_users_task(self):
        task = Task.objects.create(user=self.other, title='not mine')
        response = self.client.post(reverse('delete_task', args=[task.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Task.objects.filter(id=task.id).exists())

    def test_delete_requires_post(self):
        task = Task.objects.create(user=self.user, title='mine')
        response = self.client.get(reverse('delete_task', args=[task.id]))
        self.assertEqual(response.status_code, 405)
```
Запуск: `USE_SQLITE=1 python manage.py test`.

### 8. Docker
- `depends_on: db` ждёт только старта контейнера, а не готовности Postgres. Первый запуск часто
  падает с «connection refused». Нужен `healthcheck` у `db` и `condition: service_healthy`.
- Порт `5432` наружу открывать не нужно: `web` ходит в `db` по внутренней сети.
- Нет `.dockerignore`: в образ копируются `.git`, `venv`, `db.sqlite3`.
- Миграции нигде не запускаются автоматически. Можно добавить в `command`:
  `sh -c "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"`.

---

## 🟢 Мелочи и стиль

- `todo/views.py:105`: строка `request.user` ничего не делает, удалить.
- «Вернуть» на странице выполненных задач перекидывает на главную, а не обратно на `/completed/`.
- `edit_task`: если отправить пустое название, страница просто перезагрузится без сообщения об ошибке
  (`ModelForm` из пункта 3 решит и это).
- На `/completed/` и в API нет сортировки. Можно один раз задать в модели:
  `class Meta: ordering = ['-created_at']`.
- Четыре шаблона повторяют один и тот же `<head>` и navbar. Стоит вынести в `base.html`
  и использовать `{% extends "base.html" %}` + `{% block content %}`.
- URL-ы лучше вынести в `todo/urls.py` и подключить через `include('todo.urls')`. Так приложение
  становится самостоятельным.
- Импорты в `views.py` перемешаны: принято сначала Django, потом сторонние (DRF), потом свои модули.
- API: вместо двух функций с `if request.method == ...` в DRF есть `ModelViewSet` + `router`,
  получится ~10 строк. Но и текущий вариант хорош для понимания, как всё устроено.
- `admin.py`: можно сделать админку удобнее через `@admin.register(Task)` с `list_display`,
  `list_filter`, `search_fields`.
- Коммиты: «Update», «First», два одинаковых сообщения подряд. Лучше коротко писать, *что* изменилось:
  `fix: rename signup template`, `feat: add task priority`.

---

## Итого

Хорошая база: CRUD, авторизация, изоляция данных между пользователями, REST API, Docker, PostgreSQL.
Для учебного проекта это много. Чтобы было «готово», предлагаю такой порядок:

1. Переименовать `singup.html` → `signup.html` (5 секунд).
2. delete/toggle только через POST.
3. `TaskForm` вместо ручного `request.POST.get`.
4. Написать 3–5 тестов.
5. Секреты в env, обновить README.

Если что-то непонятно, спрашивай!
