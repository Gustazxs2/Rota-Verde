import json

from django.contrib.gis.geos import GEOSGeometry
from rest_framework import serializers

from .models import (
    Ciclovia,
    Calcada,
    Travessia,
    RecursoAcessibilidade
)


class GeoJSONGeometryField(serializers.Field):

    def __init__(self, expected_type, **kwargs):
        self.expected_type = expected_type
        super().__init__(**kwargs)

    def to_representation(self, value):
        if value is None:
            return None

        return json.loads(value.geojson)

    def to_internal_value(self, data):
        try:
            geometry = GEOSGeometry(json.dumps(data), srid=4326)

            if geometry.geom_type != self.expected_type:
                raise serializers.ValidationError(
                    f"Esperado: {self.expected_type}."
                )

            if geometry.srid != 4326:
                raise serializers.ValidationError(
                    "Utilize coordenadas no sistema SRID 4326."
                )

            return geometry

        except (ValueError, TypeError, OSError):
            raise serializers.ValidationError(
                "Geometria GeoJSON inválida."
            )


class CicloviaSerializer(serializers.ModelSerializer):

    geometria = GeoJSONGeometryField(
        expected_type="LineString"
    )

    class Meta:
        model = Ciclovia
        fields = "__all__"


class CalcadaSerializer(serializers.ModelSerializer):

    geometria = GeoJSONGeometryField(
        expected_type="LineString"
    )

    class Meta:
        model = Calcada
        fields = "__all__"


class TravessiaSerializer(serializers.ModelSerializer):

    geometria = GeoJSONGeometryField(
        expected_type="LineString"
    )

    class Meta:
        model = Travessia
        fields = "__all__"


class RecursoAcessibilidadeSerializer(serializers.ModelSerializer):

    geometria = GeoJSONGeometryField(
        expected_type="Point"
    )

    class Meta:
        model = RecursoAcessibilidade
        fields = "__all__"