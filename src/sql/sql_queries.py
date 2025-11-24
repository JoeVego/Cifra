from fastapi import FastAPI
import asyncpg
from pydantic import BaseModel
from typing import List, Any
import psycopg2
from psycopg2 import pool

# app = FastAPI()


# class QueryModel(BaseModel):
#     query: str
#     params: List[Any] = []


# # параметры подключения к базе данных
# DB_HOST = "postgres"
# DB_PORT = 5432
# DB_USER = "app"
# DB_PASSWORD = "secret"
# DB_NAME = "app_db"

# Инициализация пула соединений
db_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dbname="app_db",
    user="app",
    password="secret",
    host="172.20.0.2",
    port=5432
)


def execute_sql(sql_query, params):
    try:
        # conn = psycopg2.connect(
        #     dbname="app_db",
        #     user="app",
        #     password="secret",
        #     host="172.20.0.2",
        #     port=5432
        # )
        conn = db_pool.getconn()
        cursor = conn.cursor()
        cursor.execute(sql_query, params)

        conn.commit()

        cursor.close()
        # conn.close()
        db_pool.putconn(conn)
    except psycopg2.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")


def insert_to_source(img_id, source_link, datetime_value, zone_value, image_bytes, lic_pl_text):
    # Экранирование строковых значений для предотвращения SQL-инъекций
    query = f"""
    INSERT INTO source (img_id, link, date, zone, image, lic_pl_text)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    params = [img_id, source_link, datetime_value, zone_value, image_bytes, lic_pl_text]

    return query, params


def get_detection_results():
    results = []
    query = f"""
        SELECT *
        FROM source
        """
    # print("Select res query = ", query)

    try:
        # conn = psycopg2.connect(
        #     dbname="app_db",
        #     user="app",
        #     password="secret",
        #     host="172.20.0.2",
        #     port=5432
        # )
        conn = db_pool.getconn()
        # print("conn info = ", conn.info)  # Информация о соединении
        # print("conn dsn = ", conn.get_dsn_parameters())

        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        print("select results = ", results)

        conn.commit()

        cursor.close()
        # conn.close()
        db_pool.putconn(conn)
    except psycopg2.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")

    return results


def get_report():
    results = []
    query = f"""
        SELECT
            client_type,
            status,
            COUNT(*) AS total_count
        FROM
            service
        GROUP BY
            client_type,
            status;
        """
    # print("Select res query = ", query)

    try:
        # conn = psycopg2.connect(
        #     dbname="app_db",
        #     user="app",
        #     password="secret",
        #     host="172.20.0.2",
        #     port=5432
        # )
        conn = db_pool.getconn()
        # print("conn info = ", conn.info)  # Информация о соединении
        # print("conn dsn = ", conn.get_dsn_parameters())

        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        print("select report results = ", results)

        conn.commit()

        cursor.close()
        # conn.close()
        db_pool.putconn(conn)
    except psycopg2.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")

    return results


def insert_frame(frame_id, image_path):
    # Экранирование строковых значений для предотвращения SQL-инъекций
    query = f"""
    INSERT INTO frame (id, frame)
    VALUES (%s, %s)
    """

    params = [frame_id, image_path]

    return query, params
