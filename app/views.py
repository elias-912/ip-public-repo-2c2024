# capa de vista/presentación

from django.shortcuts import redirect, render
from .layers.services import services
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import render


def index_page(request):
    return render(request, 'index.html')

# esta función obtiene 2 listados que corresponden a las imágenes de la API y los favoritos del usuario, y los usa para dibujar el correspondiente template.
# si el opcional de favoritos no está desarrollado, devuelve un listado vacío.

def calcular_paginacion(total_items, pagina_actual, items_por_pagina=20, paginas_por_grupo=10):
   
    total_paginas = (total_items + items_por_pagina - 1) // items_por_pagina

    if pagina_actual < 1: #sirve para no pasarse de los limites de los indices
        pagina_actual = 1
    elif pagina_actual > total_paginas:
        pagina_actual = total_paginas

    grupo_actual = (pagina_actual - 1) // paginas_por_grupo
    inicio = grupo_actual * paginas_por_grupo + 1
    fin = min(inicio + paginas_por_grupo - 1, total_paginas)
    paginas_mostrar = range(inicio, fin + 1) if total_paginas > 0 else []

    inicio_slice = (pagina_actual - 1) * items_por_pagina
    fin_slice = min(inicio_slice + items_por_pagina, total_items)

    return {
        'paginas_mostrar': paginas_mostrar,
        'pagina_actual': pagina_actual,
        'total_paginas': total_paginas,
        'grupo_inicio': inicio,
        'grupo_fin': fin,
        'inicio_slice': inicio_slice,
        'fin_slice': fin_slice
    }

def home(request, page=1):
    try:
        pagina = int(request.GET.get('page', 1))
    except ValueError:
        pagina = 1

    api_info = services.getApiInfo()
    total_paginas = api_info['pages']

    paginacion = calcular_paginacion(total_paginas * 20, pagina)

    list_images = services.getAllImages(f"?page={pagina}")
    favourite_list = services.getAllFavourites(request)

    contexto = {
        'images': list_images,
        'favourite_list': favourite_list,
        'paginas': paginacion['paginas_mostrar'],
        'pagina_actual': paginacion['pagina_actual'],
        'total_paginas': paginacion['total_paginas'],
        'grupo_inicio': paginacion['grupo_inicio'],
        'grupo_fin': paginacion['grupo_fin']
    }

    return render(request, 'home.html', contexto)

def search(request):
    search_msg = request.POST.get('query') or request.GET.get('query', '')
    try:
        pagina = int(request.GET.get('page', 1))
    except ValueError:
        pagina = 1

    if not search_msg:
        return redirect('home')

    all_matching_images = []
    current_page = 1

    while True:
        input = f"?page={current_page}&name={search_msg}"
        try:
            images = services.getAllImages(input)
        except Exception as e:
            print(f"Error al obtener imágenes: {e}")
            break

        if not images:
            break

        all_matching_images.extend(images)
        current_page += 1

    total_items = len(all_matching_images)

    if total_items == 0:
        contexto = {
            'images': [],
            'is_search': True,
            'search_term': search_msg,
            'total_paginas': 0
        }
        return render(request, 'home.html', contexto)

    paginacion = calcular_paginacion(total_items, pagina)

    images_page = all_matching_images[paginacion['inicio_slice']:paginacion['fin_slice']]

    contexto = {
        'images': images_page,
        'paginas': paginacion['paginas_mostrar'],
        'pagina_actual': paginacion['pagina_actual'],
        'total_paginas': paginacion['total_paginas'],
        'grupo_inicio': paginacion['grupo_inicio'],
        'grupo_fin': paginacion['grupo_fin'],
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