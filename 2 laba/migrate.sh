#!/bin/bash

# Настройки подключения к базе данных
DB="postgres"
USER="postgres"
PGPASSWORD="postgres" 
HOST="localhost"
PORT="5432"
MIGRATIONS_DIR="."


# Полный путь к psql.exe для Windows
PSQL_PATH="/c/Program Files/PostgreSQL/16/bin/psql.exe"

# Экспортируем пароль для psql
export PGPASSWORD

# Функция для выполнения SQL команд из файла
run_sql() {
    echo "Выполняем: $1"
    "$PSQL_PATH" -U $USER -d $DB -h $HOST -p $PORT -f "$1"
}

# Функция для выполнения SQL команды из строки
run_sql_c() {
    "$PSQL_PATH" -U $USER -d $DB -h $HOST -p $PORT -t -c "$1"
}

# Шаг 1: Создаем таблицу для отслеживания миграций, если она еще не существует
echo "Создаем таблицу для отслеживания миграций..."
# Убираем комментарии из SQL команды!
run_sql_c "CREATE TABLE IF NOT EXISTS migrations (
    id SERIAL PRIMARY KEY,
    migration_name VARCHAR(255) UNIQUE NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)" > /dev/null

# Шаг 2: Получаем список уже выполненных миграций из базы данных
echo "Получаем список уже выполненных миграций..."
DONE_MIGRATIONS=$(run_sql_c "SELECT migration_name FROM migrations")

# Шаг 3: Ищем все SQL файлы в указанной папке и применяем их
echo "Ищем SQL файлы для применения..."
for file in $MIGRATIONS_DIR/*.sql; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        
        # Проверяем была ли уже выполнена эта миграция
        if echo "$DONE_MIGRATIONS" | grep -q "$filename"; then
            echo "$filename - уже выполнена ранее"
        else
            echo "Выполняем новую миграцию: $filename"
            
            # Выполняем SQL команды из файла
            if run_sql "$file"; then
                # Добавляем запись о выполненной миграции в таблицу migrations
                # Экранируем имя файла как строку (добавляем кавычки)
                run_sql_c "INSERT INTO migrations (migration_name) VALUES ('$filename')" > /dev/null
                echo "$filename - успешно применена и записана в историю"
            else
                echo "ОШИБКА: $filename - не удалось применить миграцию"
                exit 1
            fi
        fi
    fi
done

echo "Готово! Все миграции применены!"