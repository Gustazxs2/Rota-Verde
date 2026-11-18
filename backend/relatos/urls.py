from django.urls import path
from . import views

urlpatterns = [
    path(
        '',
        views.ListaCriaRelatosView.as_view(),
        name='lista-cria-relatos'
    ),
    path(
        '<int:pk>/',
        views.ExcluirRelatoView.as_view(),
        name='excluir-relato'
    ),
]