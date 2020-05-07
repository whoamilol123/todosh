import requests

from config import GEOCODER_APIKEY


def get_ll_spn(place):
    """
    Получение координат (ll) и масштаба (spn)
    для переданного места place.

    :param place: Место для поиска.
    :return: ll и spn в формате: place|lat,lon|spn_lat,spn_lon
    """
    a = requests.get('https://geocode-maps.yandex.ru/1.x', {
        'geocode': place,
        'apikey': GEOCODER_APIKEY,
        'format': 'json',
        'results': 1
    }).json()
    go = a['response']['GeoObjectCollection']['featureMember']
    if not go:
        return None
    go = go[0]['GeoObject']
    bounds = go['boundedBy']['Envelope']
    lat1, lon1 = map(float, bounds['lowerCorner'].split(' '))
    lat2, lon2 = map(float, bounds['upperCorner'].split(' '))
    return f"{place}|{go['Point']['pos'].replace(' ', ',')}|{abs(lat2 - lat1)},{abs(lon2 - lon1)}"
