from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import RelatoPerigo
from .serializers import RelatoPerigoSerializer


class ListaCriaRelatosView(generics.ListCreateAPIView):
    serializer_class = RelatoPerigoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RelatoPerigo.objects.select_related('autor').filter(
            autor=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(autor=self.request.user)


class ExcluirRelatoView(generics.DestroyAPIView):
    queryset = RelatoPerigo.objects.all()
    serializer_class = RelatoPerigoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RelatoPerigo.objects.filter(
            autor=self.request.user
        )