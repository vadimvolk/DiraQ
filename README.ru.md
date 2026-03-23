**[English](README.md)** | **Русский**

# dirq

Быстрая навигация по папкам из командной строки с нечётким поиском через [fzf](https://github.com/junegunn/fzf). Сохраняйте директории как закладки с настраиваемой глубиной сканирования и мгновенно переходите в них.

## Требования

- Python 3.11+
- [fzf](https://github.com/junegunn/fzf) установлен и доступен в PATH
- [uv](https://docs.astral.sh/uv/) (рекомендуется для установки)

## Установка

### Как uv-скрипт (рекомендуется)

Глобальная установка через [uv](https://docs.astral.sh/uv/):

```bash
uv tool install git+https://github.com/vadimvolk/DiraQ.git
```

Или из локального клона:

```bash
git clone https://github.com/vadimvolk/DiraQ.git && cd dirq
uv tool install .
```

После этого `dirq` доступен отовсюду без активации виртуального окружения.

### Для разработки

```bash
git clone https://github.com/vadimvolk/DiraQ.git && cd dirq
uv sync
```

Затем запускайте через `uv run dirq` или активируйте виртуальное окружение.

### Через pip

```bash
pip install -e .
```

## Быстрый старт

```bash
# Создать файл конфигурации
dirq init config

# Настроить интеграцию с оболочкой (fish, bash или zsh)
dirq init shell bash
# Следуйте инструкциям для подключения обёртки

# Сохранить закладку (текущая директория, глубина 0)
dirq save

# Сохранить с именем и глубиной сканирования подпапок
dirq save ~/projects 2 proj

# Перейти к закладке через fzf
dirq navigate
```

## Использование

### Сохранение закладок

```bash
dirq save [путь] [глубина] [имя]
```

Все аргументы необязательны. По умолчанию: `путь` = текущая директория, `глубина` = 0, `имя` = имя папки. Глубина (0-10) определяет количество уровней сканирования подпапок.

### Навигация

```bash
dirq navigate              # Все закладки
dirq navigate --only a,b   # Только указанные закладки
dirq navigate --except c   # Исключить указанные закладки
```

При выборе папки в fzf рабочая директория меняется автоматически (через обёртку оболочки).

### Удаление закладок

```bash
dirq delete proj           # По имени
dirq delete ~/projects     # По пути
```

### Список закладок

```bash
dirq list
```

### Интеграция с оболочкой

```bash
dirq init shell fish
dirq init shell bash
dirq init shell zsh
```

Генерирует функцию-обёртку и автодополнение для вашей оболочки.

## Конфигурация

Расположение файла конфигурации (определяется автоматически):

| ОС | Путь |
|---|---|
| Linux | `~/.config/dirq/config.rc` |
| macOS | `~/Library/Application Support/dirq/config.rc` |
| Windows | `%APPDATA%\dirq\config.rc` |

Учитывает `$XDG_CONFIG_HOME`, если задан.

Формат (разделитель — табуляция):

```
proj	2	/home/user/projects
docs	0	/home/user/Documents
```

## Разработка

```bash
uv run pytest              # Запуск тестов
uv run ruff check .        # Линтинг
uv run mypy src/dirq/      # Проверка типов
```

## Архитектура

- **Ноль Python-зависимостей** — только стандартная библиотека
- **fzf — единственная внешняя зависимость** — нечёткий поиск через subprocess
- **Нативные пути конфигурации** — XDG на Linux, нативные на macOS/Windows
- **Обёртки для оболочек** — настоящий `cd` (а не просто вывод пути)

## Лицензия

Подробнее в [LICENSE](LICENSE).
