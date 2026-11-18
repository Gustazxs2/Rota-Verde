from django.urls import path
from .views import CalcularRotaView, BuscarDestinoView

urlpatterns = [
    path(
        "calcular/",
        CalcularRotaView.as_view(),
        name="calcular-rota"
    ),
    path(
        "buscar-destino/",
        BuscarDestinoView.as_view(),
        name="buscar-destino"
    ),
]