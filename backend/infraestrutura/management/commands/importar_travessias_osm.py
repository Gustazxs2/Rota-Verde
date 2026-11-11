import json
from pathlib import Path

from django.contrib.gis.geos import GEOSGeometry
from django.core.management.base import BaseCommand, CommandError

from infraestrutura.models import Travessia


class BaseCommandImportacao(BaseCommand):
    def importar_arquivo(self, arquivo):
        caminho = Path(arquivo)

        if not caminho.exists():
            raise CommandError(f"Arquivo {arquivo} não encontrado.")

        with caminho.open(encoding="utf-8") as f:
            dados = json.load(f)

        criadas = atualizadas = ignoradas = 0

        for elemento in dados.get("features", []):
            try:
                identificador = elemento.get("id")
                geometria_json = elemento.get("geometry")
                tags = elemento.get("properties", {})

                if not identificador or not geometria_json:
                    ignoradas += 1
                    continue

                tipo = geometria_json.get("type")

                if tipo not in ("Point", "LineString"):
                    ignoradas += 1
                    continue

                geometria = GEOSGeometry(
                    json.dumps(geometria_json),
                    srid=4326
                )

                # Sinalização explícita.
                crossing = tags.get("crossing", "").lower()
                markings = tags.get("crossing:markings", "").lower()

                sinalizada = None

                if crossing in ("marked", "zebra"):
                    sinalizada = True
                elif crossing == "unmarked":
                    sinalizada = False
                elif markings == "yes":
                    sinalizada = True
                elif markings == "no":
                    sinalizada = False

                # Semáforo explícito.
                crossing_signals = tags.get("crossing:signals", "").lower()

                semaforizada = None

                if crossing == "traffic_signals" or crossing_signals == "yes":
                    semaforizada = True
                elif crossing_signals == "no":
                    semaforizada = False

                valores = {
                    "nome": tags.get("name", ""),
                    "sinalizada": sinalizada,
                    "semaforizada": semaforizada,
                    "elevada": None,
                    "osm_tags": tags,
                    "geometria": geometria,
                    "fonte_dados": "OpenStreetMap",
                }

                _, criada = Travessia.objects.update_or_create(
                    osm_id=identificador,
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

        return criadas, atualizadas, ignoradas


class Command(BaseCommandImportacao):
    help = "Importa travessias do OpenStreetMap para o PostGIS."

    def handle(self, *args, **options):
        arquivos = [
            "travessias_pontos_belem.geojson",
            "travessias_belem.geojson",
        ]

        total_criadas = total_atualizadas = total_ignoradas = 0

        for arquivo in arquivos:
            criadas, atualizadas, ignoradas = self.importar_arquivo(arquivo)

            total_criadas += criadas
            total_atualizadas += atualizadas
            total_ignoradas += ignoradas

            self.stdout.write(f"\nArquivo: {arquivo}")
            self.stdout.write(f"Criadas: {criadas}")
            self.stdout.write(f"Atualizadas: {atualizadas}")
            self.stdout.write(f"Ignoradas: {ignoradas}")

        self.stdout.write(self.style.SUCCESS(
            "\nImportação de travessias concluída!\n"
            f"Total criadas: {total_criadas}\n"
            f"Total atualizadas: {total_atualizadas}\n"
            f"Total ignoradas: {total_ignoradas}"
        ))
