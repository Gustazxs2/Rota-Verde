from django.contrib.gis.geos import Point
from rest_framework import serializers

from .models import RelatoPerigo


class RelatoPerigoSerializer(serializers.ModelSerializer):

    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)

    localizacao = serializers.SerializerMethodField()

    categoria_display = serializers.CharField(
        source='get_categoria_display',
        read_only=True
    )

    autor = serializers.SerializerMethodField()

    class Meta:
        model = RelatoPerigo
        fields = [
            'id',
            'autor',
            'categoria',
            'categoria_display',
            'descricao',
            'latitude',
            'longitude',
            'localizacao',
            'criado_em',
        ]

    def validate_latitude(self, value):
        if not -90 <= value <= 90:
            raise serializers.ValidationError(
                'Latitude inválida.'
            )
        return value

    def validate_longitude(self, value):
        if not -180 <= value <= 180:
            raise serializers.ValidationError(
                'Longitude inválida.'
            )
        return value

    def get_localizacao(self, obj):
        return {
            'latitude': obj.localizacao.y,
            'longitude': obj.localizacao.x,
        }

    def get_autor(self, obj):
        return {
            'id': obj.autor.id,
            'nome': obj.autor.first_name,
        }

    def create(self, validated_data):
        latitude = validated_data.pop('latitude')
        longitude = validated_data.pop('longitude')

        validated_data['localizacao'] = Point(
            longitude,
            latitude,
            srid=4326
        )

        return super().create(validated_data)