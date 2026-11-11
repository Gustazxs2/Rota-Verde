# Rota-Verde

**Mobilidade urbana mais acessível, consciente e segura para ciclistas e pedestres.**

O Rota Verde é um projeto de mobilidade urbana que tem como objetivo auxiliar ciclistas e pedestres a encontrarem rotas mais adequadas para seus deslocamentos.

A aplicação utiliza dados geográficos do OpenStreetMap e tecnologias de geoprocessamento para analisar a infraestrutura urbana e calcular caminhos considerando características das vias, condições de circulação e restrições específicas de cada perfil.

O projeto utiliza informações geográficas de Belém, no Pará, como base para o desenvolvimento e os testes do sistema.

---

## 📌 Objetivos do projeto

- Calcular rotas para ciclistas e pedestres.
- Considerar características da infraestrutura urbana durante o cálculo.
- Utilizar informações geográficas para representar a malha viária.
- Considerar restrições de circulação e sentidos permitidos nas vias.
- Disponibilizar informações sobre ciclovias, calçadas, travessias e recursos de acessibilidade.
- Incentivar formas de deslocamento urbano mais sustentáveis.

---

## 🚀 Funcionalidades

### Implementadas

- [x] Cálculo de rotas para ciclistas.
- [x] Cálculo de rotas para pedestres.
- [x] Utilização do algoritmo Dijkstra por meio do pgRouting.
- [x] Identificação dos vértices mais próximos das coordenadas informadas.
- [x] Ponderação de custos conforme as características das vias.
- [x] Consideração de restrições de circulação.
- [x] Consideração de sentidos permitidos para bicicletas e pedestres.
- [x] Geração de rotas em formato GeoJSON.
- [x] API REST para gerenciamento de ciclovias.
- [x] API REST para gerenciamento de calçadas.
- [x] API REST para gerenciamento de travessias.
- [x] API REST para gerenciamento de recursos de acessibilidade.

### Em desenvolvimento

- [ ] Desenvolvimento e integração do frontend.
- [ ] Implementação de autenticação e gerenciamento de usuários.
- [ ] Implementação de registros de relatos sobre problemas urbanos.
- [ ] Histórico de rotas.
- [ ] Funcionalidades adicionais de acessibilidade.

---

## 🛠️ Tecnologias utilizadas

### Backend

| Tecnologia | Utilização |
|---|---|
| Python | Linguagem de programação |
| Django 6.1 | Framework do backend |
| Django REST Framework 3.18 | Desenvolvimento da API REST |
| PostgreSQL 18 | Banco de dados relacional |
| PostGIS 3.6 | Armazenamento e processamento de dados geográficos |
| pgRouting 4.0 | Algoritmos de roteamento geográfico |
| GeoDjango | Integração de recursos geoespaciais com Django |
| NetworkX 3.7 | Biblioteca de análise de grafos |
| PyOsmium 4.3 | Processamento de dados do OpenStreetMap |

### Dados geográficos

- OpenStreetMap (OSM).
- GeoJSON.
- Arquivos OSM/PBF.

---

## 🏗️ Arquitetura do projeto

O backend está organizado em aplicações Django, cada uma com responsabilidades específicas.

```text
rota-esverdeada/
│
├── backend/
│   │
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   ├── rotas/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests.py
│   │
│   ├── infraestrutura/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests.py
│   │
│   ├── usuarios/
│   │
│   ├── relatos/
│   │
│   ├── manage.py
│   └── arquivos geográficos
│
└── README.md
```

### Responsabilidade das aplicações

| Aplicação | Responsabilidade |
|---|---|
| `config` | Configurações gerais do Django e definição das URLs principais. |
| `rotas` | Cálculo de caminhos, identificação de vértices e lógica de roteamento. |
| `infraestrutura` | Gerenciamento dos elementos de infraestrutura urbana. |
| `usuarios` | Estrutura inicial para funcionalidades relacionadas aos usuários. |
| `relatos` | Estrutura inicial para futuros registros de problemas urbanos. |

