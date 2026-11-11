from django.urls import path
from .views import CalcularRotaView

urlpatterns = [
    path(
        "calcular/",
        CalcularRotaView.as_view(),
        name="calcular-rota"
    ),
]
