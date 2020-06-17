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

    async def create_table(self, table_name, column_sets):
        await self.db.execute(f'DROP TABLE IF EXISTS {table_name}')
        await self.db.execute(f'CREATE TABLE {table_name}({column_sets})')
        await self.db.commit()


if __name__ == "__main__":
    column_sets = set_column("TEXT", token="gulag")
    db = HoChanicDB("bot_db.db")
    loop.run_until_complete(db.create_table("settings", column_sets))
