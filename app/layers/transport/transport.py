# capa de transporte/comunicación con otras interfaces o sistemas externos.

import requests
from ...config import config

# comunicación con la REST API.
# este método se encarga de "pegarle" a la API y traer una lista de objetos JSON crudos (raw).


def getAllImages(input=None):
    if input is None:
        json_response = requests.get(config.DEFAULT_REST_API_URL).json()
    elif input.startswith('?page='):
        # Si el input es una página, usar la URL directamente con el número de página
        page_number = input.replace('?page=', '')
        json_response = requests.get(f'https://rickandmortyapi.com/api/character?page={page_number}').json()
    else:
        # Si es una búsqueda por nombre
        json_response = requests.get(config.DEFAULT_REST_API_SEARCH + input).json()

    json_collection = []

    if 'error' in json_response:
        print("[transport.py]: la búsqueda no arrojó resultados.")
        return json_collection

    for object in json_response['results']:
        try:
            if 'image' in object:
                json_collection.append(object)
            else:
                print("[transport.py]: se encontró un objeto sin clave 'image', omitiendo...")
        except KeyError:
            pass

    return json_collection