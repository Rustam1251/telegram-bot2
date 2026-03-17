#!/bin/bash

# Скрипт деплоя EGOIST ACADEMY на Ubuntu VPS
# Использование: sudo bash deploy.sh

set -e

echo "🚀 Начинаем деплой EGOIST ACADEMY..."

# Получаем текущего пользователя и директорию
CURRENT_USER=${SUDO_USER:-$USER}
PROJECT_DIR=$(pwd)
SERVICE_NAME="egoist_bot"

echo "📁 Директория проекта: $PROJECT_DIR"
echo "👤 Пользователь: $CURRENT_USER"

# Проверка наличия виртуального окружения
if [ ! -d "venv" ]; then
    echo "❌ Виртуальное окружение не найдено!"
    echo "Создайте его командой: python3 -m venv venv"
    exit 1
fi

# Проверка наличия .env файла
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден!"
    echo "Скопируйте .env.example в .env и заполните его"
    exit 1
fi

# Создание systemd сервиса
echo "📝 Создание systemd сервиса..."

cat > /tmp/${SERVICE_NAME}.service << EOF
[Unit]
Description=EGOIST ACADEMY Telegram Bot
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/python3 $PROJECT_DIR/main.py
Restart=always
RestartSec=10

# Логирование
StandardOutput=append:$PROJECT_DIR/bot.log
StandardError=append:$PROJECT_DIR/bot.log

[Install]
WantedBy=multi-user.target
EOF

# Копирование сервиса в systemd
sudo mv /tmp/${SERVICE_NAME}.service /etc/systemd/system/

# Перезагрузка systemd
echo "🔄 Перезагрузка systemd..."
sudo systemctl daemon-reload

# Включение автозапуска
echo "✅ Включение автозапуска..."
sudo systemctl enable ${SERVICE_NAME}

# Запуск сервиса
echo "▶️  Запуск сервиса..."
sudo systemctl start ${SERVICE_NAME}

# Проверка статуса
sleep 2
echo ""
echo "📊 Статус сервиса:"
sudo systemctl status ${SERVICE_NAME} --no-pager

echo ""
echo "✅ Деплой завершён!"
echo ""
echo "📋 Полезные команды:"
echo "  Статус:      sudo systemctl status ${SERVICE_NAME}"
echo "  Остановка:   sudo systemctl stop ${SERVICE_NAME}"
echo "  Запуск:      sudo systemctl start ${SERVICE_NAME}"
echo "  Перезапуск:  sudo systemctl restart ${SERVICE_NAME}"
echo "  Логи:        sudo journalctl -u ${SERVICE_NAME} -f"
echo "  Логи файл:   tail -f $PROJECT_DIR/bot.log"
echo ""
echo "🎉 Бот запущен и готов к работе!"
