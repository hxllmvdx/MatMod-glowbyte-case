import psycopg2
import json
from sqlalchemy import create_engine, text
import pandas as pd
from table_for_predicting import processing_work_table
from psycopg2 import OperationalError, sql

def get_date():
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")

    tables = cursor.fetchall()
    return tables


def read_table_from_postgres(table_name):
    try:
        query = f'SELECT * FROM "{table_name}";'
        cursor.execute(query)
        df = cursor.fetchall()
        return df
    except Exception as e:
        print(f"❌ Ошибка: {e}")


def save_dataframe_to_db(df, table_name, db_uri):
    """
    Сохраняет DataFrame в PostgreSQL с помощью SQLAlchemy.

    :param df: pandas.DataFrame – данные для сохранения
    :param table_name: str – имя таблицы
    :param db_uri: str – строка подключения SQLAlchemy (например, 'postgresql://user:pass@host/dbname')
    """
    engine = create_engine(db_uri)

    # Сохраняем в базу, создавая таблицу при необходимости
    df.to_sql(table_name, engine, if_exists='replace', index=False)



def save_tables(csv_file_path, end_name):
    # Получаем имя таблицы из имени файла
    # table_name = os.path.splitext(os.path.basename(csv_file_path))[0]
    table_name = end_name

    # Загружаем CSV в DataFrame
    df = pd.read_csv(csv_file_path)

    # Создаем таблицу с колонками по структуре CSV (все текстовые)
    columns = df.columns
    create_table_query = sql.SQL("""
        CREATE TABLE IF NOT EXISTS {table} (
            {fields}
        );
    """).format(
        table=sql.Identifier(table_name),
        fields=sql.SQL(', ').join(
            sql.SQL("{} TEXT").format(sql.Identifier(col)) for col in columns
        )
    )
    cursor.execute(create_table_query)

    # Вставляем строки
    for _, row in df.iterrows():
        insert_query = sql.SQL("""
            INSERT INTO {table} ({fields}) VALUES ({placeholders});
        """).format(
            table=sql.Identifier(table_name),
            fields=sql.SQL(', ').join(map(sql.Identifier, columns)),
            placeholders=sql.SQL(', ').join(sql.Placeholder() * len(columns))
        )
        cursor.execute(insert_query, tuple(str(v) for v in row))

    conn.commit()


def create_work_table(db_uri):
    # Получаем DataFrame
    df = processing_work_table()

    # Приводим все значения к строкам (если нужно)
    df = df.astype(str)

    table_name = 'working_table'
    engine = create_engine(db_uri)

    # Удаляем таблицу вручную (опционально, если не используешь if_exists='replace')
    with engine.connect() as connection:
        connection.execute(text(f'DROP TABLE IF EXISTS {table_name};'))
        print('second')

    # Сохраняем DataFrame в базу
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print("Таблица working_table успешно пересоздана и заполнена.")



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
        # drop_table_from_postgres('serious_table')
        # save_tables('data/working_table.csv', 'working_table')
        for i in read_table_from_postgres('working_table'):
            print(i)
        # create_work_table('postgresql://postgres:ZEcOwNDTbOQDjLHchZKyhEOeEOfnEcFW@switchyard.proxy.rlwy.net:44380/railway')
        # save_dataframe_to_db(
        #     'data/working_table.csv',
        #     'working_table',
        #     'postgresql://postgres:ZEcOwNDTbOQDjLHchZKyhEOeEOfnEcFW@switchyard.proxy.rlwy.net:44380/railway')
    except OperationalError as e:
        print(f"❌ Ошибка подключения: {e}")
    # finally:
    #     cursor.close()
    #     conn.close()
    #     print("🔒 Соединение закрыто")