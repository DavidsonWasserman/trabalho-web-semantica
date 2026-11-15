# Decisões de Modelagem, Estratégia LOD e Declaração de IA

## 1. Desenho de URIs e Publicação no GitHub Pages
Como o GitHub Pages é um servidor estático que não realiza negociação de conteúdo HTTP 303 (*Content Negotiation*) dinamicamente por recurso individual, adotou-se o padrão de **Hash URIs** ancoradas nos documentos publicados no repositório:

- **Ontologia OWL (`acad:`):**
  `https://davidsonwasserman.github.io/trabalho-web-semantica/ontologia/ontologia.owl#<Termo>`
- **Taxonomia SKOS (`pes:`):**
  `https://davidsonwasserman.github.io/trabalho-web-semantica/ontologia/taxonomia_pessoas.ttl#<Conceito>`
- **Instâncias / Recursos (`recurso:`):**
  `https://davidsonwasserman.github.io/trabalho-web-semantica/ontologia/dados.ttl#<Individuo>`

**Justificativa:**
1. Ao requisitar a URI de qualquer classe, propriedade ou indivíduo em um cliente HTTP/RDF, a parte anterior ao `#` resolve diretamente para o arquivo Turtle/OWL completo com status `200 OK`.
2. Cada página HTML em `exemplos/perfis/*.html` declara `<link rel="alternate" type="text/turtle" href="../../ontologia/dados.ttl">` e traz embutido um bloco `<script type="application/ld+json">` contendo o `@id` exato do recurso no grafo RDF, garantindo correspondência inequívoca entre representação humana (HTML) e representação legível por máquina (RDF / JSON-LD).

---

## 2. Decisões Críticas de Modelagem Ontológica

### 2.1. Reificação de Entidades (`AreaConhecimento`, `FormacaoAcademica`, `Publicacao`, `RedeAcademica`)
Em um primeiro rascunho ingênuo, campos como "áreas de pesquisa", "formação" ou "publicações" poderiam ser armazenados como meros literais (`xsd:string`). Entretanto:
- **Áreas como recursos (`acad:AreaConhecimento`):** ao modelar cada área como indivíduo (`recurso:AreaWebSemantica`, `recurso:AreaDadosAbertos`), é possível associar rótulos controlados (`skos:prefLabel`) e ligar cada área às suas equivalentes externas na Wikidata e DBpedia (`skos:exactMatch`), permitindo que a consulta SPARQL #3 navegue do docente para a base externa.
- **Publicações como indivíduos (`acad:Publicacao`):** permite ligar múltiplos autores (`acad:temAutor`) à mesma obra, possibilitando a identificação automática de **coautores** na consulta SPARQL #5 sem duplicar dados.
- **Formações Acadêmicas (`acad:FormacaoAcademica`):** preserva grau, curso, instituição e ano de conclusão como propriedades estruturadas.

### 2.2. Não-Disjunção entre `acad:Docente` e `acad:Discente`
Embora sejam classes distintas sob `acad:Pessoa`, optou-se deliberadamente por **não** declarar `acad:Docente owl:disjointWith acad:Discente`. No ambiente universitário real, um professor pode estar formalmente matriculado em programa de doutorado ou pós-doutorado, acumulando ambos os vínculos simultaneamente. As disjunções foram aplicadas entre grandes categorias conceituais incompatíveis (`Pessoa`, `OrganizacaoAcademica`, `Curso`, `AreaConhecimento`, `Disciplina`, `ProjetoPesquisa`, `Publicacao`, `FormacaoAcademica`, `RedeAcademica`).

### 2.3. Compatibilidade com Raciocinador HermiT (OWL 2 DL) e SPARQL sem Reasoner
- **Tipos de dados seguros para HermiT:** conforme boas práticas verificadas na disciplina, evitou-se `xsd:gYear` e `xsd:date` dentro de expressões `owl:onDataRange` em restrições OWL, utilizando `xsd:integer` para anos (`anoPublicacao`, `anoIngresso`, `anoConclusao`) e `xsd:string` / `xsd:anyURI` para os demais campos.
- **Materialização explícita de supertipos em `dados.ttl`:** cada docente é tipado com `acad:Docente, acad:Pessoa` e cada discente com `acad:DiscenteGraduacao, acad:Discente, acad:Pessoa`. Isso garante que motores SPARQL sem raciocinador RDFS/OWL acoplado (como uma execução padrão em `rdflib`) respondam corretamente tanto a `?x a acad:Discente` quanto a `?x a acad:Pessoa`.

### 2.4. Fonte Única de Verdade (`dados_perfis.json` + `build.py`)
Para eliminar divergências entre as páginas HTML exibidas no navegador e os arquivos RDF consultados via SPARQL, o JSON estruturado funciona como fonte única de entrada para o gerador Python (`codigo-fonte/build.py`), garantindo sincronia total entre HTML, JSON-LD e Turtle.

---

## 3. Política de Ligações Externas (LOD) e Uso Criterioso de `owl:sameAs`
O trabalho evita o antipadrão comum de usar `owl:sameAs` como sinônimo genérico de relacionamento. Cada propriedade externa foi escolhida pela sua semântica exata:

