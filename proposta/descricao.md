# Proposta do Sistema — Portal Semântico de Perfis Acadêmicos (UFRRJ)

## 1. Objetivo
Desenvolver os artefatos semânticos, a modelagem ontológica e uma aplicação web gerada a partir de dados estruturados para integrar páginas de perfis acadêmicos de **docentes** e **discentes** da **Universidade Federal Rural do Rio de Janeiro (UFRRJ)** ao ecossistema da **Web Semântica** e do **Linked Open Data (LOD)**.

Em vez de páginas HTML estáticas isoladas (silos de texto apenas legíveis por humanos), cada perfil passa a possuir representação formal em **OWL 2 / RDF (Turtle)** e **JSON-LD**, identificadores globais por **URI**, vocabulário controlado em **W3C SKOS**, ligações com fontes externas abertas (**Wikidata**, **DBpedia**, **ORCID**, **Currículo Lattes**) e capacidade de responder a consultas semânticas via **SPARQL**.

---

## 2. Público-Alvo
- **Comunidade Acadêmica (Docentes e Discentes):** descoberta de orientadores, linhas de pesquisa, projetos em andamento e redes de coautoria dentro do Instituto de Ciências Exatas (ICEx/UFRRJ).
- **Gestores e Órgãos Institucionais:** consolidação uniforme de vínculos acadêmicos, disciplinas ministradas, cursos e participação em grupos de pesquisa sem ambiguidade terminológica.
- **Agentes de Software, Buscadores e Pesquisadores Externos:** consumo automatizado por motores de busca (*Rich Snippets* via Schema.org/JSON-LD), coletores RDF e aplicações de dados abertos interligados.

---

## 3. Funcionalidades Principais
1. **Diretório Web e Páginas Individuais de Perfis:** exibição de 4 perfis iniciais (2 docentes e 2 discentes) construídos a partir da base visual fornecida pelo professor (`docente.html`, `discente.html`, `estilos.css`), porém gerados automaticamente por um pipeline em Python a partir de uma fonte de dados estruturada única (`codigo-fonte/dados_perfis.json`).
2. **Geração Automática de Grafo RDF e JSON-LD:** o mesmo processo de build gera o grafo `ontologia/dados.ttl` e embute metadados `application/ld+json` + `<link rel="alternate" type="text/turtle">` em cada página HTML.
3. **Navegação Semântica Cruzada e Links LOD:** interligação clicável entre coautores em publicações, visualização de classificações facetadas SKOS e links diretos para conceitos equivalentes na Wikidata, DBpedia, ORCID e Lattes.
4. **Execução e Validação de Consultas SPARQL:** suporte às 6 perguntas de competência obrigatórias com resultados verificados via `rdflib`.

---

## 4. Tipos de Perfil Contemplados

| Tipo de Perfil | Classe OWL Principal | Taxonomia SKOS (`pes:`) | Perfis Disponibilizados (v0.1) |
| :--- | :--- | :--- | :--- |
| **Docente** | `acad:Docente` | `pes:Docente`, `pes:Pesquisador`, `pes:Orientador` | 1. Profa. Dra. Ana Exemplo da Silva *(adaptado do modelo)*<br>2. Prof. Dr. Carlos Eduardo Mendes *(novo perfil)* |
| **Discente** | `acad:DiscenteGraduacao` (`rdfs:subClassOf acad:Discente`) | `pes:Discente`, `pes:Graduando`, `pes:Extensionista` / `pes:Bolsista` | 1. João Exemplo Pereira *(adaptado do modelo)*<br>2. Mariana Costa Souza *(novo perfil)* |

---

## 5. Justificativa das Informações Selecionadas
Os campos selecionados equilibram os requisitos explícitos do enunciado, os modelos HTML fornecidos e as necessidades das perguntas de competência SPARQL:
- **Identificação e Apresentação (`nome`, `email`, `cargoOuFuncao`, `apresentacao`):** identificam o pesquisador/estudante e contextualizam sua trajetória.
- **Vínculo Institucional Estruturado (`Instituição`, `UnidadeAcadêmica`, `Departamento`, `Curso`):** modela explicitamente a cadeia organizacional da UFRRJ (Docente $\rightarrow$ Departamento $\rightarrow$ ICEx; Discente $\rightarrow$ Curso $\rightarrow$ ICEx), permitindo consultas tanto por departamento/curso quanto unificadas por unidade acadêmica (Perguntas 1, 2 e 6).
- **Formação Acadêmica (`FormacaoAcademica`):** reificada como entidade própria para preservar grau, curso, instituição e ano de conclusão sem perda semântica.
- **Áreas de Atuação/Interesse (`AreaConhecimento`):** tratadas como recursos (`skos:Concept`) em vez de meras strings literais, viabilizando desambiguação e ligação direta via `skos:exactMatch` com Wikidata e DBpedia (Pergunta 3).
- **Disciplinas, Projetos e Grupos de Pesquisa:** estruturam relações de ensino e colaboração entre docentes e discentes (Pergunta 4).
- **Publicações e Coautorias (`Publicacao`):** permitem ligar múltiplos autores (`acad:temAutor`), recuperar DOI e listar coautores de um docente (Pergunta 5).
- **Redes e Identificadores Externos (`ORCID`, `Lattes`, `LinkedIn`, `ResearchGate`):** combatem homônimos e conectam o grafo institucional à Web de Dados.
