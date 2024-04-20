# First, make sure you have Django installed. You can install it using pip:
# pip install django

import os
import requests
import secrets
import aiohttp
import aiomysql
from django.conf import settings
from django.http import JsonResponse
from django.urls import path
from django.core.wsgi import get_wsgi_application
from django.core.management import execute_from_command_line
from views import eve_api
from navbar import navbar
from django.http import JsonResponse


# Django settings
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET_KEY = secrets.Secret_Key
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

DEBUG = True

settings.configure(
    BASE_DIR=BASE_DIR,
    SECRET_KEY=secrets.Secret_Key,
    DEBUG=DEBUG,
    ROOT_URLCONF=__name__,
)

# Django views
def eve_api(request):
    # Make a request to EVE Online API
    api_url = 'https://esi.evetech.net/latest/status/'
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        # Extract relevant information from the API response
        players_online = data['players']
        server_version = data['server_version']
        start_time = data['start_time']
        return JsonResponse({'players_online': players_online, 'server_version': server_version, 'start_time': start_time})
    else:
        return JsonResponse({'error': 'Failed to fetch data from EVE Online API'}, status=500)

# Django URLs
urlpatterns = [
    path('', navbar),
    path('eve_api/', eve_api),
]

# WSGI application
application = get_wsgi_application()

# Run Django server
if __name__ == "__main__":
    execute_from_command_line(['manage.py', 'runserver'])

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

def pull_items_and_store_in_db(request):
    try:
        import asyncio
        asyncio.run(main())
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
