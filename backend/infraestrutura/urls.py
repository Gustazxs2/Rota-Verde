from rest_framework.routers import DefaultRouter

from .views import (
    CicloviaViewSet,
    CalcadaViewSet,
    TravessiaViewSet,
    RecursoAcessibilidadeViewSet
)

router = DefaultRouter()

router.register('ciclovias', CicloviaViewSet)
router.register('calcadas', CalcadaViewSet)
router.register('travessias', TravessiaViewSet)
router.register('recursos-acessibilidade', RecursoAcessibilidadeViewSet)

urlpatterns = router.urls