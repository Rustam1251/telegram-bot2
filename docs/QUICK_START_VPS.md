# 🚀 Быстрый запуск на VPS Ubuntu 24

## Шаг 1: Подключение к серверу
Вы уже подключены через файловый менеджер. Откройте терминал на сервере.

## Шаг 2: Переход в директорию проекта
```bash
cd "/root/egoist academy"
```

## Шаг 3: Установка Python и зависимостей
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python
sudo apt install python3 python3-pip python3-venv -y

# Проверка версии
python3 --version
```

## Шаг 4: Создание виртуального окружения
```bash
# Создание venv
python3 -m venv venv

# Активация
source venv/bin/activate
```

## Шаг 5: Установка зависимостей проекта
```bash
# Обновление pip
pip install --upgrade pip

# Установка зависимостей
pip install -r requirements.txt
```

## Шаг 6: Настройка переменных окружения
```bash
# Копирование примера
cp .env.example .env

# Редактирование
nano .env
```

Заполните:
```env
BOT_TOKEN=ваш_токен_от_BotFather
GROQ_API_KEY=ваш_ключ_от_Groq
```

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

## Шаг 7: Тестовый запуск
```bash
# Запуск бота
python3 main.py
```

Вы должны увидеть:
```
INFO - Инициализация базы данных...
INFO - База данных инициализирована
INFO - Создание бота...
INFO - Запуск polling...
```

Нажмите `Ctrl+C` для остановки.

## Шаг 8: Запуск как сервис (рекомендуется)
```bash
# Сделать скрипт исполняемым
chmod +x deploy.sh
chmod +x backup.sh

# Запустить деплой
sudo bash deploy.sh
```

## Шаг 9: Управление сервисом
```bash
# Проверка статуса
sudo systemctl status egoist_bot

# Просмотр логов
sudo journalctl -u egoist_bot -f

# Остановка
sudo systemctl stop egoist_bot

# Запуск
sudo systemctl start egoist_bot

# Перезапуск
sudo systemctl restart egoist_bot
```

## Шаг 10: Настройка автоматических бэкапов
```bash
# Добавить в crontab
crontab -e

# Добавьте строку (бэкап каждый день в 3:00):
0 3 * * * cd "/root/egoist academy" && ./backup.sh
```

## ✅ Готово!

Бот запущен и работает на VPS сервере!

## 🔧 Полезные команды

### Просмотр логов приложения
```bash
tail -f bot.log
```

### Проверка процессов
```bash
ps aux | grep python
```

### Проверка места на диске
```bash
df -h
```

### Размер базы данных
```bash
du -h academy.db
```

### Список бэкапов
```bash
ls -lh backups/
```

## 🐛 Решение проблем

### Бот не запускается
```bash
# Проверьте логи
sudo journalctl -u egoist_bot -n 50

# Проверьте .env
cat .env

# Проверьте права
ls -la
```

### База данных заблокирована
```bash
# Остановите бота
sudo systemctl stop egoist_bot

# Проверьте процессы
ps aux | grep python

# Убейте зависшие процессы
kill -9 PID

# Запустите снова
sudo systemctl start egoist_bot
```

### Ошибка импорта модулей
```bash
# Активируйте venv
source venv/bin/activate

# Переустановите зависимости
pip install -r requirements.txt --force-reinstall
```

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи: `tail -f bot.log`
2. Проверьте статус: `sudo systemctl status egoist_bot`
3. Проверьте .env: `cat .env`
