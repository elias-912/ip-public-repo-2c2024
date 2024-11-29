# capa de servicio/lógica de negocio

from ..persistence import repositories
from ..utilities import translator
from django.contrib.auth import get_user
from ..transport import transport
import requests
from app.config import config 

def getApiInfo(): #permite acceder a la informacion de la api
    response = requests.get(config.DEFAULT_REST_API_URL).json()
    return response['info']

def getAllImages(input=None):
    # obtiene un listado de datos "crudos" desde la API, usando a transport.py.
    json_collection=transport.getAllImages(input)#llamamos al archivo transpor y a la funcion getAlllimages y le agregamos como parametro 
                                                 #lo que el usuario ingrese en el buscador
    # recorre cada dato crudo de la colección anterior, lo convierte en una Card y lo agrega a images.
    images = []
    for item in json_collection:#recorresmos el json_collection 
        images.append(translator.fromRequestIntoCard(item))#llamamos al archivo transletor y a la funcion fromrequestintocard pasandole como parametro la cada elemento del json
    return images#se nos guarda en imagenes y si el usuario ingreso un nombre en el buscador se va a buscar en la api y los va a inplimir
# añadir favoritos (usado desde el template 'home.html')
def saveFavourite(request):
    fav = translator.fromTemplateIntoCard(request) # transformamos un request del template en una Card.
    fav.user =get_user(request) # le asignamos el usuario correspondiente.

    return repositories.saveFavourite(fav) # lo guardamos en la base.

# usados desde el template 'favourites.html'
def getAllFavourites(request):
    if not request.user.is_authenticated:
        return "usuario no resgistrado"
    else:
        user = get_user(request)

        favourite_list = repositories.getAllFavourites(user)# buscamos desde el repositories.py TODOS los favoritos del usuario (variable 'user').       
        mapped_favourites = []

        for favourite in favourite_list:
            card = translator.fromRepositoryIntoCard(favourite)# transformamos cada favorito en una Card, y lo almacenamos en card.
            mapped_favourites.append(card)

        return mapped_favourites

def deleteFavourite(request):
    favId = request.POST.get('id')
    return repositories.deleteFavourite(favId) # borramos un favorito por su ID.