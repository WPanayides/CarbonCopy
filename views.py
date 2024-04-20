# views.py

import requests
from django.http import JsonResponse

def eve_api(request):
    # Make a request to EVE Online API
    api_url = 'https://esi.evetech.net/latest/status/'
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        # Extract relevant information from the API response
        players_online = data['players']
        server_status = data['server_status']
        return JsonResponse({'players_online': players_online, 'server_status': server_status})
    else:
        return JsonResponse({'error': 'Failed to fetch data from EVE Online API'}, status=500)
