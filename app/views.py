# capa de vista/presentación
#asdtawsdwseas
from django.shortcuts import redirect, render
from .layers.services import services
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.paginator import Paginator
from django.shortcuts import render
from app.layers.persistence import repositories

def index_page(request):
    return render(request, 'index.html')

# esta función obtiene 2 listados que corresponden a las imágenes de la API y los favoritos del usuario, y los usa para dibujar el correspondiente template.
# si el opcional de favoritos no está desarrollado, devuelve un listado vacío.
def home(request, page=1):
    images = services.getAllImages()
    
    favourite_list=services.getAllFavourites(request)
    
    paginator=Paginator(images,per_page=20)
    
    page_object=paginator.get_page(page)
    
    muestra={
        'page_object':page_object,
        'images':images,
        'favourite_list':favourite_list,
    }
    
    return render(request, 'home.html',muestra)

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