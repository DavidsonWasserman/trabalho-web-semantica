# Especificação de Requisitos e Perguntas de Competência

## 1. Requisitos da Aplicação Web
- **RA-01 (Apresentação Web):** Exibir perfis de docentes e discentes em páginas HTML responsivas acessíveis via navegador, partindo dos modelos fornecidos pelo professor (`paginaTrabalho/docente.html`, `discente.html`, `estilos.css`).
- **RA-02 (Quantidade Mínima de Perfis):** Disponibilizar pelo menos 2 perfis de docentes e 2 perfis de discentes utilizando dados fictícios/demonstrativos, sem expor dados pessoais sensíveis de terceiros.
- **RA-03 (Geração a partir de Fonte Estruturada):** Gerar as páginas HTML automaticamente a partir de fonte de dados estruturada (`codigo-fonte/dados_perfis.json` via `codigo-fonte/build.py`), evitando páginas HTML manuais desconectadas dos dados do projeto.
- **RA-04 (Conteúdo dos Perfis):** Contemplar nome, vínculo institucional, unidade/departamento ou curso, formação, áreas de atuação/interesse, disciplinas (para docentes), projetos, grupos de pesquisa, publicações/trabalhos e links de redes/perfis acadêmicos.
- **RA-05 (Publicação Pública):** Disponibilizar o site, a ontologia, os dados RDF e a documentação em repositório público no GitHub e via GitHub Pages.

---

## 2. Requisitos de Web Semântica e Linked Open Data (LOD)
- **RS-01 (Modelo Conceitual e Dicionário de Dados):** Documentar entidades, atributos, relacionamentos, tipos XSD, cardinalidades e regras de domínio.
- **RS-02 (Pesquisa e Reuso de Vocabulários):** Avaliar ontologias/vocabulários existentes (`FOAF`, `Schema.org`, `BIBO`, `VIVO`, `DC Terms`, `SKOS`) e justificar reuso, alinhamento e extensões da ontologia de aplicação.
- **RS-03 (Ontologia de Aplicação em OWL 2):** Definir formalmente classes, propriedades de objeto (incluindo inversas e funcionais), propriedades de dados, domínios, alcances, classes definidas (`owl:equivalentClass`) e restrições/disjunções em `ontologia/ontologia.owl` (Turtle).
- **RS-04 (Vocabulário Controlado SKOS):** Integrar taxonomia facetada (`ontologia/taxonomia_pessoas.ttl`) para padronização de vínculos, atuações e condições acadêmicas.
- **RS-05 (URIs Públicas e Dados RDF Acessíveis):** Atribuir URIs HTTP estáveis no domínio do GitHub Pages a todos os indivíduos em `ontologia/dados.ttl`, vinculando o RDF às páginas HTML via `<link rel="alternate" type="text/turtle">` e JSON-LD embutido.
- **RS-06 (Ligações Externas LOD):** Relacionar os dados a pelo menos 3 fontes externas relevantes (Wikidata, DBpedia, ORCID/Lattes/OpenAlex) justificando as propriedades semânticas empregadas e evitando o uso indiscriminado de `owl:sameAs`.
- **RS-07 (Proveniência e Licenciamento):** Declarar fonte dos dados (`dcterms:source`), data de atualização (`dcterms:modified`) e licença de reutilização (`dcterms:license`, CC BY 4.0).

---

## 3. Perguntas de Competência Obrigatórias (SPARQL)
O modelo ontológico e o grafo RDF devem responder com precisão às 6 consultas armazenadas em `consultas/consulta01.rq` a `consultas/consulta06.rq`:

1. **PC-01:** *Quais são os docentes cadastrados e seus respectivos departamentos ou unidades acadêmicas?*
2. **PC-02:** *Quais discentes pertencem a determinado curso?*
3. **PC-03:** *Quais docentes atuam em determinada área de pesquisa?*
4. **PC-04:** *Quais docentes e discentes participam de um mesmo projeto de pesquisa?* *(explora múltiplos tipos de entidades)*
5. **PC-05:** *Quais publicações estão associadas a determinado docente e quem são seus coautores, quando essa informação estiver representada?* *(explora múltiplos tipos de entidades e relação de coautoria)*
6. **PC-06:** *Quais pessoas estão vinculadas a uma unidade acadêmica específica, independentemente de serem docentes ou discentes?* *(explora superclasse e Property Paths entre entidades organizacionais)*
