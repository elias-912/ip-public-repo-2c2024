from django.contrib import admin
from django.urls import include, path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]

indice=[
    path('',views.home,name='home'),
    path('<int:page',views.home,name='home'),
]
