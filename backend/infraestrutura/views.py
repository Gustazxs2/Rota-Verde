from rest_framework import viewsets

from .models import (
    Ciclovia,
    Calcada,
    Travessia,
    RecursoAcessibilidade
)

from .serializers import (
    CicloviaSerializer,
    CalcadaSerializer,
    TravessiaSerializer,
    RecursoAcessibilidadeSerializer
)


class CicloviaViewSet(viewsets.ModelViewSet):
    queryset = Ciclovia.objects.all()
    serializer_class = CicloviaSerializer


class CalcadaViewSet(viewsets.ModelViewSet):
    queryset = Calcada.objects.all()
    serializer_class = CalcadaSerializer


class TravessiaViewSet(viewsets.ModelViewSet):
    queryset = Travessia.objects.all()
    serializer_class = TravessiaSerializer


class RecursoAcessibilidadeViewSet(viewsets.ModelViewSet):
    queryset = RecursoAcessibilidade.objects.all()
    serializer_class = RecursoAcessibilidadeSerializer