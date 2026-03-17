#!/bin/bash

# Скрипт автоматического резервного копирования базы данных
# Использование: ./backup.sh

BACKUP_DIR="backups"
DB_FILE="academy.db"
DATE=$(date +%Y%m%d_%H%M%S)

# Создаём директорию для бэкапов, если её нет
mkdir -p "$BACKUP_DIR"

# Проверяем существование базы данных
if [ ! -f "$DB_FILE" ]; then
    echo "❌ Ошибка: файл базы данных $DB_FILE не найден"
    exit 1
fi

# Создаём резервную копию
echo "📦 Создание резервной копии..."
cp "$DB_FILE" "$BACKUP_DIR/academy_$DATE.db"

if [ $? -eq 0 ]; then
    echo "✅ Резервная копия создана: academy_$DATE.db"
else
    echo "❌ Ошибка при создании резервной копии"
    exit 1
fi

# Удаляем бэкапы старше 7 дней
echo "🧹 Очистка старых резервных копий (старше 7 дней)..."
find "$BACKUP_DIR" -name "academy_*.db" -mtime +7 -delete

# Показываем список текущих бэкапов
echo ""
echo "📋 Текущие резервные копии:"
ls -lh "$BACKUP_DIR" | grep "academy_"

# Подсчитываем количество бэкапов
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/academy_*.db 2>/dev/null | wc -l)
echo ""
echo "📊 Всего резервных копий: $BACKUP_COUNT"

exit 0
