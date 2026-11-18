from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("cadastro/", views.cadastro, name="cadastro"),
    path("login/", views.login, name="login"),
    path("me/", views.meu_perfil, name="meu_perfil"),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh"
    ),
]