#!/bin/bash
# Автоматическая установка EGOIST ACADEMY на Ubuntu 24

set -e

echo "╔════════════════════════════════════════╗"
echo "║   EGOIST ACADEMY - Автоустановка      ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода с цветом
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Проверка, что скрипт запущен из директории проекта
if [ ! -f "main.py" ]; then
    print_error "Файл main.py не найден!"
    echo "Пожалуйста, запустите скрипт из директории проекта"
    exit 1
fi

print_status "Директория проекта: $(pwd)"
echo ""

# 1. Обновление системы
echo "📦 Обновление системы..."
sudo apt update -qq
print_status "Система обновлена"
echo ""

# 2. Установка Python и зависимостей
echo "🐍 Установка Python и зависимостей..."
sudo apt install -y python3 python3-pip python3-venv > /dev/null 2>&1
print_status "Python установлен: $(python3 --version)"
echo ""

# 3. Создание виртуального окружения
echo "📁 Создание виртуального окружения..."
if [ -d "venv" ]; then
    print_warning "venv уже существует, пропускаем..."
else
    python3 -m venv venv
    print_status "Виртуальное окружение создано"
fi
echo ""

# 4. Активация и установка зависимостей
echo "📚 Установка зависимостей..."
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
print_status "Зависимости установлены"
echo ""

# 5. Создание .env файла
echo "⚙️  Настройка конфигурации..."
if [ -f ".env" ]; then
    print_warning ".env уже существует"
    read -p "Перезаписать? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        print_status ".env создан из .env.example"
    fi
else
    cp .env.example .env
    print_status ".env создан из .env.example"
fi
echo ""

# 6. Запрос токенов
echo "🔑 Настройка токенов..."
echo ""

if [ ! -f ".env" ]; then
    print_error ".env файл не найден!"
    exit 1
fi

# Проверка, заполнен ли .env
if grep -q "your_bot_token_here" .env; then
    print_warning "Необходимо заполнить .env файл"
    echo ""
    echo "Откройте другой терминал и выполните:"
    echo "  nano .env"
    echo ""
    echo "Заполните:"
    echo "  BOT_TOKEN=ваш_токен_от_BotFather"
    echo "  GROQ_API_KEY=ваш_ключ_от_Groq"
    echo ""
    read -p "Нажмите Enter после заполнения .env..."
fi

# 7. Проверка конфигурации
echo ""
echo "🔍 Проверка конфигурации..."
if grep -q "your_bot_token_here" .env; then
    print_error "BOT_TOKEN не заполнен в .env!"
    echo "Пожалуйста, отредактируйте .env файл"
    exit 1
fi

if grep -q "your_groq_api_key_here" .env; then
    print_error "GROQ_API_KEY не заполнен в .env!"
    echo "Пожалуйста, отредактируйте .env файл"
    exit 1
fi

print_status "Конфигурация проверена"
echo ""

# 8. Установка прав на скрипты
echo "🔐 Установка прав на скрипты..."
chmod +x deploy.sh
chmod +x backup.sh
print_status "Права установлены"
echo ""

# 9. Выбор режима запуска
echo "╔════════════════════════════════════════╗"
echo "║        Выберите режим запуска:        ║"
echo "╠════════════════════════════════════════╣"
echo "║  1. Тестовый запуск (в терминале)     ║"
echo "║  2. Запуск как systemd сервис          ║"
echo "║  3. Только установка (без запуска)     ║"
echo "╚════════════════════════════════════════╝"
echo ""
read -p "Ваш выбор (1-3): " choice

case $choice in
    1)
        echo ""
        print_status "Запуск в тестовом режиме..."
        echo ""
        echo "Для остановки нажмите Ctrl+C"
        echo ""
        python3 main.py
        ;;
    2)
        echo ""
        print_status "Установка как systemd сервис..."
        sudo bash deploy.sh
        echo ""
        print_status "Сервис установлен и запущен!"
        echo ""
        echo "Управление сервисом:"
        echo "  sudo systemctl status egoist_bot"
        echo "  sudo systemctl stop egoist_bot"
        echo "  sudo systemctl start egoist_bot"
        echo "  sudo systemctl restart egoist_bot"
        echo ""
        echo "Просмотр логов:"
        echo "  sudo journalctl -u egoist_bot -f"
        ;;
    3)
        echo ""
        print_status "Установка завершена!"
        echo ""
        echo "Для запуска выполните:"
        echo "  source venv/bin/activate"
        echo "  python3 main.py"
        echo ""
        echo "Или установите как сервис:"
        echo "  sudo bash deploy.sh"
        ;;
    *)
        print_error "Неверный выбор"
        exit 1
        ;;
esac

echo ""
echo "╔════════════════════════════════════════╗"
echo "║     ✅ Установка завершена успешно!    ║"
echo "╚════════════════════════════════════════╝"
