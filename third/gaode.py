from parser import Location, GeoInfo
from .geo_service import GeoService
from requests import request
from dotenv import find_dotenv, load_dotenv
import os


class GaoDe(GeoService):

    def __init__(self):
        load_dotenv(find_dotenv())
        self._key = os.getenv('gao_de_key')

    def regeo(self, location: Location) -> GeoInfo:
        if location is None:
            return None
        params = {
            'key': self._key,
            'location': str(location).replace(' ', '')
        }
        resp = request('GET', 'https://restapi.amap.com/v3/geocode/regeo',
                       params=params).json()
        if resp['status'] == '1':
            address_component = resp['regeocode']['addressComponent']
            city = address_component['city']
            street = address_component['streetNumber']['street']

            geo_info = {
                'province': address_component['province'],
                'city': city[0] if len(city) > 0 else "",
                'district': address_component['district'],
                'township': address_component['township'],
                'street': street if type(street) is not list else street[0] if len(street) > 0 else ""
            }
            return GeoInfo(**geo_info)
        else:
            print(resp)
            return None
