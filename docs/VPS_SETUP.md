# 🎯 Установка на VPS - Пошаговая инструкция

## Вариант 1: Автоматическая установка (Рекомендуется)

### 1. Откройте терминал на сервере

### 2. Перейдите в директорию проекта
```bash
cd "/root/egoist academy"
```

### 3. Сделайте скрипт установки исполняемым
```bash
chmod +x install.sh
```

### 4. Запустите автоматическую установку
```bash
./install.sh
```

Скрипт автоматически:
- ✅ Обновит систему
- ✅ Установит Python и зависимости
- ✅ Создаст виртуальное окружение
- ✅ Установит все пакеты
- ✅ Создаст .env файл
- ✅ Предложит выбрать режим запуска

### 5. Заполните .env файл когда скрипт попросит
```bash
nano .env
```

Заполните:
```env
BOT_TOKEN=ваш_токен_от_BotFather
GROQ_API_KEY=ваш_ключ_от_Groq
```

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

### 6. Выберите режим запуска
- **1** - Тестовый запуск (в терминале)
- **2** - Запуск как сервис (рекомендуется для продакшена)
- **3** - Только установка

---

## Вариант 2: Ручная установка

### 1. Подключитесь к серверу и перейдите в директорию
```bash
cd "/root/egoist academy"
```

### 2. Обновите систему
```bash
sudo apt update && sudo apt upgrade -y
```

### 3. Установите Python
```bash
sudo apt install python3 python3-pip python3-venv -y
```

### 4. Создайте виртуальное окружение
```bash
python3 -m venv venv
source venv/bin/activate
```

### 5. Установите зависимости
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Настройте .env
```bash
cp .env.example .env
nano .env
```

Заполните токены и сохраните.

### 7. Тестовый запуск
```bash
python3 main.py
```

### 8. Установка как сервис
```bash
chmod +x deploy.sh
sudo bash deploy.sh
```

---

## 📊 Проверка работы

### Статус сервиса
```bash
sudo systemctl status egoist_bot
```

### Просмотр логов
```bash
# Логи systemd
sudo journalctl -u egoist_bot -f

# Логи приложения
tail -f bot.log
```

### Проверка процессов
```bash
ps aux | grep python
```

---

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

---

## 🔄 Настройка автоматических бэкапов

```bash
# Сделать скрипт исполняемым
chmod +x backup.sh

# Добавить в crontab
crontab -e

# Добавить строку (бэкап каждый день в 3:00):
0 3 * * * cd "/root/egoist academy" && ./backup.sh
```

---

## 🐛 Решение проблем

### Ошибка: "Cannot connect to host api.telegram.org"
Это нормально на VPS за пределами РФ. Бот должен работать.

### Ошибка: "ModuleNotFoundError"
```bash
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

### База данных заблокирована
```bash
sudo systemctl stop egoist_bot
ps aux | grep python
kill -9 <PID>
sudo systemctl start egoist_bot
```

### Бот не отвечает
```bash
# Проверьте логи
sudo journalctl -u egoist_bot -n 50

# Проверьте .env
cat .env

# Перезапустите
sudo systemctl restart egoist_bot
```

---

## ✅ Чек-лист после установки

- [ ] Бот запущен и работает
- [ ] Статус сервиса: active (running)
- [ ] Бот отвечает на /start в Telegram
- [ ] Логи не показывают ошибок
- [ ] Автозапуск включен
- [ ] Бэкапы настроены

---

## 📞 Полезные команды

```bash
# Размер базы данных
du -h academy.db

# Список бэкапов
ls -lh backups/

# Свободное место
df -h

# Использование памяти
free -h

# Нагрузка на CPU
top
```

---

## 🎉 Готово!

Бот установлен и работает на VPS сервере Ubuntu 24!

Для тестирования:
1. Откройте Telegram
2. Найдите вашего бота
3. Отправьте `/start`
4. Пройдите регистрацию
5. Попробуйте запросить урок
