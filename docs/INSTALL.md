# 📦 Инструкция по установке на Ubuntu 24 VPS

## Шаг 1: Подключение к серверу

```bash
ssh root@your_server_ip
# или
ssh your_user@your_server_ip
```

## Шаг 2: Обновление системы

```bash
sudo apt update && sudo apt upgrade -y
```

## Шаг 3: Установка необходимых пакетов

```bash
# Python и инструменты
sudo apt install python3 python3-pip python3-venv git screen htop -y

# Проверка версии Python (должна быть 3.11+)
python3 --version
```

## Шаг 4: Создание пользователя для бота (опционально, но рекомендуется)

```bash
# Создание пользователя
sudo adduser botuser

# Добавление в группу sudo (если нужно)
sudo usermod -aG sudo botuser

# Переключение на пользователя
su - botuser
```

## Шаг 5: Загрузка проекта

### Вариант A: Через Git (если проект в репозитории)
```bash
cd ~
git clone https://github.com/your_username/egoist_academy.git
cd egoist_academy
```

### Вариант B: Загрузка файлов через SCP
На вашем локальном компьютере:
```bash
scp -r /path/to/egoist_academy your_user@your_server_ip:~/
```

На сервере:
```bash
cd ~/egoist_academy
```

## Шаг 6: Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate
```

## Шаг 7: Установка зависимостей

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Шаг 8: Настройка переменных окружения

```bash
# Копирование примера
cp .env.example .env

# Редактирование
nano .env
```

Заполните файл .env:
```env
BOT_TOKEN=your_bot_token_here
GROQ_API_KEY=your_groq_api_key_here
GROQ_BASE_URL=https://api.groq.com/openai/v1
GROQ_MODEL=llama-3.3-70b-versatile
DATABASE_PATH=academy.db
LOG_FILE=bot.log
BACKUP_DIR=backups
```

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

## Шаг 9: Тестовый запуск

```bash
# Активируйте окружение (если не активировано)
source venv/bin/activate

# Запустите бота
python3 main.py
```

Если всё работает, нажмите `Ctrl+C` для остановки.

## Шаг 10: Настройка автозапуска (systemd)

```bash
# Сделать скрипт исполняемым
chmod +x deploy.sh

# Запустить деплой
sudo bash deploy.sh
```

Скрипт автоматически:
- Создаст systemd сервис
- Настроит автозапуск при перезагрузке
- Запустит бота

## Шаг 11: Настройка автоматических бэкапов

```bash
# Сделать скрипт исполняемым
chmod +x backup.sh

# Тестовый запуск
./backup.sh

# Добавить в crontab
crontab -e

# Добавьте строку (бэкап каждый день в 3:00 ночи):
0 3 * * * cd /home/botuser/egoist_academy && ./backup.sh >> /home/botuser/egoist_academy/backup.log 2>&1
```

## Шаг 12: Проверка работы

```bash
# Статус сервиса
sudo systemctl status egoist_bot

# Просмотр логов в реальном времени
sudo journalctl -u egoist_bot -f

# Или логи приложения
tail -f bot.log
```

## 🔧 Управление ботом

### Остановка
```bash
sudo systemctl stop egoist_bot
```

### Запуск
```bash
sudo systemctl start egoist_bot
```

### Перезапуск
```bash
sudo systemctl restart egoist_bot
```

### Отключение автозапуска
```bash
sudo systemctl disable egoist_bot
```

### Включение автозапуска
```bash
sudo systemctl enable egoist_bot
```

## 📊 Мониторинг

### Использование ресурсов
```bash
htop
# Найдите процесс python3
```

### Размер базы данных
```bash
du -h academy.db
```

### Список бэкапов
```bash
ls -lh backups/
```

### Свободное место на диске
```bash
df -h
```

## 🔒 Безопасность

### Настройка firewall
```bash
# Разрешить SSH
sudo ufw allow ssh

# Включить firewall
sudo ufw enable

# Проверить статус
sudo ufw status
```

### Обновление системы
```bash
# Регулярно обновляйте систему
sudo apt update && sudo apt upgrade -y
```

### Права доступа к файлам
```bash
# Убедитесь, что .env доступен только владельцу
chmod 600 .env

# Проверка
ls -la .env
```

## 🐛 Решение проблем

### Бот не запускается
```bash
# Проверьте логи
sudo journalctl -u egoist_bot -n 50

# Проверьте конфигурацию
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

# Убейте зависшие процессы (если есть)
kill -9 PID

# Запустите снова
sudo systemctl start egoist_bot
```

### Нет места на диске
```bash
# Проверьте место
df -h

# Удалите старые бэкапы
rm backups/academy_2024*.db

# Очистите логи
> bot.log
```

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи: `tail -f bot.log`
2. Проверьте статус: `sudo systemctl status egoist_bot`
3. Проверьте переменные окружения: `cat .env`

## ✅ Готово!

Ваш бот запущен и работает на VPS сервере Ubuntu 24!

Telegram: @fel12x_bot
