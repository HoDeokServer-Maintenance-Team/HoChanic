import aiosqlite
import asyncio

loop = asyncio.get_event_loop()


def set_column(store_type, **kwargs):
    result_list = None
    for k, v in kwargs.items():
        if v is None:
            v = "NULL DEFAULT NULL"
        elif v is False:
            v = "NOT NULL"
        else:
            v = f"NOT NULL DEFAULT {v}"
        name = k
        init_val = v
        result = f"{name} {store_type} {init_val}"
        if result_list is None:
            result_list = result
            continue
        result_list += ', ' + result
    return result_list


class HoChanicDB:
    def __init__(self, db_name):
        self.db = loop.run_until_complete(aiosqlite.connect(db_name))

    async def close_db(self):
        await self.db.close()

    async def create_table(self, table_name, store_type, **kwargs):
        column_sets = set_column(store_type, **kwargs)
        await self.db.execute(f'DROP TABLE IF EXISTS {table_name}')
        await self.db.execute(f'CREATE TABLE {table_name}({column_sets})')
        await self.db.commit()

    async def run_sql(self, sql: str):
        await self.db.execute(sql)
        await self.db.commit()

    async def res_sql(self, sql: str):
        cursor = await self.db.execute(sql)
        rows = await cursor.fetchall()
        await cursor.close()
        return rows

    async def get_table(self, table_name):
        cursor = await self.db.execute(f'SELECT * FROM {table_name}')
        rows = await cursor.fetchall()
        await cursor.close()
        return rows

    async def get_from_table(self, table_name, where, where_val, is_int=False):
        if not is_int:
            where_val = '"' + where_val + '"'
        cursor = await self.db.execute(f'SELECT * FROM {table_name} WHERE {where}={where_val}')
        rows = await cursor.fetchall()
        await cursor.close()
        return rows

    async def insert_table(self, table_name, is_int=False, **kwargs):
        if is_int:
            fields = ', '.join(kwargs.keys())
            values = ', '.join(kwargs.values())
            await self.db.execute(f'INSERT INTO {table_name}({fields}) VALUES ({values})')
        else:
            fields = ', '.join(kwargs.keys())
            values = '", "'.join(kwargs.values())
            await self.db.execute(f'INSERT INTO {table_name}({fields}) VALUES ("{values}")')
        await self.db.commit()

    async def update_db(self, table_name, field, value, where, where_val, is_int=False):
        if not is_int:
            value = '"' + value + '"'
            where_val = '"' + where_val + '"'
        await self.db.execute(f"UPDATE {table_name} SET {field}={value} WHERE {where}={where_val}")
        await self.db.commit()
