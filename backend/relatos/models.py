from django.conf import settings
from django.contrib.gis.db import models


class RelatoPerigo(models.Model):

    CATEGORIAS = [
        ('buraco', 'Buraco na via'),
        ('iluminacao', 'Iluminação insuficiente'),
        ('obstaculo', 'Obstáculo na via'),
        ('assalto', 'Risco de assalto'),
        ('acidente', 'Acidente'),
        ('alagamento', 'Alagamento'),
        ('outro', 'Outro'),
    ]

    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='relatos_perigo'
    )

    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIAS
    )

    descricao = models.TextField(
        max_length=500
    )

    localizacao = models.PointField(
        srid=4326
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Relato de perigo'
        verbose_name_plural = 'Relatos de perigo'

    def __str__(self):
        return f'{self.get_categoria_display()} - {self.autor}'