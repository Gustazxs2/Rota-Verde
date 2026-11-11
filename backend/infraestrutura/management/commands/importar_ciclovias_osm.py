import json

from pathlib import Path

from django.contrib.gis.geos import LineString
from django.core.management.base import BaseCommand, CommandError

from infraestrutura.models import Ciclovia


class Command(BaseCommand):
    help = "Importa ciclovias do OpenStreetMap para o PostGIS."

    def handle(self, *args, **options):
        arquivo = Path("resultado_ciclovias.json")

        if not arquivo.exists():
            raise CommandError(
                "Arquivo resultado_ciclovias.json não encontrado."
            )

        with arquivo.open(encoding="utf-8") as f:
            dados = json.load(f)

        elementos = dados.get("elements", [])

        criadas = 0
        atualizadas = 0
        ignoradas = 0

        for elemento in elementos:
            try:
                osm_id = elemento["id"]
                tags = elemento.get("tags", {})
                pontos = elemento.get("geometry", [])

                # Precisamos de pelo menos dois pontos para uma LineString.
                if len(pontos) < 2:
                    ignoradas += 1
                    continue

                coordenadas = [
                    (ponto["lon"], ponto["lat"])
                    for ponto in pontos
                ]

                geometria = LineString(
                    coordenadas,
                    srid=4326
                )

                nome = tags.get("name", "")

                segregada = None

                if tags.get("segregated") == "yes":
                    segregada = True
                elif tags.get("segregated") == "no":
                    segregada = False

                valores = {
                    "nome": nome,
                    "tipo": "ciclovia",
                    "segregada": segregada,
                    "surface": tags.get("surface", ""),
                    "osm_tags": tags,
                    "geometria": geometria,
                    "fonte_dados": "OpenStreetMap",
                }

                _, criada = Ciclovia.objects.update_or_create(
                    osm_id=osm_id,
                    defaults=valores
                )

                if criada:
                    criadas += 1
                else:
                    atualizadas += 1

            except (KeyError, TypeError, ValueError) as erro:
                ignoradas += 1
                self.stderr.write(
                    f"Elemento ignorado: {elemento.get('id')} - {erro}"
                )

        self.stdout.write(
            self.style.SUCCESS(
                "\nImportação concluída!\n"
                f"Criadas: {criadas}\n"
                f"Atualizadas: {atualizadas}\n"
                f"Ignoradas: {ignoradas}\n"
                f"Total recebido: {len(elementos)}"
            )
        )
