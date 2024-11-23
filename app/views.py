from email.mime import image
from django.shortcuts import redirect, render
from .layers.services import services
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.paginator import Paginator
from app.layers.persistence import repositories

def index_page(request):
    return render(request, 'index.html')

# Esta función obtiene 2 listados que corresponden a las imágenes de la API y los favoritos del usuario,
# y los usa para dibujar el correspondiente template.
# Si el opcional de favoritos no está desarrollado, devuelve un listado vacío.
def home(request, page=1):
    list_images = services.getAllImages()
    favourite_list = services.getAllFavourites

    paginator = Paginator(list_images, 10)  # Determina la cantidad de elementos por página
    pagina = request.GET.get("page") or 1  # Obtiene el índice desde la URL; si no lo tiene, va a la página 1
    images = paginator.get_page(pagina)
    pagina_actual = int(pagina)  # Convierte la página actual en un entero
    paginas = range(1, paginator.num_pages + 1)  # Genera una lista con todos los números de página

    # Diccionario con los datos que se pasarán al template
    contexto = {
        'images': images,
        'favourite_list': favourite_list,
        'paginas': paginas,
        'pagina_actual': pagina_actual
    }

    return render(request, 'home.html', contexto)



def search(request):
    search_msg = request.POST.get('query', '')

    # si el texto ingresado no es vacío, trae las imágenes y favoritos desde services.py,
    # y luego renderiza el template (similar a home).
    if (search_msg !=''):
       images=services.getAllImages(search_msg)
       busqueda={
                'images':images,
       }
       return render(request, 'home.html',busqueda)
    else:
        return redirect('home')


# Estas funciones se usan cuando el usuario está logueado en la aplicación.
@login_required
def getAllFavouritesByUser(request):
    favourite_list = services.getAllFavourites(request)
    return render(request, 'favourites.html', { 'favourite_list': favourite_list })

@login_required
def saveFavourite(request):
    services.saveFavourite(request)
    return home(request)

@login_required
def deleteFavourite(request):
    services.deleteFavourite(request)
    return getAllFavouritesByUser(request)

@login_required
def exit(request):
    logout(request)
    return redirect('home')