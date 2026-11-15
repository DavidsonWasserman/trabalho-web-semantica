# Guia de Alinhamento: Reunião de 18/11 com o Professor & Resumo para a Dupla

Este guia foi criado para cumprir dois objetivos práticos:
1. **Servir de pauta objetiva** para apresentar a Versão Inicial (`v0.1`) ao professor Tiago Cruz de França no dia **18/11** e validar as decisões antes do polimento final (`01/12`).
2. **Alinhar rapidamente a dupla** sobre toda a parte teórica, decisões de modelagem, estrutura dos arquivos e como alterar/executar o projeto caso o professor solicite modificações ao vivo na apresentação.

---

## Parte 1 — Pauta para Levar ao Professor no Dia 18/11

### O que já temos pronto na v0.1 para mostrar
- Repositório público estruturado conforme a Seção 8 do edital (`https://github.com/DavidsonWasserman/trabalho-web-semantica`).
- **4 perfis completos (2 docentes + 2 discentes)** ambientados na UFRRJ (ICEx / Departamento de Computação), gerados automaticamente a partir de `codigo-fonte/dados_perfis.json` pelo script `codigo-fonte/build.py`.
- **Ontologia de aplicação OWL 2 (`ontologia/ontologia.owl`)** alinhada a FOAF, Schema.org, BIBO e DC Terms, **integrada com a Taxonomia Facetada SKOS (`ontologia/taxonomia_pessoas.ttl`)**.
- **Grafo RDF completo (`ontologia/dados.ttl`)** com **1.013 triplas no grafo unificado** e ligações externas para Wikidata, DBpedia, ORCID, Lattes e OpenAlex.
- **Todas as 6 consultas SPARQL (`consultas/consulta01.rq`..`consulta06.rq`)** já executadas e validadas com resultados não-vazios em `rdflib`.

### Perguntas Estratégicas para Validar com o Professor em 18/11
1. **Arquitetura do Site (Gerador Estático + JSON-LD + RDF):**
   > *"Professor, centralizamos os dados em `dados_perfis.json` e fizemos um script Python (`build.py`) que gera as páginas HTML estáticas (mantendo o seu CSS/layout), embute JSON-LD e gera/valida `dados.ttl` e as 6 queries SPARQL para o GitHub Pages. Essa abordagem atende plenamente ao requisito de não criar páginas HTML estáticas isoladas?"*
2. **Padrão de Hash URIs no GitHub Pages:**
   > *"Como o GitHub Pages é hospedagem estática (sem content negotiation 303), usamos Hash URIs apontando para `.../ontologia/dados.ttl#Recurso` e `<link rel="alternate" type="text/turtle">` no HTML. Isso é suficiente para comprovar a publicação LOD?"*
3. **Pergunta de Competência 6 (Unidade Acadêmica via Property Path):**
   > *"Na Consulta 6, além de modelar a propriedade `vinculadoAUnidade`, demonstramos a resolução automática por caminho de propriedades: `(acad:lotadoEm/acad:parteDeUnidade)|(acad:matriculadoEm/acad:oferecidoPorUnidade)`. O senhor prefere que mantenhamos essa abordagem com Property Path ou prefere via inferência de OWL property chain?"*
4. **Reaproveitamento da Taxonomia SKOS (`ProjetoPratico`):**
   > *"Integramos nossa taxonomia facetada SKOS (`pes:Docente`, `pes:Graduando`, `pes:Pesquisador`, `pes:Bolsista`) para classificar papéis e condições além da hierarquia OWL. Faz sentido manter os dois arquivos (`ontologia.owl` + `taxonomia_pessoas.ttl`) separados e importados no `dados.ttl`?"*
5. **Execução do SPARQL na Apresentação Final (01/12):**
   > *"Como o endpoint SPARQL público na web é opcional/desejável, podemos demonstrar as consultas ao vivo usando um servidor Apache Jena Fuseki local (ou via `rdflib` / script CLI) ou recomenda subirmos um endpoint/visualizador no próprio GitHub Pages (ex.: Comunica JS ou triplestore gratuito)?"*

---

## Parte 2 — Resumo Rápido para a Dupla (O que você precisa saber para a apresentação de 01/12)

> **Por que isso importa?** A nota da apresentação é **individual (peso de 0 a 1 multiplicando a nota do trabalho)** e o professor pode pedir para **qualquer um dos dois** explicar uma decisão teórica ou fazer uma alteração no modelo, nos dados ou em uma consulta SPARQL.

### 1. Qual é a "grande ideia" do trabalho em 30 segundos?
Páginas HTML comuns de professores/alunos são texto solto que computadores não entendem semanticamente. Nós pegamos os modelos HTML do professor e os transformamos em um **portal de Linked Open Data (LOD)**:
- O que aparece na tela para humanos (`exemplos/perfis/*.html`) também existe como **dados estruturados em grafo RDF** (`ontologia/dados.ttl`) e **JSON-LD** dentro da própria página.
- Esses dados seguem regras formais definidas na nossa **Ontologia OWL** (`ontologia/ontologia.owl`) e em um **Vocabulário Controlado SKOS** (`ontologia/taxonomia_pessoas.ttl`).
- Assim, conseguimos fazer **consultas inteligentes em SPARQL** (perguntas 1 a 6) e ligar a UFRRJ e as áreas de pesquisa ao restante da Web de Dados (**Wikidata**, **DBpedia**, **ORCID**).

