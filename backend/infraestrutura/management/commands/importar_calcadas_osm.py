import json
from pathlib import Path

from django.contrib.gis.geos import GEOSGeometry
from django.core.management.base import BaseCommand, CommandError

from infraestrutura.models import Calcada


class Command(BaseCommand):
    help = "Importa calçadas do OpenStreetMap para o PostGIS."

    def handle(self, *args, **options):
        arquivo = Path("calcadas_belem.geojson")

        if not arquivo.exists():
            raise CommandError("Arquivo calcadas_belem.geojson não encontrado.")

        with arquivo.open(encoding="utf-8") as f:
            dados = json.load(f)

        elementos = dados.get("features", [])

        criadas = atualizadas = ignoradas = 0
        candidatas = 0

        for elemento in elementos:
            geometria_json = elemento.get("geometry")
            tags = elemento.get("properties", {})

            # Importar somente calçadas representadas como linhas.
            if (
                not geometria_json
                or geometria_json.get("type") != "LineString"
                or tags.get("highway") != "footway"
                or tags.get("footway") != "sidewalk"
            ):
                continue

            candidatas += 1

            try:
                # O ID vem no formato w259860468.
                identificador = str(elemento["id"])
                osm_id = int(identificador.split("/")[-1].lstrip("w"))

                geometria = GEOSGeometry(
                    json.dumps(geometria_json),
                    srid=4326
                )

                if geometria.geom_type != "LineString":
                    ignoradas += 1
                    continue

                wheelchair = tags.get("wheelchair", "").lower()

                acessivel = None
                if wheelchair == "yes":
                    acessivel = True
                elif wheelchair == "no":
                    acessivel = False

                valores = {
                    "nome": tags.get("name", ""),
                    "largura_m": None,
                    "acessivel": acessivel,
                    "tem_obstaculos": None,
                    "surface": tags.get("surface", ""),
                    "osm_tags": tags,
                    "geometria": geometria,
                    "fonte_dados": "OpenStreetMap",
                }

                _, criada = Calcada.objects.update_or_create(
                    osm_id=osm_id,
                    defaults=valores
                )

                if criada:
                    criadas += 1
                else:
                    atualizadas += 1

            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as erro:
                ignoradas += 1
                self.stderr.write(
                    f"Calçada ignorada: {elemento.get('id')} - {erro}"
                )

        self.stdout.write(self.style.SUCCESS(
            "\nImportação de calçadas concluída!\n"
            f"Elementos no GeoJSON: {len(elementos)}\n"
            f"Calçadas identificadas: {candidatas}\n"
            f"Criadas: {criadas}\n"
            f"Atualizadas: {atualizadas}\n"
            f"Ignoradas: {ignoradas}"
        ))
