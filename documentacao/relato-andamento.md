# Relato de Andamento do Projeto — Checkpoint de 25/11/2026

- **Disciplina:** Web Semântica e Linked Open Data — DCC/ICEx — UFRRJ
- **Professor:** Tiago Cruz de França
- **Projeto:** Portal Semântico de Perfis Acadêmicos e Linked Open Data (UFRRJ)
- **Integrantes:** Davidson Wasserman · Nicolas Duarte — Sistemas de Informação (UFRRJ)
- **Entrega final:** 01/12/2026

---

## 1. Acesso aos repositórios (parte técnica)

| O quê | Endereço |
| :--- | :--- |
| Repositório no GitHub (público) | https://github.com/DavidsonWasserman/trabalho-web-semantica |
| Site publicado (GitHub Pages) | https://davidsonwasserman.github.io/trabalho-web-semantica/ |
| Ontologia OWL 2 (RDF/XML) | https://davidsonwasserman.github.io/trabalho-web-semantica/ontologia/ontologia.owl |
| Ontologia OWL 2 (Turtle) | https://davidsonwasserman.github.io/trabalho-web-semantica/ontologia/ontologia.ttl |
| Taxonomia SKOS | https://davidsonwasserman.github.io/trabalho-web-semantica/ontologia/taxonomia_pessoas.ttl |
| Dados RDF (instâncias) | https://davidsonwasserman.github.io/trabalho-web-semantica/ontologia/dados.ttl |
| Consultas SPARQL e resultados | https://github.com/DavidsonWasserman/trabalho-web-semantica/blob/main/consultas/resultados/resultados_sparql.md |

O repositório e o portal web são públicos e não exigem convite de acesso.

---

## 2. Resumo do andamento

A primeira versão funcional (**v0.1**) cobre o fluxo completo pedido no enunciado: proposta → dicionário de dados → pesquisa de vocabulários → ontologia OWL 2 → dados RDF → consultas SPARQL → site publicado com perfis e JSON-LD. **Todos os entregáveis da Seção 7 já têm uma versão no repositório.** O trabalho até 01/12 é de revisão, validação no Protégé, ajustes conforme o retorno do professor e preparação da apresentação.

**Números da versão atual**

| Item | Quantidade |
| :--- | ---: |
| Classes OWL | 19 |
| Propriedades de objeto | 27 |
| Propriedades de dados | 28 |
| Restrições OWL (`owl:Restriction`) | 8 |
| Conceitos SKOS (taxonomia facetada) | 21 |
| Perfis publicados | 4 (2 docentes + 2 discentes) |
| Triplas no grafo unificado (ontologia + SKOS + dados) | 1.013 |
| Consultas SPARQL (perguntas de competência) | 6 |

---

## 3. Situação por entregável (Seção 7 do enunciado)

| Entregável | Situação | Onde está |
| :--- | :---: | :--- |
| Proposta: objetivo, público-alvo, funcionalidades, perfis, justificativa | Pronto (v0.1) | `proposta/descricao.md`, `proposta/requisitos.md` |
| Código-fonte e site público com ≥ 2 docentes e ≥ 2 discentes | Pronto (v0.1) | `codigo-fonte/`, `index.html`, `exemplos/perfis/` |
| Dicionário de dados e documentação de metadados/vocabulários | Pronto (v0.1) | `documentacao/dicionario-dados.md` |
| Pesquisa de ontologias/vocabulários e justificativa | Pronto (v0.1) | `documentacao/vocabularios.md` |
| Documentação da ontologia (diagrama, classes, propriedades, axiomas) | Pronto (v0.1) | `documentacao/ontologia.md`, `documentacao/diagrama.svg` |
| Arquivos OWL e RDF/Turtle | Pronto (v0.1) | `ontologia/` |
| Seis consultas SPARQL, resultados e explicações | Pronto (v0.1) | `consultas/consulta01.rq` … `consulta06.rq`, `consultas/resultados/` |
| Evidências de publicação: URIs, links externos, licença, fontes | Pronto (v0.1) | `proposta/decisoes-modelagem.md` (Seções 1, 3 e 4) |
| README com integrantes, endereços, estrutura e reprodução | Pronto (v0.1) | `README.md` |
| Declaração de uso de IA | Pronto (v0.1), será revisada na entrega final | `proposta/decisoes-modelagem.md` (Seção 5) |

---

## 4. Arquitetura e principais decisões técnicas

