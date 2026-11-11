import json
from pathlib import Path

from django.contrib.gis.geos import GEOSGeometry
from django.core.management.base import BaseCommand, CommandError

from infraestrutura.models import RecursoAcessibilidade


class Command(BaseCommand):
    help = "Importa recursos de acessibilidade do OpenStreetMap."

    def handle(self, *args, **options):
        arquivo = Path("recursos_acessibilidade_belem.geojson")

        if not arquivo.exists():
            raise CommandError(f"Arquivo {arquivo} não encontrado.")

        with arquivo.open(encoding="utf-8") as f:
            dados = json.load(f)

        criadas = 0
        atualizadas = 0
        ignoradas = 0

        for elemento in dados.get("features", []):
            try:
                identificador = elemento.get("id")
                geometria_json = elemento.get("geometry")
                tags = elemento.get("properties", {})

                if not identificador or not geometria_json:
                    ignoradas += 1
                    continue

                # Identifica o tipo de recurso.
                tipo = None

                if tags.get("kerb") == "lowered":
                    tipo = "rebaixamento"

                elif tags.get("tactile_paving") == "yes":
                    tipo = "piso_tatil"

                elif tags.get("traffic_signals:sound") == "yes":
                    tipo = "semaforo_sonoro"

                # Não importa elementos sem recurso positivo identificado.
                if not tipo:
                    ignoradas += 1
                    continue

                geometria = GEOSGeometry(
                    json.dumps(geometria_json),
                    srid=4326
                )

                valores = {
                    "nome": tags.get("name", ""),
                    "tipo": tipo,
                    "osm_tags": tags,
                    "geometria": geometria,
                    "fonte_dados": "OpenStreetMap",
                }

                _, criada = RecursoAcessibilidade.objects.update_or_create(
                    osm_id=identificador,
                    defaults=valores
                )

                if criada:
                    criadas += 1
                else:
                    atualizadas += 1

            except Exception as erro:
                ignoradas += 1
                self.stderr.write(
                    f"Elemento ignorado: {elemento.get('id')} - {erro}"
                )

        self.stdout.write(self.style.SUCCESS(
            "\nImportação de recursos de acessibilidade concluída!\n"
            f"Criados: {criadas}\n"
            f"Atualizados: {atualizadas}\n"
            f"Ignorados: {ignoradas}\n"
        ))
