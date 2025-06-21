import time

import psycopg
import json

from YP.logger import logger


PARSX_DB = {
    'DB_NAME': "YP_DB",
    'DB_USERNAME': "postgres",
    'DB_PASSWORD': "jQhdcM,s1@ULs?",
    'PORT': '5432',
    'HOST': "37.252.17.82",
}
VK_SYNC_DB = {
    'DB_NAME': "vk_price",
    'DB_USERNAME': "postgres",
    'DB_PASSWORD': "jQhdcM,s1@ULs?",
    'PORT': '5433',
    'HOST': "94.228.120.147",
}

DB_NAME, DB_USERNAME, DB_PASSWORD, HOST, PORT = (
    VK_SYNC_DB['DB_NAME'], VK_SYNC_DB['DB_USERNAME'], VK_SYNC_DB['DB_PASSWORD'], VK_SYNC_DB['HOST'], VK_SYNC_DB['PORT'])

PX_DB_NAME, PX_DB_USERNAME, PX_DB_PASSWORD, PX_HOST, PX_PORT = (
    PARSX_DB['DB_NAME'], PARSX_DB['DB_USERNAME'], PARSX_DB['DB_PASSWORD'], PARSX_DB['HOST'], PARSX_DB['PORT'])

class PgSqlModel:
    def __init__(self, table):
        """
        Инициализация объекта для работы с PgSql.
        """
        self.table = table
        self.conn = psycopg.connect(
            f"dbname={DB_NAME} user={DB_USERNAME} password={DB_PASSWORD} host={HOST} port={PORT}")
        logger.debug("Соединение установлено.")

    def object_exists(self, column_name, primary_key):
        """
        Проверяет наличие объекта в таблице по заданным условиям.
        :param primary_key: первичный ключ.
        :param column_name: название поля
        :return: True, если объект существует, иначе False.
        """
        query = f"SELECT 1 FROM {self.table} WHERE {column_name} = '{primary_key}'"

        with self.conn.cursor() as cursor:
            cursor.execute(query)

            return cursor.fetchone() is not None

    def add_object(self, **kwargs):
        """
        Добавляет объект в таблицу.
        :param kwargs: Словарь с названиями колонок и значениями для вставки.
        """
        columns = ', '.join(kwargs.keys())
        fields_for_upd = ', '.join([f"{fld} = COALESCE(EXCLUDED.{fld}, {self.table}.{fld})" for fld in kwargs.keys()])

        placeholders = ', '.join(['%s'] * len(kwargs))
        values = tuple(kwargs.values())

        pk_field = {"products_product": "sbis_id", "products_category": "id"}
        query = (f"INSERT INTO {self.table} ({columns})\n"
                 f"VALUES ({placeholders})\n"
                 f"ON CONFLICT({pk_field[self.table]}) DO UPDATE SET "
                 f"{fields_for_upd};"
                 )
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, values)
                self.conn.commit()
        except Exception as e:
            logger.error(f"Ошибка запроска к БД. {kwargs}\n{e} \nЗапрос - {query}")

    def get_image_list(self, sbis_id):
        if self.table != 'products_product':
            logger.error('Метод get_image_list используется только с таблицей products_product')
            raise Exception
        query = (f"SELECT images_response "
                 f"FROM {self.table} "
                 f"WHERE sbis_id = '{sbis_id}'")
        with self.conn.cursor() as cursor:
            cursor.execute(query)

            result = cursor.fetchone()
        if result:
            return result[0]

    def get_product_data(self, sbis_id):
        if self.table != 'products_product':
            logger.error('Метод get_product_data используется только с таблицей products_product')
            raise Exception
        query = (f"SELECT * "
                 f"FROM {self.table} "
                 f"WHERE sbis_id = '{sbis_id}'")
        with self.conn.cursor() as cursor:
            cursor.execute(query)

            result = cursor.fetchone()
            if result:
                return result

    def get_category(self):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM products_category")
        return cursor.fetchall()

    def edit_object(self, obj_id, field, value):
        """
        Обновляет объект, меняя значение одного из его полей.
        :param obj_id: ID объекта
        :param field: название поля
        :param value: значение
        """
        query = f"""
                UPDATE {self.table}
                SET {field} = %s
                WHERE id = %s
            """
        with self.conn.cursor() as cursor:
            cursor.execute(query, (value, obj_id))
            self.conn.commit()

    def products_iteration(self, offset: int):
        """
        Возвращает список из 100 товаров из БД. БД обходится по очереди.
        :param offset: Индекс строки БД, с которой будет начинаться список.
        """
        batch_size = 100
        last_page = False
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM products_product ORDER BY id LIMIT %s OFFSET %s", (batch_size, offset))
            rows = cursor.fetchall()

            if len(rows) < batch_size:
                last_page = True

            return rows, last_page

    def get_vk_category(self, category_id):
        query = f"""
                    SELECT vk_id 
                    FROM products_category 
                    WHERE id = %s
                """
        with self.conn.cursor() as cursor:
            cursor.execute(query, (category_id,))

            return cursor.fetchone()

    def get_category_prod(self, sbis_id):
        "Метод вернет ID категории ВК и информацию о товаре"
        query_1 = f"""
                    SELECT *
                    FROM products_product
                    WHERE sbis_id = %s;
                """
        query_2 = f"""
                    SELECT vk_id FROM products_category
                    WHERE id = (
                            SELECT category_id
                            FROM products_product
                            WHERE sbis_id = %s
                    );
                """
        with self.conn.cursor() as cursor:
            cursor.execute(query_1, (sbis_id,))
            product_data = cursor.fetchone()

            cursor.execute(query_2, (sbis_id,))
            vk_category_id = cursor.fetchone()

            if not product_data or not vk_category_id:
                logger.error(f'product_data = {product_data}\n vk_category_id = {vk_category_id}')
                return None

            return product_data, vk_category_id


def upsert_products(products: list[dict]):
    """
    Обновляет или вставляет товары по полю `sbis_id`.

    :param products: список словарей с полями: name, description, parameters, price, sbis_id
    """
    conn = psycopg.connect(
        f"dbname={PX_DB_NAME} user={PX_DB_USERNAME} password={PX_DB_PASSWORD} host={PX_HOST} port={PX_PORT}")
    logger.debug("Соединение установлено.")

    query = """
    INSERT INTO vk_sync_products (sbis_id, customer_id, name, description, parameters, price, images, category_id, stocks_mol, unisiter_url)
    VALUES (%(sbis_id)s, %(customer_id)s, %(name)s, %(description)s, %(parameters)s, %(price)s, %(images)s, %(category_id)s, %(stocks_mol)s, %(unisiter_url)s)
    ON CONFLICT (sbis_id)
    DO UPDATE SET
        customer_id = EXCLUDED.customer_id,
        name = EXCLUDED.name,
        description = EXCLUDED.description,
        parameters = EXCLUDED.parameters,
        price = EXCLUDED.price,
        images = EXCLUDED.images,
        category_id = EXCLUDED.category_id,
        stocks_mol = EXCLUDED.stocks_mol,
        unisiter_url = EXCLUDED.unisiter_url;
    """

    with conn.cursor() as cur:
        cur.executemany(query, products)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    # conn = psycopg.connect(f"dbname={DB_NAME} user={DB_USERNAME} password={DB_PASSWORD} host={HOST} port={PORT}")
    # cur = conn.cursor()
    # cur.execute("SELECT * FROM products_product")
    # for row in cur:
    #     print(row)
    #
    # cur.close()
    # conn.close()

    sql = PgSqlModel(None)
    print(sql.get_category_prod("РТ000013807"))
