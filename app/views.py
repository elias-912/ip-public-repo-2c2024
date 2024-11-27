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
    try:
        pagina = int(request.GET.get('page', 1))
    except ValueError:
        pagina = 1

    # Obtener información de la API
    api_info = services.getApiInfo()
    total_paginas = api_info['pages']

    # Asegurarse de que la página esté dentro del rango válido
    if pagina < 1:
        pagina = 1
    elif pagina > total_paginas:
        pagina = total_paginas

    # Calcular el grupo actual y el rango de páginas a mostrar
    grupo_actual = (pagina - 1) // 10
    inicio = grupo_actual * 10 + 1
    fin = min(inicio + 9, total_paginas)
    paginas_mostrar = range(inicio, fin + 1)

    # Obtener imágenes de la API para la página actual
    list_images = services.getAllImages(f"?page={pagina}")
    favourite_list = services.getAllFavourites(request)

    # No es necesario volver a paginar si la API ya lo hace
    contexto = {
        'images': list_images,
        'favourite_list': favourite_list,
        'paginas': paginas_mostrar,
        'pagina_actual': pagina,
        'total_paginas': total_paginas,
        'grupo_inicio': inicio,
        'grupo_fin': fin
    }

    return render(request, 'home.html', contexto)

def search(request):
    # Obtener término de búsqueda del POST o GET
    search_msg = request.POST.get('query') or request.GET.get('query', '')
    try:
        pagina = int(request.GET.get('page', 1))
    except ValueError:
        pagina = 1

    # Si no hay término de búsqueda, redirigir a home
    if not search_msg:
        return redirect('home')

    # Lista para almacenar todos los resultados coincidentes
    all_matching_images = []
    current_page = 1

    # Recorrer todas las páginas de la API
    while True:
        input = f"?page={current_page}&name={search_msg}"
        try:
            images = services.getAllImages(input)
        except Exception as e:
            print(f"Error al obtener imágenes: {e}")
            break

        if not images:
            break

        # Filtrar y almacenar imágenes coincidentes
        all_matching_images.extend(images)
        current_page += 1

    total_items = len(all_matching_images)

    # Si no hay resultados, mostrar mensaje sin índices
    if total_items == 0:
        contexto = {
            'images': [],
            'is_search': True,
            'search_term': search_msg,
            'total_paginas': 0
        }
        return render(request, 'home.html', contexto)

    # Calcular paginación para 20 items por página
    total_paginas = (total_items + 19) // 20

    # Asegurarse de que la página esté dentro del rango válido
    if pagina < 1:
        pagina = 1
    elif pagina > total_paginas:
        pagina = total_paginas

    # Calcular el grupo actual y el rango de páginas a mostrar
    grupo_actual = (pagina - 1) // 10
    inicio = grupo_actual * 10 + 1
    fin = min(inicio + 9, total_paginas)
    paginas_mostrar = range(inicio, fin + 1) if total_paginas > 0 else []

    # Paginar los resultados (20 items por página)
    inicio_slice = (pagina - 1) * 20
    fin_slice = min(inicio_slice + 20, total_items)
    images_page = all_matching_images[inicio_slice:fin_slice]

    contexto = {
        'images': images_page,
        'paginas': paginas_mostrar,
        'pagina_actual': pagina,
        'total_paginas': total_paginas,
        'grupo_inicio': inicio,
        'grupo_fin': fin,
        'is_search': True,
        'search_term': search_msg,
        'query': search_msg
    }

    return render(request, 'home.html', contexto)


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