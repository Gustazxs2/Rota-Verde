from django.contrib.gis.db import models


class PontoIluminacao(models.Model):
    nome = models.CharField(max_length=100)

    localizacao = models.PointField()

    ativo = models.BooleanField(default=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome