# capa de vista/presentación

from django.shortcuts import redirect, render
from .layers.services import services
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegistroForm
from django.contrib.auth import authenticate, login

def index_page(request):
    return render(request, 'index.html')

#esta funcion maneja la solicitudes http para registrar nuevos usuarios
def registro(request):                   #recibe como parametro un request que contiene toda la informacion sobra la solicitud
    if request.method == 'POST':         #verifica si el metodo de la silicitud es POST
        form = RegistroForm(request.POST)#se crea una 
        if form.is_valid():              #Revisa que los datos ingresados sean validos
            username = form.cleaned_data.get('username')#
            if User.objects.filter(username=username).exists(): #Revisa que el usuario no exista
                messages.error(request, "El nombre de usuario ya está en uso.")#tira un mensaje de error si el nombre de usuario ya esta registrado
            else:
                user = form.save(commit=False)  #Crea el usuario 
                user.set_password(form.cleaned_data.get('password')) #Guarda la contraseña de cada usuario
                user.is_active = True  # Activar el usuario inmediatamente
                user.save()#guarda los nuevos usuario en la base de datos
                
                messages.success(request, "Registro exitoso. Ahora puedes iniciar sesión.")#muestra un mensaje en la parte de login si el registro del usuario fue exitoso
                return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'registro.html', {'form': form})


def login_view(request):
    if request.method == 'POST':#verifica si el metodo de la solicitud es POST
                                #(es importante por que los datos del formulario se envian mediante una solicitus POST)
        username = request.POST.get('username')  # Guarda el usuario
        password = request.POST.get('password')  # Guarda la contraseña
        
        # Autenticación del usuario
        user = authenticate(request, username=username, password=password)#verifica las credenciales del usuario
        if user is not None:
            login(request, user)  # Inicia la sesión
            messages.success(request, 'Sesión iniciada correctamente.')
            return redirect('home')  # Redirige a la página principal
        else:
            messages.error(request, 'Usuario o contraseña incorrectos. Intenta nuevamente.')
            #se muestra un mensaje de error y dirije al login.html
    return render(request, 'login.html')


def calcular_paginacion(total_items, pagina_actual, items_por_pagina=20, paginas_por_grupo=10):
   
    total_paginas = (total_items + items_por_pagina - 1) // items_por_pagina #calcual cuantos indices se necesitaran, se suma los items de pagina menos 1 para redondear hacia arriba
    #sirve para no pasarse de los limites de los indices
    if pagina_actual < 1: 
        pagina_actual = 1
    elif pagina_actual > total_paginas:
        pagina_actual = total_paginas

    grupo_actual = (pagina_actual - 1) // paginas_por_grupo #divide los indices por grupos 
    inicio = grupo_actual * paginas_por_grupo + 1 #calcula cual seria el primer indice de cada grupo
    fin = min(inicio + paginas_por_grupo - 1, total_paginas) #calcula cual seria el ultimo indice del grupo
    paginas_mostrar = range(inicio, fin + 1) if total_paginas > 0 else [] #son la lista de paginas que se muestran en los indices
    inicio_slice = (pagina_actual - 1) * items_por_pagina #indica cual es el primer item a mostrar segun el indice
    fin_slice = min(inicio_slice + items_por_pagina, total_items) #indica cual es el ultimo item a mostrar segun el indice

    return {
        'paginas_mostrar': paginas_mostrar,
        'pagina_actual': pagina_actual,
        'total_paginas': total_paginas,
        'grupo_inicio': inicio,
        'grupo_fin': fin,
        'inicio_slice': inicio_slice,
        'fin_slice': fin_slice
    }

def home(request):
    #lleva a la pagina 1
    try:
        pagina = int(request.GET.get('page', 1))
    except ValueError:
        pagina = 1
    # obtiene información de la API
    api_info = services.getApiInfo()
    total_paginas = api_info['pages']
    
    paginacion = calcular_paginacion(total_paginas * 20, pagina) #crea los indices
   
    list_images = services.getAllImages(f"?page={pagina}")  # obtiene imagenes de la API para la página actual
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
    
    return render(request, 'home.html',contexto)

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
    #recorre toda la api buscando coincidencias de nombre y las agrega a una lista 
    while True:
        input = f"?page={current_page}&name={search_msg}"
        try:
            images = services.getAllImages(input)
        except Exception as e:
            print(f"Error al obtener imágenes: {e}")
            break

        if not images:
            break

        all_matching_images.extend(images) #se utiliza extend ya que es similar a append pero con varios elementos
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

    paginacion = calcular_paginacion(total_items, pagina) #se crean indices para las busquedas

    images_page = all_matching_images[paginacion['inicio_slice']:paginacion['fin_slice']] #crea una sublista con inicio y fin en las imagenes correspondientes al indice

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