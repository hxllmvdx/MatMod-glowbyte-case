import psycopg2
from psycopg2 import OperationalError

# Параметры подключения
db_config = {
    'host': '192.168.168.228',  # IP-адрес вашего Cloud SQL instance
    'port': 5432,                         # Порт PostgreSQL (обычно 5432)
    'user': 'analyst',              # Имя пользователя
    'password': 'secure123',          # Пароль
    'database': 'Coal'      # Имя базы данных
}

def fetch_data_from_db():
    connection = None
    try:
        # Подключение к базе данных
        connection = psycopg2.connect(**db_config)

        # Создание курсора для выполнения SQL-запросов
        cursor = connection.cursor()

        # Выполнение SQL-запроса
        cursor.execute("SELECT * FROM your_table_name LIMIT 10;")

        # Получение результата запроса
        result = cursor.fetchall()

        # Печать результатов
        for row in result:
            print(row)

    except OperationalError as e:
        print(f"Ошибка при подключении к базе данных: {e}")
    finally:
        # Закрытие соединения
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с базой данных закрыто.")

# Вызов функции
fetch_data_from_db()