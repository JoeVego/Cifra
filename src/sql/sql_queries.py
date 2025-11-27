import psycopg2
from psycopg2 import pool

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

#выполнение запрос по полученному запросу и параметрам
def execute_sql(sql_query, params):
    try:
        conn = db_pool.getconn()
        cursor = conn.cursor()

        cursor.execute(sql_query, params)
        conn.commit()

        cursor.close()
        db_pool.putconn(conn)
    except psycopg2.Error as e:
        print(f"Ошибка при выполнении запроса с базой данных: {e}",
              "\n Запрос : ", sql_query, ", \n Параметры запроса : ", params)


#сохранение кадров объектов
def insert_to_source(img_id, source_link, datetime_value, zone_value, image_bytes, lic_pl_text):
    # Экранирование строковых значений для предотвращения SQL-инъекций
    query = f"""
    INSERT INTO source (img_id, link, date, zone, image, lic_pl_text)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    params = [img_id, source_link, datetime_value, zone_value, image_bytes, lic_pl_text]

    return query, params

#получение сохраненных объектов
def get_detection_results():
    results = []
    query = f"""
        SELECT *
        FROM source
        ORDER BY lic_pl_text
        """

    try:
        conn = db_pool.getconn()
        cursor = conn.cursor()

        cursor.execute(query)
        results = cursor.fetchall()
        conn.commit()

        cursor.close()
        db_pool.putconn(conn)
    except psycopg2.Error as e:
        print(f"Ошибка при работе с базой данных: {e}", "Резалт : ", results)

    return results

#получение записей о заявках
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

    try:
        conn = db_pool.getconn()
        cursor = conn.cursor()

        cursor.execute(query)
        results = cursor.fetchall()
        conn.commit()

        cursor.close()
        db_pool.putconn(conn)
    except psycopg2.Error as e:
        print(f"Ошибка при работе с базой данных: {e}", "Резалт : ", results)

    return results


# def insert_frame(frame_id, image_path):
#     # Экранирование строковых значений для предотвращения SQL-инъекций
#     query = f"""
#     INSERT INTO frame (id, frame)
#     VALUES (%s, %s)
#     """
#
#     params = [frame_id, image_path]
#
#     return query, params

#получение информации о времени
def get_time_report():
    results = []
    #запрос не учитывает, что выезд случуился раньше заезд, но как будто и не должен такой кейс случится
    query = f"""
        SELECT
            e1.lic_pl_text,
            TO_CHAR(TO_TIMESTAMP(e2.date, 'YYYY-MM-DD HH24:MI:SS') - TO_TIMESTAMP(e1.date, 'YYYY-MM-DD HH24:MI:SS'), 'HH24:MI:SS') AS duration,
            s.type
        FROM "source" e1
        JOIN "source" e2 
            ON e1.lic_pl_text = e2.lic_pl_text
            AND e1.zone = 'зона въезда'
            AND e2.zone = 'зона выезда'
            AND TO_TIMESTAMP(e2.date, 'YYYY-MM-DD HH24:MI:SS') > TO_TIMESTAMP(e1.date, 'YYYY-MM-DD HH24:MI:SS')
        JOIN clients s ON s.lic_pl_text = e1.lic_pl_text;
        """
    #s.client_type -- добавляем тип клиента
    #JOIN service s ON s.lp_text = pt.lic_pl_text;

    try:
        conn = db_pool.getconn()
        cursor = conn.cursor()

        cursor.execute(query)
        results = cursor.fetchall()
        print("Two tables res = ", results)
        conn.commit()

        cursor.close()
        db_pool.putconn(conn)
    except psycopg2.Error as e:
        print(f"Ошибка при работе с базой данных: {e}", "Резалт : ", results)

    return results