As aplicações `usuarios` e `relatos` ainda não possuem modelos implementados.

---

## 🗺️ Banco de dados e geoprocessamento

O projeto utiliza PostgreSQL com PostGIS e pgRouting para armazenar e processar informações geográficas.

O banco possui dois schemas principais:

### Schema `public`

Armazena os dados relacionados às entidades da aplicação.

| Tabela | Descrição |
|---|---|
| `infraestrutura_ciclovia` | Informações sobre ciclovias e ciclofaixas. |
| `infraestrutura_calcada` | Informações sobre calçadas. |
| `infraestrutura_travessia` | Informações sobre travessias. |
| `infraestrutura_recursoacessibilidade` | Recursos de acessibilidade. |
| `rotas_pontoiluminacao` | Pontos de iluminação pública. |

### Schema `roteamento`

Armazena a estrutura geográfica utilizada pelo mecanismo de cálculo de rotas.

| Tabela | Descrição |
|---|---|
| `osm_nodes` | Nós provenientes do OpenStreetMap. |
| `osm_ways` | Vias e respectivas tags do OpenStreetMap. |
| `osm_relations` | Relações do OpenStreetMap. |
| `rv_ways` | Arestas da rede de roteamento. |
| `rv_ways_vertices_pgr` | Vértices utilizados pelo pgRouting. |
| `rv_pointsofinterest` | Pontos de interesse. |
| `configuration` | Configurações da estrutura geográfica. |

### Sistema de referência espacial

As geometrias utilizadas pela API de infraestrutura trabalham com o sistema de referência espacial **SRID 4326**.

Esse sistema permite representar coordenadas geográficas de latitude e longitude.

---

## 🧠 Algoritmo de cálculo de rotas

O principal mecanismo do Rota Verde utiliza o algoritmo **Dijkstra**, disponibilizado pelo pgRouting.

O algoritmo trabalha sobre uma rede viária representada como um grafo, composto por vértices e arestas.

Diferentemente de um roteamento que considera apenas a menor distância, o Rota Verde utiliza custos ponderados para avaliar as características das vias.

### 1. Identificação dos pontos

A aplicação recebe as coordenadas geográficas de origem e destino.

Em seguida, identifica os vértices mais próximos na rede viária, utilizando consultas espaciais do PostGIS.

### 2. Construção dos custos

Os custos das arestas são calculados dinamicamente de acordo com o perfil selecionado.

O custo-base considera o comprimento da via multiplicado por fatores de ponderação.

**Perfil ciclista 🚴**

São considerados:

- Tipo de via.
- Presença de ciclovias e ciclofaixas.
- Tipo de superfície.
- Condição de conservação da via.
- Permissões específicas para bicicletas.
- Sentido de circulação, considerando `oneway:bicycle` e, quando ausente, `oneway`.

**Perfil pedestre 🚶**

São considerados:

- Tipo de via.
- Presença de calçadas.
- Tipo de superfície.
- Condição de conservação da via.
- Permissões específicas para pedestres.
- Sentido de circulação conforme `oneway:foot`.

### 3. Restrições de circulação

O algoritmo identifica restrições presentes nas tags do OpenStreetMap.

Quando uma direção não é permitida, seu custo recebe o valor `-1`, indicando ao pgRouting que aquela direção não deve ser utilizada.

O sistema também considera situações de contrafluxo conforme as regras específicas de cada perfil.

### 4. Execução do Dijkstra

Após a construção dos custos, a aplicação executa o algoritmo:

```sql
pgr_dijkstra(
    edges_sql,
    origem,
    destino,
    directed := true
)
```

O parâmetro `directed := true` permite considerar os custos de deslocamento em cada direção.

### 5. Geração da rota

Após encontrar o caminho, o backend:

1. Recupera os segmentos utilizados.
2. Organiza os segmentos conforme a sequência do percurso.
3. Ajusta a orientação das geometrias.
4. Constrói uma geometria única utilizando `ST_MakeLine`.
5. Calcula a distância total.
6. Retorna o resultado em GeoJSON.