1. **Uma única fonte de dados.** Os perfis ficam em `codigo-fonte/dados_perfis.json`. O script `codigo-fonte/build.py` (Python + `rdflib`) gera a partir dele o `dados.ttl`, as páginas HTML dos perfis com **JSON-LD embutido** e `<link rel="alternate" type="text/turtle">`, e o índice do site. Assim o RDF e o que aparece nas páginas não ficam diferentes.
2. **Ontologia de aplicação própria (`acad:`) alinhada a vocabulários existentes:** FOAF, Schema.org, BIBO e DC Terms (via `rdfs:subClassOf` / `rdfs:subPropertyOf`). A escolha está justificada em `documentacao/vocabularios.md`.
3. **Reaproveitamento da taxonomia SKOS** feita no projeto prático da disciplina (`pes:`), ligada às pessoas por `acad:possuiClassificacaoSKOS`, para classificar papéis e situações que não cabem bem na hierarquia OWL.
4. **Axiomas e inferência:** classes definidas por `owl:equivalentClass` (ex.: `AutorAcademico`, `PesquisadorEmProjeto`), propriedades inversas e funcionais, e disjunção entre as classes de nível superior. `Docente` e `Discente` **não** foram declarados disjuntos, porque um docente pode estar matriculado em uma pós-graduação.
5. **Compatibilidade com o HermiT:** anos são `xsd:integer` em vez de `xsd:gYear`, porque `xsd:gYear` não faz parte do mapa de tipos do OWL 2 que o HermiT aceita.
6. **URIs e publicação:** o GitHub Pages não faz negociação de conteúdo. Por isso usamos *hash URIs* (`…/dados.ttl#Recurso`). A ontologia é publicada em dois formatos: `ontologia.ttl` (Turtle) e `ontologia.owl` (RDF/XML, gerado pelo build para ser servido corretamente como `application/rdf+xml`).
7. **Ligações LOD:** `owl:sameAs` foi usado só para identidade comprovada (UFRRJ → Wikidata `Q7834196` e DBpedia). Relações mais fracas usam propriedades mais adequadas, como explicado em `proposta/decisoes-modelagem.md`, Seção 3.
8. **Licença:** dados e documentação sob CC BY 4.0. Todos os perfis são **fictícios**, conforme a Seção 12 do enunciado.

---

## 5. Como verificar a parte técnica

1. **Site e perfis:** abrir o endereço do GitHub Pages e um dos perfis. No código-fonte da página (Ctrl+U) aparece o bloco `application/ld+json`.
2. **Ontologia:** abrir `ontologia/ontologia.owl` no Protégé (pela URL pública ou pelo arquivo) e rodar o HermiT para ver as classes inferidas.
3. **Dados e consultas:** reproduzir localmente:
   ```bash
   git clone https://github.com/DavidsonWasserman/trabalho-web-semantica.git
   cd trabalho-web-semantica
   python3 -m venv .venv && source .venv/bin/activate && pip install rdflib
   python3 codigo-fonte/build.py
   ```
   O script valida a sintaxe de todos os arquivos RDF e dos blocos JSON-LD, roda as 6 consultas sobre o grafo unificado e atualiza `consultas/resultados/resultados_sparql.md`.

**Resultados atuais das perguntas de competência**

| Consulta | Pergunta de competência | Linhas |
| :---: | :--- | ---: |
| PC-01 | Docentes e seus departamentos/unidades | 2 |
| PC-02 | Discentes de um determinado curso | 1 |
| PC-03 | Docentes que atuam em uma área de pesquisa | 4 |
| PC-04 | Docentes e discentes que participam de um mesmo projeto | 5 |
| PC-05 | Publicações de um docente e seus coautores | 6 |
| PC-06 | Pessoas vinculadas a uma unidade acadêmica (com *property path*) | 4 |

---

## 6. Dificuldades encontradas e como foram resolvidas

| Dificuldade | Solução adotada |
| :--- | :--- |
| `xsd:gYear` não é aceito nas restrições pelo HermiT | Anos modelados como `xsd:integer` |
| O navegador mostrava erro de XML ao abrir o `.owl` publicado (Turtle sendo servido como RDF/XML) | `ontologia.ttl` mantido como fonte em Turtle e `ontologia.owl` serializado em RDF/XML pelo build |
| Manter HTML, JSON-LD e RDF sincronizados à mão | Uma fonte JSON e um script gerador e validador |
| Na revisão dos links externos, dois identificadores do Wikidata apontavam para entidades erradas (UFRRJ e "Engenharia do Conhecimento") | Corrigidos para `Q7834196` e `Q1540472`, conferidos com os `owl:sameAs` publicados pela DBpedia. Todos os links externos foram revisados de novo |
| GitHub Pages não oferece endpoint SPARQL | Arquivos RDF publicados e consultas reproduzíveis via `rdflib` (alternativa prevista na Seção 6 do enunciado) |

---

## 7. Próximos passos até 01/12

| Atividade | Responsável | Prazo |
| :--- | :--- | :---: |
| Aplicar os ajustes indicados pelo professor neste checkpoint | Nicolas Duarte | 28/11 |
| Validar a ontologia no Protégé + HermiT e registrar evidências (capturas de tela) | Nicolas Duarte | 28/11 |
| Exportar o diagrama também em PNG (estrutura sugerida na Seção 8) | Nicolas Duarte | 28/11 |
| Avaliar um visualizador/endpoint SPARQL no próprio site (desejável) | Nicolas Duarte | 29/11 |
| Revisar a declaração de uso de IA (Seção 9) após os ajustes finais | Nicolas Duarte | 29/11 |
| Preparação e ensaio da apresentação final (explicação do modelo e edição ao vivo) | Nicolas Duarte | 30/11 |

---

## 8. Pontos que gostaríamos de validar com o professor

1. **Gerador estático (JSON → HTML + JSON-LD + RDF):** a abordagem atende ao requisito de integração entre o site e a camada semântica?
2. **Hash URIs no GitHub Pages:** junto com `<link rel="alternate">` e o RDF publicado, isso é evidência suficiente de publicação como LOD?
3. **PC-06:** manter o *property path* no SPARQL ou modelar também uma *property chain* em OWL?
4. **Ontologia e taxonomia SKOS em arquivos separados:** essa organização é adequada?
5. **SPARQL na apresentação:** executar as consultas ao vivo via `rdflib`/Fuseki local é suficiente, ou vale a pena um endpoint/visualizador no site?