### 2. Por que escolhemos esses vocabulários (e não apenas um)?
- **FOAF (`foaf:`):** padrão clássico da Web Semântica para `Person`, `Organization`, `Project`, `name`, `mbox`.
- **Schema.org (`schema:`):** padrão adotado por Google/Bing para SEO e JSON-LD (`CollegeOrUniversity`, `ScholarlyArticle`, `knowsAbout`).
- **SKOS (`skos:`):** padrão W3C para vocabulários controlados e tesauros (`prefLabel`, `altLabel`, `broader`, `narrower`, e `exactMatch` para ligar áreas à Wikidata).
- **BIBO (`bibo:`):** padrão para referências acadêmicas (`AcademicArticle`, `doi`).
- **Dublin Core (`dcterms:`):** metadados obrigatórios do dataset (licença CC BY 4.0, fonte, data de atualização).
- **Por que NÃO importamos o VIVO inteiro?** Porque a ontologia VIVO é enorme e complexa (centenas de classes BFO/IAO), o que tornaria as consultas SPARQL desnecessariamente complicadas. Criamos a ontologia de aplicação `acad:` enxuta e alinhada aos padrões acima.

### 3. Regra de Ouro que o professor cobra muito: `owl:sameAs` vs `skos:exactMatch` vs `rdfs:seeAlso`
Se o professor perguntar *"Por que vocês não usaram `owl:sameAs` em tudo?"*, a resposta exata é:
- **`owl:sameAs` afirma identidade lógica absoluta** (que duas URIs representam exatamente o mesmo objeto físico/entidade no mundo real — qualquer propriedade de A vale para B). Por isso, só usamos `owl:sameAs` na `recurso:UFRRJ` ligando à Wikidata (`Q7894375`) e DBpedia (`Federal_Rural_University_of_Rio_de_Janeiro`), porque ambas representam de fato a UFRRJ real.
- Para **áreas de pesquisa** (*Web Semântica*, *Dados Abertos*), usamos **`skos:exactMatch`**, pois são conceitos equivalentes entre esquemas de conhecimento.
- Para **cursos**, usamos **`skos:closeMatch`**, pois o currículo brasileiro tem aproximação (não identidade exata) com o verbete genérico da Wikidata.
- Para **ORCID/Lattes/OpenAlex de perfis fictícios**, usamos **`rdfs:seeAlso`** (e propriedades específicas como `acad:orcid`), evitando afirmar identidade falsa entre um perfil demonstrativo fictício e um registro real.

### 4. Como funciona o código na prática (se o professor pedir mudança ao vivo!)
Todo o projeto é gerado por **um único fluxo**:
1. Os dados estão em **`codigo-fonte/dados_perfis.json`** (nomes, áreas, projetos, publicações, coautores).
2. Ao rodar no terminal:
   ```bash
   python3 codigo-fonte/build.py
   ```
   *(ou com o `.venv` onde `rdflib` está instalado)*
3. O script automaticamente:
   - Atualiza `ontologia/dados.ttl`;
   - Atualiza `index.html` e todas as páginas em `exemplos/perfis/*.html`;
   - Valida a sintaxe de todos os arquivos OWL/TTL/JSON-LD;
   - Roda as 6 consultas `consultas/consulta01.rq` .. `consulta06.rq` e atualiza `consultas/resultados/resultados_sparql.md`.

### 5. Resumo das 6 Consultas SPARQL (para saber explicar cada uma)
1. **Consulta 01:** `Docente` $\xrightarrow{\text{lotadoEm}}$ `Departamento` $\xrightarrow{\text{parteDeUnidade}}$ `UnidadeAcademica` (ICEx).
2. **Consulta 02:** `Discente` $\xrightarrow{\text{matriculadoEm}}$ `Curso` com `FILTER` pelo nome do curso (*Sistemas de Informação*).
3. **Consulta 03:** `Docente` $\xrightarrow{\text{atuaEmArea}}$ `AreaConhecimento` (*Dados Abertos*) + `OPTIONAL { ?area skos:exactMatch ?linkExternoLOD }` trazendo Wikidata/DBpedia.
4. **Consulta 04:** Cruzamento triplo: `Docente` + `Discente` ligados ao mesmo `ProjetoPesquisa` via `acad:participaDeProjeto`.
5. **Consulta 05:** `Publicacao` ligada ao docente alvo (`Ana Exemplo da Silva`) e a um `?coautor` via `acad:temAutor`, usando `FILTER(?coautor != ?docente)` para excluir o próprio docente da lista de coautores.
6. **Consulta 06:** Uso de **Property Path** `(acad:lotadoEm/acad:parteDeUnidade)|(acad:matriculadoEm/acad:oferecidoPorUnidade)` para achar todas as `Pessoa`s (docentes e discentes juntos) do `ICEx`.