| Recurso Interno | Recurso Externo | Propriedade Semântica Utilizada | Justificativa |
| :--- | :--- | :--- | :--- |
| `recurso:UFRRJ` | Wikidata `Q7894375` e DBpedia `Federal_Rural_University_of_Rio_de_Janeiro` | `owl:sameAs` | **Identidade estrita:** tratam exatamente da mesma instituição real no mundo (a Universidade Federal Rural do Rio de Janeiro). |
| `recurso:AreaWebSemantica`, `recurso:AreaDadosAbertos`, `recurso:AreaInteligenciaArtificial`, etc. | Wikidata (`Q54837`, `Q309901`, `Q11660`, ...) e DBpedia (`Semantic_Web`, `Open_data`, ...) | `skos:exactMatch` | Trata-se de equivalência conceitual entre termos de tesauros/conceitos de áreas do conhecimento, não de identidade ontológica entre instâncias físicas. |
| `recurso:CursoSistemasInformacao`, `recurso:CursoCienciaComputacao` | Wikidata (`Q16387`, `Q21198`) | `skos:closeMatch` | Os currículos brasileiros (ex.: Bacharelado em Sistemas de Informação da UFRRJ) possuem alta proximidade conceitual, mas não equivalência exata com a definição genérica internacional do curso. |
| Perfis (`DocenteAnaSilva`, etc.) | ORCID, Currículo Lattes | `rdfs:seeAlso` + `acad:orcid` / `acad:lattes` | Como os perfis são demonstrativos/fictícios (e uma página de perfil é uma descrição documental da pessoa), usa-se `rdfs:seeAlso` em RDF em vez de afirmar identidade absoluta via `owl:sameAs` com registros reais. |
| `recurso:PubDadosConectados2024` | OpenAlex / DOI | `bibo:doi` + `rdfs:seeAlso` | Aponta para metadados bibliográficos externos relacionados sem fundir registros fictícios e reais. |

---

## 4. Proveniência e Licença
- **Licença:** Creative Commons Atribuição 4.0 Internacional (`https://creativecommons.org/licenses/by/4.0/`), declarada em `ontologia.owl`, `taxonomia_pessoas.ttl`, `dados.ttl` e no rodapé das páginas.
- **Fonte dos Dados:** baseados nos templates demonstrativos da disciplina (`paginaTrabalho/docente.html`, `discente.html`) com dados fictícios complementares criados exclusivamente para o projeto, sem exposição de dados sensíveis de terceiros.

---

## 5. Declaração de Uso de Ferramentas de Inteligência Artificial (Seção 9)

Em conformidade com a Seção 9 da especificação do trabalho, registramos de forma transparente o uso de ferramentas de IA como apoio ao desenvolvimento:

- **Ferramentas utilizadas:** Assistente de IA em ambiente de desenvolvimento (Antigravity / modelos Gemini), como apoio à arquitetura do código, revisão de sintaxe Turtle/OWL 2, geração do script automatizado em Python e redação inicial de documentação.
- **Finalidades:**
  1. Estruturar o script gerador `codigo-fonte/build.py` para manter sincronizados HTML, JSON-LD e `dados.ttl`;
  2. Revisar axiomas OWL 2 e restrições de compatibilidade com o raciocinador HermiT (substituindo tipos não suportados como `xsd:gYear` por `xsd:integer`);
  3. Auxiliar na formulação e teste das 6 consultas SPARQL (incluindo o uso de Property Paths na Consulta 06);
  4. Organizar as tabelas de documentação e verificar consistência entre dicionário de dados, ontologia e consultas.
- **Síntese dos prompts relevantes utilizados:**
  - *"Analisar a especificação do trabalho em PDF e os modelos HTML/CSS do professor, propondo uma divisão de escopo e uma arquitetura unificada onde uma fonte JSON gere as páginas HTML e o grafo RDF/Turtle."*
  - *"Definir uma ontologia de aplicação em OWL 2 (Turtle) compatível com Protégé/HermiT alinhada a FOAF, Schema.org, BIBO, DC Terms e integrada à taxonomia facetada SKOS já desenvolvida na disciplina."*
  - *"Escrever as 6 consultas SPARQL correspondentes às perguntas de competência, utilizando Property Paths na consulta de unidade acadêmica e evitando uso genérico de `owl:sameAs`."*
- **Partes geradas ou modificadas com auxílio de IA:** esqueleto do pipeline `codigo-fonte/build.py`, rascunho de `ontologia/ontologia.owl`, consultas `.rq`, diagramas Mermaid/SVG e templates de documentação em Markdown.
- **Como os resultados foram verificados e validados pela dupla:**
  1. **Validação sintática automática:** todos os arquivos `.owl`, `.ttl` e blocos `application/ld+json` foram validados pelo parser oficial da biblioteca Python `rdflib` (v7.6.0) com zero erros de sintaxe (totalizando 1.013 triplas no grafo unificado);
  2. **Execução real das 6 queries SPARQL:** todas as consultas em `consultas/consulta01.rq`..`consulta06.rq` foram executadas via `rdflib` e tiveram seus resultados conferidos linha a linha contra os dados de `codigo-fonte/dados_perfis.json`;
  3. **Revisão crítica humana:** os integrantes revisaram todas as decisões semânticas (especialmente os relacionamentos LOD `owl:sameAs` vs `skos:exactMatch`, não-disjunção entre Docente e Discente, e a aderência visual ao CSS fornecido pelo professor), garantindo o domínio individual das escolhas de modelagem, dos dados RDF e das consultas SPARQL para a apresentação.