**Observação:** os pesos utilizados representam critérios de preferência definidos no algoritmo. Eles não constituem uma garantia absoluta de segurança ou acessibilidade dos trajetos.

---

## 🔌 API REST

O backend disponibiliza endpoints para cálculo de rotas e gerenciamento da infraestrutura urbana.

### Cálculo de rotas

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/api/rotas/calcular/` | Calcula uma rota entre dois pontos. |

#### Exemplo de requisição

```http
POST /api/rotas/calcular/
Content-Type: application/json
```

```json
{
    "origem_latitude": -1.4732767,
    "origem_longitude": -48.4533129,
    "destino_latitude": -1.4727514,
    "destino_longitude": -48.455965,
    "perfil": "ciclista"
}
```

O campo `perfil` aceita dois valores:

- `ciclista`
- `pedestre`

Caso não seja informado, o sistema utiliza `ciclista` como padrão.

#### Exemplo de resposta

A resposta utiliza o formato GeoJSON `Feature`.

```json
{
    "type": "Feature",
    "geometry": {
        "type": "LineString",
        "coordinates": [
            [-48.4533129, -1.4732767],
            [-48.4536126, -1.4732913]
        ]
    },
    "properties": {
        "perfil": "ciclista",
        "vertice_origem": 17416,
        "vertice_destino": 21147,
        "distancia_ate_origem_m": 5.46,
        "distancia_ate_destino_m": 5.46,
        "quantidade_segmentos": 5,
        "custo_total": 10.5,
        "distancia_m": 120.50,
        "distancia_km": 0.121
    }
}
```

*Os valores numéricos e as coordenadas deste exemplo são ilustrativos.*

#### Propriedades retornadas

| Campo | Descrição |
|---|---|
| `perfil` | Perfil utilizado no cálculo. |
| `vertice_origem` | Identificador do vértice inicial. |
| `vertice_destino` | Identificador do vértice final. |
| `distancia_ate_origem_m` | Distância entre a coordenada inicial e o vértice encontrado. |
| `distancia_ate_destino_m` | Distância entre a coordenada final e o vértice encontrado. |
| `quantidade_segmentos` | Quantidade de segmentos utilizados. |
| `custo_total` | Custo acumulado do caminho. |
| `distancia_m` | Distância total em metros. |
| `distancia_km` | Distância total em quilômetros. |

### Infraestrutura urbana

Os endpoints de infraestrutura utilizam `ModelViewSet` e o `DefaultRouter` do Django REST Framework.

| Recurso | Endpoint |
|---|---|
| Ciclovias | `/api/ciclovias/` |
| Calçadas | `/api/calcadas/` |
| Travessias | `/api/travessias/` |
| Recursos de acessibilidade | `/api/recursos-acessibilidade/` |

Esses endpoints disponibilizam as operações REST convencionais:

- `GET`: listar ou consultar registros.
- `POST`: cadastrar registros.
- `PUT`: atualizar registros.
- `PATCH`: atualizar parcialmente.
- `DELETE`: excluir registros.

O acesso às operações depende das configurações de permissões da aplicação.

### Geometrias GeoJSON

Os endpoints de infraestrutura recebem e retornam geometrias no formato GeoJSON.

Tipos geométricos esperados:

| Recurso | Tipo |
|---|---|
| Ciclovias | `LineString` |
| Calçadas | `LineString` |
| Travessias | `LineString` |
| Recursos de acessibilidade | `Point` |

O backend valida o tipo de geometria e o SRID antes de armazenar os dados.

### Códigos de resposta do cálculo de rotas

| Código HTTP | Descrição |
|---|---|
| 200 | Rota calculada com sucesso. |
| 400 | Dados inválidos, perfil não reconhecido ou origem e destino no mesmo vértice. |
| 404 | Vértices não encontrados ou inexistência de rota entre os pontos. |

---

## 💻 Instalação e execução

### Pré-requisitos

Antes de executar o backend, é necessário possuir:

- Python 3.12 ou superior.
- PostgreSQL 18.
- PostGIS 3.6.
- pgRouting 4.0.
- Git.

Também é necessário possuir um banco de dados PostgreSQL configurado com as extensões geoespaciais e as tabelas da rede de roteamento utilizadas pelo projeto.

### 1. Clonar o repositório

```bash
git clone URL_DO_REPOSITORIO
```

Entre na pasta do projeto:

```bash
cd rota-esverdeada/backend
```

### 2. Criar o ambiente virtual

```bash
python -m venv .venv
```

Ative o ambiente virtual:

```bash
source .venv/bin/activate
```

### 3. Instalar as dependências

```bash
pip install Django==6.1.1
pip install djangorestframework==3.18.1
pip install psycopg==3.3.6
pip install networkx==3.7
pip install osmium==4.3.2
```

### 4. Configurar o banco de dados

Crie o banco PostgreSQL e configure a conexão no arquivo:

```text
config/settings.py
```

O backend utiliza:

| Parâmetro | Valor de referência |
|---|---|
| Banco | `rota_verde` |
| Usuário | `rota_verde_user` |
| Host | `localhost` |
| Porta | `5432` |
| Engine | `django.contrib.gis.db.backends.postgis` |

As credenciais devem ser configuradas localmente, sem serem compartilhadas no repositório.

O banco também precisa conter a estrutura de roteamento no schema `roteamento`, incluindo as tabelas `rv_ways` e `rv_ways_vertices_pgr`.

### 5. Executar as migrações

```bash
python manage.py migrate
```

### 6. Criar um superusuário

```bash
python manage.py createsuperuser
```

### 7. Iniciar o servidor

```bash
python manage.py runserver
```

O backend estará disponível localmente em:

```text
http://127.0.0.1:8000/
```

A interface administrativa poderá ser acessada em:

```text
http://127.0.0.1:8000/admin/
```

---

## 📱 Frontend

O frontend do Rota Verde encontra-se em desenvolvimento.

Esta seção será ampliada conforme a implementação da interface e sua integração com a API forem avançando.

O objetivo é oferecer uma experiência intuitiva para que ciclistas e pedestres possam informar seus destinos, selecionar seus perfis de deslocamento e visualizar as rotas calculadas pelo backend.

---

## 🗺️ Dados geográficos

O projeto utiliza dados do OpenStreetMap para representar a infraestrutura e a rede viária.

Entre os arquivos geográficos utilizados durante o desenvolvimento estão:

- Rede viária de Belém.
- Dados de calçadas.
- Dados de travessias.
- Recursos de acessibilidade.
- Limites geográficos de Belém.
- Extratos regionais da região Norte.

Os dados são utilizados na construção e no desenvolvimento da estrutura geográfica do sistema.

A documentação sobre o processo de extração, importação e atualização dessas bases será complementada posteriormente.

---

## 🔮 Próximos passos

- Desenvolvimento do frontend.
- Troca de ambiente do servidor e do backend para a nuvem.
- Integração completa entre frontend e backend.
- Implementação de autenticação e gerenciamento de usuários.
- Implementação de histórico de rotas.
- Expansão das informações de acessibilidade.
- Aprimoramento dos critérios de ponderação.
- Ampliação da cobertura geográfica.

---

## 👥 Projeto acadêmico

O Rota Verde é um projeto acadêmico desenvolvido com foco em mobilidade urbana sustentável, geoprocessamento e desenvolvimento de software.

O projeto busca demonstrar como tecnologias de dados geográficos e algoritmos de grafos podem contribuir para melhorar a experiência de deslocamento de ciclistas e pedestres nas cidades.

---
Grupo do projeto
Gustavo Brioso - 04182372
David Moraes - 04188750
Arthur Vieira - 04183624

**Rota Verde — Caminhos melhores para uma cidade melhor.** 🌱
