# Развертывание на VPS

## 🚀 Быстрое развертывание

### 1. Подключение к серверу

```bash
ssh root@YOUR_SERVER_IP
```

### 2. Клонирование репозитория

```bash
cd /root
git clone https://github.com/yourusername/egoist-academy.git
cd egoist-academy
```

### 3. Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 5. Конфигурация

```bash
nano .env
```

Добавьте:
```env
BOT_TOKEN=your_token
GROQ_API_KEY=your_key
GROQ_BASE_URL=https://api.groq.com/openai/v1
GROQ_MODEL=mixtral-8x7b-32768
DATABASE_PATH=/root/egoist-academy/academy.db
LOG_FILE=/root/egoist-academy/bot.log
```

### 6. Запуск в screen

```bash
screen -S bot
source venv/bin/activate
python3 main.py
```

Отсоедините: `Ctrl+A`, затем `D`

### 7. Проверка статуса

```bash
ps aux | grep main.py
```

## 📋 Обновление

```bash
cd /root/egoist-academy
git pull origin main
pkill -f "python3 main.py"
source venv/bin/activate
python3 main.py
```

## 🔄 Перезагрузка после перезагрузки сервера

Добавьте в crontab:

```bash
crontab -e
```

Добавьте строку:
```
@reboot cd /root/egoist-academy && screen -d -m -S bot bash -c 'source venv/bin/activate && python3 main.py'
```

## 📊 Мониторинг

### Просмотр логов

```bash
tail -f bot.log
```

### Проверка памяти

```bash
free -h
```

### Проверка диска

```bash
df -h
```

## 🛠️ Обслуживание

### Резервная копия БД

```bash
cp academy.db academy.db.backup
```

### Очистка логов

```bash
> bot.log
```

### Обновление модулей

```bash
pip install --upgrade -r requirements.txt
```

## ⚠️ Важно

- Никогда не коммитьте .env файл
- Регулярно делайте резервные копии academy.db
- Мониторьте использование API Groq
- Проверяйте логи на ошибки

## 🆘 Решение проблем

### Бот не запускается

```bash
source venv/bin/activate
python3 main.py
```

Проверьте вывод ошибок.

### Высокое использование памяти

```bash
pkill -f "python3 main.py"
# Перезагрузите
python3 main.py
```

### Проблемы с API

- Проверьте GROQ_API_KEY
- Проверьте лимиты API
- Проверьте подключение к интернету

---

**Версия**: 1.0.0
