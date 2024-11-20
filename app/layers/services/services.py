# capa de servicio/lógica de negocio

from ..persistence import repositories
from ..utilities import translator
from django.contrib.auth import get_user
from ..transport import transport

def getAllImages(input=None):
    # obtiene un listado de datos "crudos" desde la API, usando a transport.py.
    json_collection =[]
    json_collection=transport.getAllImages(input)#llamamos al archivo transpor y ala funcion getAlllimages y le agregamos como parametro 
                                                 #lo que el usuario ingrese en el buscador
    # recorre cada dato crudo de la colección anterior, lo convierte en una Card y lo agrega a images.
    images = []
    for item in json_collection:#recorresmos el json_collection
        images.append(translator.fromRequestIntoCard(item))#llamamos al archivo transletor y ala funcion fromrequestintocard pasandole como parametro la cada elemento del json
    return images#se nos guarda en imagenes y si el usuario ingreso un nombre en el buscador se va a buscar en la api y los va a inplimir
# añadir favoritos (usado desde el template 'home.html')
def saveFavourite(request):
    fav = '' # transformamos un request del template en una Card.
    fav.user ='' # le asignamos el usuario correspondiente.

    return repositories.saveFavourite(fav) # lo guardamos en la base.

# usados desde el template 'favourites.html'
def getAllFavourites(request):
    if not request.user.is_authenticated:
        return []
    else:
        user = get_user(request)

        favourite_list = []# buscamos desde el repositories.py TODOS los favoritos del usuario (variable 'user').       
        mapped_favourites = []

        for favourite in favourite_list:
            card = ''# transformamos cada favorito en una Card, y lo almacenamos en card.
            mapped_favourites.append(card)

        return mapped_favourites

def deleteFavourite(request):
    favId = request.POST.get('id')
    return repositories.deleteFavourite(favId) # borramos un favorito por su ID.