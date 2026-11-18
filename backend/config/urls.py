from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('infraestrutura.urls')),
    path('api/rotas/', include('rotas.urls')),
    path('api/usuarios/', include('usuarios.urls')),
    path('api/relatos/', include('relatos.urls')),
   
]
