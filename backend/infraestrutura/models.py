from django.contrib.gis.db import models


class InfraestruturaBase(models.Model):

    CONDICOES = [
        ('boa', 'Boa'),
        ('regular', 'Regular'),
        ('ruim', 'Ruim'),
        ('desconhecida', 'Desconhecida'),
    ]

    nome = models.CharField(max_length=150, blank=True)

    condicao = models.CharField(
        max_length=20,
        choices=CONDICOES,
        default='desconhecida'
    )

    fonte_dados = models.CharField(
        max_length=100,
        blank=True
    )

    verificado_em = models.DateTimeField(
        null=True,
        blank=True
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Ciclovia(InfraestruturaBase):
    TIPOS = [
        ('ciclovia', 'Ciclovia'),
        ('ciclofaixa', 'Ciclofaixa'),
        ('ciclorrota', 'Ciclorrota'),
        ('compartilhada', 'Via compartilhada'),
    ]

    osm_id = models.BigIntegerField(
        unique=True,
        null=True,
        blank=True
    )

    tipo = models.CharField(max_length=20, choices=TIPOS)

    segregada = models.BooleanField(
        null=True,
        blank=True,
        default=None
    )

    surface = models.CharField(max_length=100, blank=True)

    osm_tags = models.JSONField(default=dict, blank=True)

    geometria = models.LineStringField(srid=4326)

    def __str__(self):
        return self.nome or f'Ciclovia {self.pk}'


class Calcada(InfraestruturaBase):
    osm_id = models.BigIntegerField(unique=True, null=True, blank=True)
    largura_m = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    acessivel = models.BooleanField(null=True, blank=True)
    tem_obstaculos = models.BooleanField(null=True, blank=True)
    surface = models.CharField(max_length=100, blank=True)
    osm_tags = models.JSONField(default=dict, blank=True)
    geometria = models.LineStringField(srid=4326)


class Travessia(InfraestruturaBase):

    osm_id = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True
    )

    sinalizada = models.BooleanField(
        null=True,
        blank=True
    )

    semaforizada = models.BooleanField(
        null=True,
        blank=True
    )

    elevada = models.BooleanField(
        null=True,
        blank=True
    )

    osm_tags = models.JSONField(
        default=dict,
        blank=True
    )

    geometria = models.GeometryField(srid=4326)

    def __str__(self):
        return self.nome or f'Travessia {self.pk}'


class RecursoAcessibilidade(InfraestruturaBase):

    TIPOS = [
        ('rampa', 'Rampa de acessibilidade'),
        ('piso_tatil', 'Piso tátil'),
        ('semaforo_sonoro', 'Semáforo sonoro'),
        ('rebaixamento', 'Rebaixamento de guia'),
        ('outro', 'Outro'),
    ]

    osm_id = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True
    )

    tipo = models.CharField(
        max_length=30,
        choices=TIPOS
    )

    osm_tags = models.JSONField(default=dict, blank=True)

    geometria = models.GeometryField(srid=4326)

    def __str__(self):
        return self.nome or f'Recurso de acessibilidade {self.pk}'