# tasks.py

import aiohttp
import aiomysql
import asyncio
import threading

async def fetch_items(session):
    async with session.get('https://esi.evetech.net/latest/markets/10000002/orders/') as response:
        return await response.json()

async def process_items(db_pool, items):
    async with db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS eve_items (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), value FLOAT, quantity INT)")
            for item in items:
                name = item.get('type_id')
                value = item.get('price')
                quantity = item.get('volume_remain')
                await cursor.execute("INSERT INTO eve_items (name, value, quantity) VALUES (%s, %s, %s)", (name, value, quantity))

def fetch_and_process_items():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def main():
        async with aiohttp.ClientSession() as session:
            items = await fetch_items(session)
            db_pool = await aiomysql.create_pool(host='your_mysql_host',
                                                 port=3306,
                                                 user='your_mysql_user',
                                                 password='your_mysql_password',
                                                 db='your_mysql_db',
                                                 autocommit=True)
            await process_items(db_pool, items)
            db_pool.close()
            await db_pool.wait_closed()

    asyncio.run(main())

def multi_threaded_sync():
    threads = []
    for _ in range(5):  # Number of threads
        thread = threading.Thread(target=fetch_and_process_items)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
