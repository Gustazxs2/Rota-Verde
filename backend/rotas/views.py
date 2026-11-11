import json
import math

from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


def encontrar_vertice(latitude, longitude):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                id,
                ST_Distance(
                    geom::geography,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
                ) AS distancia_m
            FROM roteamento.rv_ways_vertices_pgr
            ORDER BY
                geom::geography
                <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
            LIMIT 1;
            """,
            [longitude, latitude, longitude, latitude]
        )

        resultado = cursor.fetchone()

    if resultado is None:
        return None

    return {
        "id": resultado[0],
        "distancia_m": round(float(resultado[1]), 2)
    }


def montar_sql_arestas(perfil):
    if perfil == "ciclista":
        multiplicador = """
            (
                CASE
                    WHEN o.tags->'highway' = 'cycleway' THEN 0.65
                    WHEN o.tags->'highway' IN ('residential', 'living_street') THEN 0.90
                    WHEN o.tags->'highway' IN ('service', 'unclassified') THEN 1.10
                    WHEN o.tags->'highway' = 'tertiary' THEN 1.20
                    WHEN o.tags->'highway' = 'secondary' THEN 1.50
                    WHEN o.tags->'highway' = 'primary' THEN 1.90
                    WHEN o.tags->'highway' IN ('trunk', 'trunk_link') THEN 2.50
                    WHEN o.tags->'highway' IN ('footway', 'pedestrian', 'path') THEN 1.50
                    WHEN o.tags->'highway' = 'steps' THEN 2.50
                    WHEN o.tags->'highway' = 'track' THEN 1.30
                    ELSE 1.20
                END
                *
                CASE
                    WHEN o.tags->'cycleway' IN ('track', 'lane', 'shared_lane')
                      OR o.tags->'cycleway:left' IN ('track', 'lane', 'shared_lane')
                      OR o.tags->'cycleway:right' IN ('track', 'lane', 'shared_lane')
                      OR o.tags->'cycleway:both' IN ('track', 'lane', 'shared_lane')
                    THEN 0.85
                    ELSE 1.0
                END
                *
                CASE
                    WHEN o.tags->'surface' IN ('asphalt', 'concrete', 'paved') THEN 1.0
                    WHEN o.tags->'surface' IN ('paving_stones', 'sett') THEN 1.15
                    WHEN o.tags->'surface' IN ('unpaved', 'gravel', 'ground', 'dirt') THEN 1.35
                    WHEN o.tags->'surface' IN ('sand', 'mud', 'grass') THEN 1.80
                    ELSE 1.0
                END
                *
                CASE
                    WHEN o.tags->'smoothness' = 'excellent' THEN 0.95
                    WHEN o.tags->'smoothness' = 'good' THEN 1.0
                    WHEN o.tags->'smoothness' = 'intermediate' THEN 1.15
                    WHEN o.tags->'smoothness' = 'bad' THEN 1.40
                    WHEN o.tags->'smoothness' = 'very_bad' THEN 1.80
                    WHEN o.tags->'smoothness' = 'very_horrible' THEN 2.50
                    ELSE 1.0
                END
                *
                CASE
                    WHEN o.tags->'bicycle' = 'dismount' THEN 4.0
                    ELSE 1.0
                END
            )
        """

        permissao = """
            CASE
                WHEN tags->'bicycle' IN ('no', 'private', 'customers', 'permit') THEN -1
                WHEN tags->'bicycle' IN ('yes', 'designated', 'permissive', 'dismount') THEN custo_base
                WHEN tags->'access' IN ('no', 'private', 'customers', 'permit', 'delivery') THEN -1
                ELSE custo_base
            END
        """

        sentido = """
            CASE
                WHEN o.tags ? 'oneway:bicycle' THEN COALESCE(o.tags->'oneway:bicycle', '')
                ELSE COALESCE(o.tags->'oneway', '')
            END
        """

    else:  # Pedestre
        multiplicador = """
            (
                CASE
                    WHEN o.tags->'highway' IN ('footway', 'pedestrian') THEN 0.70
                    WHEN o.tags->'highway' = 'path' THEN 0.85
                    WHEN o.tags->'highway' IN ('residential', 'living_street') THEN 1.0
                    WHEN o.tags->'highway' = 'service' THEN 1.10
                    WHEN o.tags->'highway' IN ('tertiary', 'unclassified') THEN 1.20
                    WHEN o.tags->'highway' = 'secondary' THEN 1.40
                    WHEN o.tags->'highway' = 'primary' THEN 1.70
                    WHEN o.tags->'highway' = 'cycleway' THEN 1.15
                    WHEN o.tags->'highway' = 'steps' THEN 1.30
                    ELSE 1.0
                END
                *
                CASE
                    WHEN o.tags->'sidewalk' IN ('both', 'left', 'right', 'yes') THEN 0.85
                    ELSE 1.0
                END
                *
                CASE
                    WHEN o.tags->'surface' IN ('asphalt', 'concrete', 'paved') THEN 1.0
                    WHEN o.tags->'surface' IN ('paving_stones', 'sett') THEN 1.10
                    WHEN o.tags->'surface' IN ('unpaved', 'gravel', 'ground', 'dirt') THEN 1.25
                    WHEN o.tags->'surface' IN ('sand', 'mud', 'grass') THEN 1.60
                    ELSE 1.0
                END
                *
                CASE
                    WHEN o.tags->'smoothness' = 'excellent' THEN 0.95
                    WHEN o.tags->'smoothness' = 'good' THEN 1.0
                    WHEN o.tags->'smoothness' = 'intermediate' THEN 1.10
                    WHEN o.tags->'smoothness' = 'bad' THEN 1.30
                    WHEN o.tags->'smoothness' = 'very_bad' THEN 1.60
                    WHEN o.tags->'smoothness' = 'very_horrible' THEN 2.0
                    ELSE 1.0
                END
            )
        """

        permissao = """
            CASE
                WHEN tags->'foot' IN ('no', 'private', 'customers', 'permit') THEN -1
                WHEN tags->'foot' IN ('yes', 'designated', 'permissive') THEN custo_base
                WHEN tags->'access' IN ('no', 'private', 'customers', 'permit', 'delivery') THEN -1
                ELSE custo_base
            END
        """

        sentido = "COALESCE(o.tags->'oneway:foot', '')"

    return f"""
        WITH dados AS (
            SELECT
                r.id,
                r.source,
                r.target,
                o.tags,
                GREATEST(COALESCE(r.length_m, 0.01), 0.01) * {multiplicador} AS custo_base,
                {sentido} AS sentido
            FROM roteamento.rv_ways r
            JOIN roteamento.osm_ways o ON o.osm_id = r.osm_id
        ),
        custos AS (
            SELECT
                id,
                source,
                target,
                tags,
                sentido,
                {permissao} AS custo_permitido
            FROM dados
        )
                SELECT
                    id,
                    source,
                    target,
                    CASE
                        WHEN custo_permitido < 0
                            OR sentido IN ('-1', 'reversible', 'alternating')
                        THEN -1
                        ELSE custo_permitido
                    END AS cost,
                    CASE
                        WHEN custo_permitido < 0
                            OR sentido IN ('yes', 'reversible', 'alternating')
                    THEN -1
                    ELSE custo_permitido
                END AS reverse_cost
            FROM custos
    """


class CalcularRotaView(APIView):
    def post(self, request):
        perfil = request.data.get("perfil", "ciclista")

        if perfil not in ("ciclista", "pedestre"):
            return Response(
                {"erro": "Perfil inválido. Utilize 'ciclista' ou 'pedestre'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        campos = [
            "origem_latitude", "origem_longitude",
            "destino_latitude", "destino_longitude"
        ]

        coordenadas = {}

        for campo in campos:
            try:
                valor = float(request.data[campo])

                if not math.isfinite(valor):
                    raise ValueError

            except (KeyError, TypeError, ValueError):
                return Response(
                    {"erro": f"Campo inválido ou ausente: {campo}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            coordenadas[campo] = valor

        # Validação de intervalos
        if not (
            -90 <= coordenadas["origem_latitude"] <= 90
            and -90 <= coordenadas["destino_latitude"] <= 90
        ):
            return Response(
                {"erro": "Latitude fora do intervalo permitido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not (
            -180 <= coordenadas["origem_longitude"] <= 180
            and -180 <= coordenadas["destino_longitude"] <= 180
        ):
            return Response(
                {"erro": "Longitude fora do intervalo permitido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        origem = encontrar_vertice(
            coordenadas["origem_latitude"],
            coordenadas["origem_longitude"]
        )

        destino = encontrar_vertice(
            coordenadas["destino_latitude"],
            coordenadas["destino_longitude"]
        )

        if origem is None or destino is None:
            return Response(
                {"erro": "Não foi possível encontrar vértices na malha viária."},
                status=status.HTTP_404_NOT_FOUND
            )

        if origem["id"] == destino["id"]:
            return Response(
                {
                    "erro": "Origem e destino são o mesmo vértice.",
                    "vertice": origem
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        sql_arestas = montar_sql_arestas(perfil)

        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                WITH caminho AS (
                    SELECT * FROM pgr_dijkstra(
                        $edges$ {sql_arestas} $edges$,
                        %s, %s, directed := true
                    )
                ),
                segmentos AS (
                    SELECT
                        c.path_seq,
                        c.cost,
                        CASE
                            WHEN c.node = v.source THEN v.geom
                            ELSE ST_Reverse(v.geom)
                        END AS geom
                    FROM caminho c
                    JOIN roteamento.rv_ways v ON v.id = c.edge
                    WHERE c.edge <> -1
                ),
                resumo AS (
                    SELECT
                        ST_MakeLine(geom ORDER BY path_seq) AS geom,
                        COUNT(*) AS quantidade_segmentos,
                        SUM(cost) AS custo_total
                    FROM segmentos
                )
                SELECT
                    ST_AsGeoJSON(geom, 7),
                    quantidade_segmentos,
                    custo_total,
                    ST_Length(geom::geography)
                FROM resumo
                WHERE geom IS NOT NULL;
                """,
                [origem["id"], destino["id"]]
            )

            resultado = cursor.fetchone()

        if resultado is None:
            return Response(
                {
                    "erro": "Não foi encontrada uma rota entre os pontos.",
                    "perfil": perfil
                },
                status=status.HTTP_404_NOT_FOUND
            )

        geojson = json.loads(resultado[0])

        return Response({
            "type": "Feature",
            "geometry": geojson,
            "properties": {
                "perfil": perfil,
                "vertice_origem": origem["id"],
                "vertice_destino": destino["id"],
                "distancia_ate_origem_m": origem["distancia_m"],
                "distancia_ate_destino_m": destino["distancia_m"],
                "quantidade_segmentos": resultado[1],
                "custo_total": float(resultado[2]),
                "distancia_m": round(float(resultado[3]), 2),
                "distancia_km": round(float(resultado[3]) / 1000, 3)
            }
        })