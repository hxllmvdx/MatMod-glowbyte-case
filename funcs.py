import psycopg2
import json
import time
from sqlalchemy import create_engine, text
import pandas as pd
from table_for_predicting import processing_work_table
from psycopg2 import OperationalError, sql


def read_table_from_postgres(table_name):
    try:
        query = f'SELECT * FROM "{table_name}";'
        cursor.execute(query)
        df = cursor.fetchall()
        return df
    except Exception as e:
        print(f"❌ Ошибка: {e}")


def save_dataframe_to_db(csv_file_path, table_name, db_uri):
    """
    Сохраняет DataFrame в PostgreSQL с помощью SQLAlchemy.

    :param df: pandas.DataFrame – данные для сохранения
    :param table_name: str – имя таблицы
    :param db_uri: str – строка подключения SQLAlchemy (например, 'postgresql://user:pass@host/dbname')
    """
    df = pd.read_csv(csv_file_path)
    engine = create_engine(db_uri)

    # Сохраняем в базу, создавая таблицу при необходимости
    df.to_sql(table_name, engine, if_exists='replace', index=False)


def create_work_table(db_uri):
    # Получаем DataFrame
    engine = create_engine(db_uri)
    df = processing_work_table(engine)

    # Приводим все значения к строкам (если нужно)
    df = df.astype(str)

    table_name = 'working_table'

    # Удаляем таблицу вручную (опционально, если не используешь if_exists='replace')
    with engine.connect() as connection:
        connection.execute(text(f'DROP TABLE IF EXISTS {table_name};'))

    # Сохраняем DataFrame в базу
    df.to_sql(table_name, engine, if_exists='replace', index=False)



def drop_table_from_postgres(table_name):
    # SQL-запрос: удалить таблицу, если существует
    drop_query = sql.SQL("DROP TABLE IF EXISTS {table} CASCADE;").format(
        table=sql.Identifier(table_name)
    )
    cursor.execute(drop_query)
    conn.commit()


if __name__ == "__main__":
    with open('data/database_user.json') as file:
        file_json_data = json.load(file)
    try:
        conn = psycopg2.connect(
            host=file_json_data['host'],
            user=file_json_data['user'],
            port=file_json_data['port'],
            password=file_json_data['password'],
            database=file_json_data['database']
        )
        cursor = conn.cursor()
        # start_time = time.time()
        create_work_table('postgresql://postgres:ZEcOwNDTbOQDjLHchZKyhEOeEOfnEcFW@switchyard.proxy.rlwy.net:44380/railway')
        # end_time = time.time()
        # elapsed = end_time - start_time
        # print(f"Время выполнения processing_work_table: {elapsed:.2f} секунд")
    except OperationalError as e:
        print(f"❌ Ошибка подключения: {e}")
    # finally:
    #     cursor.close()
    #     conn.close()
    #     print("🔒 Соединение закрыто")