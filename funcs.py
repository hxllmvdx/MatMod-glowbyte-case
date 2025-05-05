import psycopg2
import json
import time
from sqlalchemy import create_engine, text
import pandas as pd
from table_for_predicting import processing_work_table
from psycopg2 import OperationalError, sql


def save_dataframe_to_db(csv_file_path, table_name, db_url):
    df = pd.read_csv(csv_file_path)
    engine = create_engine(db_url)

    # Сохраняем в базу, создавая таблицу при необходимости
    df.to_sql(table_name, engine, if_exists='replace', index=False)


def create_work_table(db_url):
    # Получаем DataFrame
    engine = create_engine(db_url)
    df = processing_work_table(engine)

    # Приводим все значения к строкам (если нужно)
    df = df.astype(str)

    table_name = 'working_table'

    # Удаляем таблицу вручную (опционально, если не используешь if_exists='replace')
    with engine.connect() as connection:
        connection.execute(text(f'DROP TABLE IF EXISTS {table_name};'))

    # Сохраняем DataFrame в базу
    df.to_sql(table_name, engine, if_exists='replace', index=False)
