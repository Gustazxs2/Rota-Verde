import json
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone


TABELAS_INFRA = {
    "public.infraestrutura_calcada": {
        "geometria": "geometria",
        "osm_id": "osm_id",
        "classificacao": "condicao",
    },
    "public.infraestrutura_ciclovia": {
        "geometria": "geometria",
        "osm_id": "osm_id",
        "classificacao": "tipo",
    },
    "public.infraestrutura_recursoacessibilidade": {
        "geometria": "geometria",
        "osm_id": "osm_id",
        "classificacao": "tipo",
    },
    "public.infraestrutura_travessia": {
        "geometria": "geometria",
        "osm_id": "osm_id",
        "classificacao": "sinalizada",
    },
    "public.rotas_pontoiluminacao": {
        "geometria": "localizacao",
        "osm_id": None,
        "classificacao": "ativo",
    },
}

TABELAS_REDE = [
    "roteamento.configuration",
    "roteamento.osm_nodes",
    "roteamento.osm_relations",
    "roteamento.osm_ways",
    "roteamento.rv_pointsofinterest",
    "roteamento.rv_ways",
    "roteamento.rv_ways_vertices_pgr",
]


class Command(BaseCommand):
    help = "Executa uma auditoria somente de leitura do banco do Rota Verde."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resultado = {
            "projeto": "Rota Verde",
            "data_auditoria": timezone.now().isoformat(),
            "observacao": (
                "Auditoria somente de leitura. "
                "Nenhum registro foi alterado."
            ),
            "resumo": {},
            "tabelas": {},
            "infraestrutura": {},
            "rede": {},
            "roteamento": {},
            "erros": [],
        }

    def consultar(self, sql, parametros=None):
        with connection.cursor() as cursor:
            cursor.execute(sql, parametros or [])
            colunas = [item[0] for item in cursor.description]
            return [
                dict(zip(colunas, linha))
                for linha in cursor.fetchall()
            ]

    def executar(self, sql, parametros=None):
        with connection.cursor() as cursor:
            cursor.execute(sql, parametros or [])
            return cursor.fetchone()

    def registrar_erro(self, etapa, erro):
        self.resultado["erros"].append({
            "etapa": etapa,
            "erro": str(erro),
        })

        self.stderr.write(
            self.style.WARNING(f"Falha em {etapa}: {erro}")
        )

    def verificar_tabela(self, tabela):
        schema, nome = tabela.split(".", 1)

        resultado = self.executar(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = %s
                  AND table_name = %s
            )
            """,
            [schema, nome],
        )

        return resultado[0]

    def auditar_tabelas(self):
        todas = list(TABELAS_INFRA.keys()) + TABELAS_REDE

        for tabela in todas:
            try:
                if not self.verificar_tabela(tabela):
                    self.resultado["tabelas"][tabela] = {
                        "status": "TABELA NÃO ENCONTRADA"
                    }
                    continue

                total = self.executar(
                    f"SELECT COUNT(*) FROM {tabela}"
                )[0]

                self.resultado["tabelas"][tabela] = {
                    "status": "OK",
                    "total_registros": total,
                }

            except Exception as erro:
                self.registrar_erro(
                    f"Contagem de {tabela}", erro
                )

    def auditar_infraestrutura(self):
        for tabela, config in TABELAS_INFRA.items():
            try:
                if not self.verificar_tabela(tabela):
                    continue

                geometria = config["geometria"]

                dados = self.executar(
                    f"""
                    SELECT
                        COUNT(*) AS total,
                        COUNT(*) FILTER (
                            WHERE {geometria} IS NULL
                        ) AS geometria_nula,
                        COUNT(*) FILTER (
                            WHERE {geometria} IS NOT NULL
                              AND ST_IsEmpty({geometria})
                        ) AS geometria_vazia,
                        COUNT(*) FILTER (
                            WHERE {geometria} IS NOT NULL
                              AND NOT ST_IsValid({geometria})
                        ) AS geometria_invalida,
                        COUNT(DISTINCT ST_SRID({geometria}))
                            FILTER (
                                WHERE {geometria} IS NOT NULL
                            ) AS quantidade_srids
                    FROM {tabela}
                    """
                )

                colunas = [
                    "total",
                    "geometria_nula",
                    "geometria_vazia",
                    "geometria_invalida",
                    "quantidade_srids",
                ]

                resultado = dict(zip(colunas, dados))

                resultado["tipos_geometria"] = self.consultar(
                    f"""
                    SELECT
                        ST_GeometryType({geometria}) AS tipo,
                        COUNT(*) AS quantidade
                    FROM {tabela}
                    WHERE {geometria} IS NOT NULL
                    GROUP BY ST_GeometryType({geometria})
                    ORDER BY quantidade DESC
                    """
                )

                classificacao = config["classificacao"]

                resultado["classificacoes"] = self.consultar(
                    f"""
                    SELECT
                        COALESCE(
                            {classificacao}::text,
                            'NULL'
                        ) AS classificacao,
                        COUNT(*) AS quantidade
                    FROM {tabela}
                    GROUP BY {classificacao}
                    ORDER BY quantidade DESC
                    """
                )

                osm_id = config["osm_id"]

                if osm_id:
                    duplicidades = self.consultar(
                        f"""
                        SELECT
                            {osm_id}::text AS osm_id,
                            COUNT(*) AS quantidade
                        FROM {tabela}
                        WHERE {osm_id} IS NOT NULL
                        GROUP BY {osm_id}
                        HAVING COUNT(*) > 1
                        ORDER BY quantidade DESC
                        LIMIT 100
                        """
                    )

                    resultado["osm_ids_duplicados"] = duplicidades

                    resultado["total_osm_ids_duplicados"] = (
                        len(duplicidades)
                    )

                self.resultado["infraestrutura"][tabela] = resultado

            except Exception as erro:
                self.registrar_erro(
                    f"Infraestrutura {tabela}", erro
                )

    def auditar_associacoes(self):
        for tabela, config in TABELAS_INFRA.items():
            if tabela == "public.rotas_pontoiluminacao":
                continue

            try:
                geometria = config["geometria"]

                resultado = self.executar(
                    f"""
                    SELECT
                        COUNT(*) AS total_registros,
                        COUNT(*) FILTER (
                            WHERE EXISTS (
                                SELECT 1
                                FROM roteamento.rv_ways r
                                WHERE ST_DWithin(
                                    a.{geometria},
                                    r.geom,
                                    0.00005
                                )
                            )
                        ) AS ate_aproximadamente_5m,
                        COUNT(*) FILTER (
                            WHERE EXISTS (
                                SELECT 1
                                FROM roteamento.rv_ways r
                                WHERE ST_DWithin(
                                    a.{geometria},
                                    r.geom,
                                    0.00010
                                )
                            )
                        ) AS ate_aproximadamente_11m,
                        COUNT(*) FILTER (
                            WHERE EXISTS (
                                SELECT 1
                                FROM roteamento.rv_ways r
                                WHERE ST_DWithin(
                                    a.{geometria},
                                    r.geom,
                                    0.00020
                                )
                            )
                        ) AS ate_aproximadamente_22m
                    FROM {tabela} a
                    WHERE a.{geometria} IS NOT NULL
                    """
                )

                self.resultado["infraestrutura"].setdefault(
                    tabela, {}
                )["proximidade_rede"] = {
                    "total_registros": resultado[0],
                    "ate_aproximadamente_5m": resultado[1],
                    "ate_aproximadamente_11m": resultado[2],
                    "ate_aproximadamente_22m": resultado[3],
                    "observacao": (
                        "Distâncias aproximadas em graus decimais, "
                        "decimais, não metros exatos."
                    ),
                }

            except Exception as erro:
                self.registrar_erro(
                    f"Associação espacial {tabela}", erro
                )

        try:
            resultado = self.executar(
                """
                SELECT
                    COUNT(*) AS total,
                    COUNT(*) FILTER (
                        WHERE ativo IS TRUE
                    ) AS ativos,
                    COUNT(*) FILTER (
                        WHERE ativo IS FALSE
                    ) AS inativos,
                    COUNT(*) FILTER (
                        WHERE localizacao IS NOT NULL
                          AND ST_SRID(localizacao) <> 4326
                    ) AS srid_diferente_4326
                FROM public.rotas_pontoiluminacao
                """
            )

            self.resultado["infraestrutura"][
                "public.rotas_pontoiluminacao"
            ]["iluminacao"] = {
                "total": resultado[0],
                "ativos": resultado[1],
                "inativos": resultado[2],
                "srid_diferente_4326": resultado[3],
            }

        except Exception as erro:
            self.registrar_erro("Iluminação pública", erro)

    def auditar_rede(self):
        try:
            dados = self.executar(
                """
                SELECT
                    COUNT(*) AS total_arestas,
                    COUNT(*) FILTER (
                        WHERE geom IS NULL
                    ) AS geometria_nula,
                    COUNT(*) FILTER (
                        WHERE geom IS NOT NULL
                          AND NOT ST_IsValid(geom)
                    ) AS geometria_invalida,
                    COUNT(*) FILTER (
                        WHERE source IS NULL OR target IS NULL
                    ) AS extremos_nulos,
                    COUNT(*) FILTER (
                        WHERE cost < 0
                    ) AS custo_negativo,
                    COUNT(*) FILTER (
                        WHERE reverse_cost < 0
                    ) AS custo_reverso_negativo,
                    COUNT(DISTINCT id) AS ids_distintos
                FROM roteamento.rv_ways
                """
            )

            campos = [
                "total_arestas",
                "geometria_nula",
                "geometria_invalida",
                "extremos_nulos",
                "custo_negativo",
                "custo_reverso_negativo",
                "ids_distintos",
            ]

            self.resultado["rede"]["arestas"] = dict(
                zip(campos, dados)
            )

            vertices = self.executar(
                """
                SELECT
                    COUNT(*) AS total_vertices,
                    COUNT(DISTINCT id) AS ids_distintos,
                    COUNT(*) FILTER (
                        WHERE geom IS NULL
                    ) AS geometria_nula,
                    COUNT(*) FILTER (
                        WHERE geom IS NOT NULL
                          AND NOT ST_IsValid(geom)
                    ) AS geometria_invalida
                FROM roteamento.rv_ways_vertices_pgr
                """
            )

            self.resultado["rede"]["vertices"] = {
                "total": vertices[0],
                "ids_distintos": vertices[1],
                "geometria_nula": vertices[2],
                "geometria_invalida": vertices[3],
            }

            conexoes = self.executar(
                """
                SELECT
                    COUNT(*) FILTER (
                        WHERE s.id IS NULL
                    ) AS source_inexistente,
                    COUNT(*) FILTER (
                        WHERE t.id IS NULL
                    ) AS target_inexistente
                FROM roteamento.rv_ways r
                LEFT JOIN roteamento.rv_ways_vertices_pgr s
                    ON s.id = r.source
                LEFT JOIN roteamento.rv_ways_vertices_pgr t
                    ON t.id = r.target
                """
            )

            self.resultado["rede"]["conexoes"] = {
                "source_inexistente": conexoes[0],
                "target_inexistente": conexoes[1],
            }

        except Exception as erro:
            self.registrar_erro("Rede de roteamento", erro)

    def auditar_perfis(self):
        try:
            from rotas.views import montar_sql_arestas

            for perfil in ["ciclista", "pedestre"]:
                sql = montar_sql_arestas(perfil)

                resultado = self.executar(
                    f"""
                    SELECT
                        COUNT(*) AS total,
                        COUNT(DISTINCT id) AS ids_distintos,
                        COUNT(*) FILTER (
                            WHERE cost >= 0
                        ) AS permitidas,
                        COUNT(*) FILTER (
                            WHERE cost < 0
                        ) AS bloqueadas,
                        COUNT(*) FILTER (
                            WHERE reverse_cost < 0
                        ) AS reversos_bloqueados
                    FROM ({sql}) AS arestas
                    """
                )

                self.resultado["roteamento"][perfil] = {
                    "total_arestas": resultado[0],
                    "ids_distintos": resultado[1],
                    "permitidas": resultado[2],
                    "bloqueadas": resultado[3],
                    "reversos_bloqueados": resultado[4],
                }

                busway = self.executar(
                    f"""
                    SELECT
                        COUNT(*) AS total_busway,
                        COUNT(*) FILTER (
                            WHERE a.cost < 0
                        ) AS bloqueadas,
                        COUNT(*) FILTER (
                            WHERE a.cost >= 0
                        ) AS permitidas
                    FROM ({sql}) a
                    JOIN roteamento.rv_ways r
                        ON r.id = a.id
                    JOIN roteamento.osm_ways o
                        ON o.osm_id = r.osm_id
                    WHERE o.tags->'highway' = 'busway'
                    """
                )

                self.resultado["roteamento"][perfil][
                    "busway"
                ] = {
                    "total": busway[0],
                    "bloqueadas": busway[1],
                    "permitidas": busway[2],
                }

        except Exception as erro:
            self.registrar_erro(
                "Regras de roteamento dos perfis", erro
            )

    def salvar_relatorios(self):
        pasta = Path("relatorios/auditoria")
        pasta.mkdir(parents=True, exist_ok=True)

        identificador = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        arquivo_json = pasta / (
            f"auditoria_{identificador}.json"
        )

        arquivo_md = pasta / (
            f"auditoria_{identificador}.md"
        )

        self.resultado["resumo"] = {
            "tabelas_analisadas": len(
                self.resultado["tabelas"]
            ),
            "infraestruturas_analisadas": len(
                self.resultado["infraestrutura"]
            ),
            "erros_na_execucao": len(
                self.resultado["erros"]
            ),
        }

        with arquivo_json.open(
            "w", encoding="utf-8"
        ) as arquivo:
            json.dump(
                self.resultado,
                arquivo,
                ensure_ascii=False,
                indent=2,
                default=str,
            )

        linhas = [
            "# Auditoria do Rota Verde",
            "",
            f"Data: {self.resultado['data_auditoria']}",
            "",
            "## Resumo",
            "",
            f"- Tabelas analisadas: "
            f"{self.resultado['resumo']['tabelas_analisadas']}",
            f"- Infraestruturas analisadas: "
            f"{self.resultado['resumo']['infraestruturas_analisadas']}",
            f"- Erros durante a auditoria: "
            f"{self.resultado['resumo']['erros_na_execucao']}",
            "",
            "## Tabelas",
            "",
        ]

        for tabela, dados in self.resultado["tabelas"].items():
            linhas.append(f"### {tabela}")
            linhas.append("")
            linhas.append(f"```json\n{json.dumps(dados, ensure_ascii=False, indent=2, default=str)}\n```")
            linhas.append("")

        for secao in [
            "infraestrutura",
            "rede",
            "roteamento",
            "erros",
        ]:
            linhas.append(f"## {secao.capitalize()}")
            linhas.append("")
            linhas.append(
                "```json\n"
                + json.dumps(
                    self.resultado[secao],
                    ensure_ascii=False,
                    indent=2,
                    default=str,
                )
                + "\n```"
            )
            linhas.append("")

        arquivo_md.write_text(
            "\n".join(linhas),
            encoding="utf-8",
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Relatório JSON: {arquivo_json}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Relatório Markdown: {arquivo_md}"
            )
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                "Iniciando auditoria do Rota Verde..."
            )
        )

        etapas = [
            ("Tabelas", self.auditar_tabelas),
            ("Infraestrutura", self.auditar_infraestrutura),
            ("Associações espaciais", self.auditar_associacoes),
            ("Rede de roteamento", self.auditar_rede),
            ("Perfis de roteamento", self.auditar_perfis),
        ]

        for nome, funcao in etapas:
            self.stdout.write(f"\nAnalisando: {nome}...")
            try:
                funcao()
            except Exception as erro:
                self.registrar_erro(nome, erro)

        self.salvar_relatorios()

        self.stdout.write(
            self.style.SUCCESS(
                "\nAuditoria finalizada."
            )
        )
