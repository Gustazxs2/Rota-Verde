from rest_framework import serializers
from .models import PontoIluminacao


class PontoIluminacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PontoIluminacao
        fields = "__all__"