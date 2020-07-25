import requests
from rest_framework.utils import json


class LocationAPIException(Exception):
    pass


class GeolocationService:

    def get_location_by_ip(self, ip) -> dict:
        try:
            resp = requests.get('http://ip-api.com/json/{}'.format(ip))
            content = json.loads(resp.text)
            if resp.status_code == 200 and content['status'] == 'success':
                return {'lat': content['lat'], 'lng': content['lon']}
            raise LocationAPIException()
        except Exception as e:
            raise LocationAPIException()


geolocation_service = GeolocationService()
