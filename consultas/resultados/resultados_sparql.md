# Resultados das Consultas SPARQL (Perguntas de Competência)

Este documento foi gerado automaticamente por `codigo-fonte/build.py` utilizando `rdflib` sobre a união dos grafos:
- `ontologia/ontologia.owl`
- `ontologia/taxonomia_pessoas.ttl`
- `ontologia/dados.ttl`

**Data da última execução:** 2026-11-15

---

## 1. Quais são os docentes cadastrados e seus respectivos departamentos ou unidades acadêmicas?

**Arquivo:** `consultas/consulta01.rq`

**Classes e propriedades utilizadas:** Utiliza as classes `acad:Docente`, `acad:Departamento` e `acad:UnidadeAcademica` conectadas pelas propriedades de objeto `acad:lotadoEm` e `acad:parteDeUnidade`, além das propriedades de dados `acad:nome`, `acad:cargoOuFuncao`, `acad:nomeOrganizacao` e `acad:sigla`.

### Consulta SPARQL
```sparql
# Consulta 01 — Quais são os docentes cadastrados e seus respectivos departamentos ou unidades acadêmicas?
# Explora a hierarquia institucional: Docente -> Departamento -> Unidade Acadêmica.

PREFIX acad: <https://davidsonwasserman.github.io/trabalho-web-semantica/ontologia/ontologia.owl#>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?docente ?nomeDocente ?cargo ?nomeDepartamento ?nomeUnidade ?siglaUnidade
WHERE {
  ?docente a acad:Docente ;
           acad:nome ?nomeDocente ;
           acad:lotadoEm ?departamento .
  OPTIONAL { ?docente acad:cargoOuFuncao ?cargo . }
  ?departamento acad:nomeOrganizacao ?nomeDepartamento ;
                acad:parteDeUnidade ?unidade .
  ?unidade acad:nomeOrganizacao ?nomeUnidade ;
           acad:sigla ?siglaUnidade .
}
ORDER BY ?nomeDocente
```

### Resultado obtido (2 registro(s))

| `?docente` | `?nomeDocente` | `?cargo` | `?nomeDepartamento` | `?nomeUnidade` | `?siglaUnidade` |
| --- | --- | --- | --- | --- | --- |
| recurso:DocenteCarlosMendes | Prof. Dr. Carlos Eduardo Mendes | Professor Adjunto | Departamento de Computação | Instituto de Ciências Exatas | ICEx |
| recurso:DocenteAnaSilva | Profa. Dra. Ana Exemplo da Silva | Professora Associada | Departamento de Computação | Instituto de Ciências Exatas | ICEx |

---

## 2. Quais discentes pertencem a determinado curso?

**Arquivo:** `consultas/consulta02.rq`

**Classes e propriedades utilizadas:** Relaciona `acad:Discente` a `acad:Curso` por meio de `acad:matriculadoEm`, navegando até `acad:UnidadeAcademica` via `acad:oferecidoPorUnidade` e filtrando por curso (`acad:nomeCurso` contendo 'sistemas de informação').

### Consulta SPARQL
```sparql
# Consulta 02 — Quais discentes pertencem a determinado curso?
# Recupera discentes matriculados em um curso específico (ex.: Bacharelado em Sistemas de Informação),
# demonstrando também o vínculo do curso com a Unidade Acadêmica (ICEx).

PREFIX acad: <https://davidsonwasserman.github.io/trabalho-web-semantica/ontologia/ontologia.owl#>

SELECT ?discente ?nomeDiscente ?nomeCurso ?anoIngresso ?periodoAtual ?nomeUnidade
WHERE {
  ?discente a acad:Discente ;
            acad:nome ?nomeDiscente ;
            acad:matriculadoEm ?curso .
  ?curso acad:nomeCurso ?nomeCurso ;
         acad:oferecidoPorUnidade ?unidade .
  ?unidade acad:nomeOrganizacao ?nomeUnidade .
  OPTIONAL { ?discente acad:anoIngresso ?anoIngresso . }
  OPTIONAL { ?discente acad:periodoAtual ?periodoAtual . }
  FILTER(CONTAINS(LCASE(?nomeCurso), "sistemas de informação"))
}
ORDER BY ?nomeDiscente
```

### Resultado obtido (1 registro(s))

| `?discente` | `?nomeDiscente` | `?nomeCurso` | `?anoIngresso` | `?periodoAtual` | `?nomeUnidade` |
| --- | --- | --- | --- | --- | --- |
| recurso:DiscenteJoaoPereira | João Exemplo Pereira | Bacharelado em Sistemas de Informação | 2024 | 5º período | Instituto de Ciências Exatas |

---

## 3. Quais docentes atuam em determinada área de pesquisa?

**Arquivo:** `consultas/consulta03.rq`

**Classes e propriedades utilizadas:** Conecta `acad:Docente` à classe `acad:AreaConhecimento` (subclasse de `skos:Concept`) via `acad:atuaEmArea`, filtrando pela área 'Dados Abertos' e recuperando as referências externas LOD (Wikidata e DBpedia) ligadas por `skos:exactMatch`.

### Consulta SPARQL
```sparql
# Consulta 03 — Quais docentes atuam em determinada área de pesquisa?
# Filtra docentes que atuam na área "Dados Abertos" e recupera a ligação externa LOD (Wikidata/DBpedia).

PREFIX acad: <https://davidsonwasserman.github.io/trabalho-web-semantica/ontologia/ontologia.owl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?docente ?nomeDocente ?nomeArea ?linkExternoLOD
WHERE {
  ?docente a acad:Docente ;
           acad:nome ?nomeDocente ;
           acad:atuaEmArea ?area .
  ?area acad:nomeArea ?nomeArea .
  OPTIONAL { ?area skos:exactMatch ?linkExternoLOD . }
  FILTER(LCASE(?nomeArea) = "dados abertos")
}
ORDER BY ?nomeDocente ?linkExternoLOD
```

### Resultado obtido (4 registro(s))

| `?docente` | `?nomeDocente` | `?nomeArea` | `?linkExternoLOD` |
| --- | --- | --- | --- |
| recurso:DocenteCarlosMendes | Prof. Dr. Carlos Eduardo Mendes | Dados Abertos | dbr:Open_data |
| recurso:DocenteCarlosMendes | Prof. Dr. Carlos Eduardo Mendes | Dados Abertos | wd:Q309901 |
| recurso:DocenteAnaSilva | Profa. Dra. Ana Exemplo da Silva | Dados Abertos | dbr:Open_data |
| recurso:DocenteAnaSilva | Profa. Dra. Ana Exemplo da Silva | Dados Abertos | wd:Q309901 |

---

## 4. Quais docentes e discentes participam de um mesmo projeto de pesquisa?

**Arquivo:** `consultas/consulta04.rq`

**Classes e propriedades utilizadas:** Consulta multi-entidade que cruza três classes distintas (`acad:ProjetoPesquisa`, `acad:Docente` e `acad:Discente`) através da propriedade `acad:participaDeProjeto`, recuperando ainda o curso do discente via `acad:matriculadoEm`.

### Consulta SPARQL
```sparql
# Consulta 04 — Quais docentes e discentes participam de um mesmo projeto de pesquisa?
# Consulta multi-entidade conectando três tipos distintos (Docente, Discente e ProjetoPesquisa).

PREFIX acad: <https://davidsonwasserman.github.io/trabalho-web-semantica/ontologia/ontologia.owl#>

SELECT ?tituloProjeto ?nomeDocente ?nomeDiscente ?nomeCursoDiscente
WHERE {
  ?projeto a acad:ProjetoPesquisa ;
           acad:tituloProjeto ?tituloProjeto .
  ?docente a acad:Docente ;
           acad:nome ?nomeDocente ;
           acad:participaDeProjeto ?projeto .
  ?discente a acad:Discente ;
            acad:nome ?nomeDiscente ;
            acad:participaDeProjeto ?projeto ;
            acad:matriculadoEm ?curso .
  ?curso acad:nomeCurso ?nomeCursoDiscente .
}
ORDER BY ?tituloProjeto ?nomeDocente ?nomeDiscente
```

### Resultado obtido (5 registro(s))

| `?tituloProjeto` | `?nomeDocente` | `?nomeDiscente` | `?nomeCursoDiscente` |
| --- | --- | --- | --- |
| Grafos de Conhecimento e IA Explicável no Ensino Superior | Prof. Dr. Carlos Eduardo Mendes | Mariana Costa Souza | Bacharelado em Ciência da Computação |
| Projeto Exemplo de Dados Abertos | Prof. Dr. Carlos Eduardo Mendes | João Exemplo Pereira | Bacharelado em Sistemas de Informação |
| Projeto Exemplo de Dados Abertos | Prof. Dr. Carlos Eduardo Mendes | Mariana Costa Souza | Bacharelado em Ciência da Computação |
| Projeto Exemplo de Dados Abertos | Profa. Dra. Ana Exemplo da Silva | João Exemplo Pereira | Bacharelado em Sistemas de Informação |
| Projeto Exemplo de Dados Abertos | Profa. Dra. Ana Exemplo da Silva | Mariana Costa Souza | Bacharelado em Ciência da Computação |

---

## 5. Quais publicações estão associadas a determinado docente e quem são seus coautores, quando essa informação estiver representada?

**Arquivo:** `consultas/consulta05.rq`

**Classes e propriedades utilizadas:** Utiliza `acad:Publicacao` e `acad:temAutor` ligando tanto o docente alvo (Profa. Dra. Ana Exemplo da Silva) quanto os demais autores (`?coautor != ?docente`), retornando metadados bibliográficos (`acad:tituloPublicacao`, `acad:anoPublicacao`, `acad:doi`) e o papel de cada coautor.

### Consulta SPARQL
```sparql
# Consulta 05 — Quais publicações estão associadas a determinado docente e quem são seus coautores?
# Explora a relação de autoria entre Publicacao, o docente alvo (Profa. Dra. Ana Exemplo da Silva)
# e seus respectivos coautores (docentes ou discentes).

PREFIX acad: <https://davidsonwasserman.github.io/trabalho-web-semantica/ontologia/ontologia.owl#>

SELECT ?tituloPublicacao ?anoPublicacao ?doi ?nomeDocente ?nomeCoautor ?papelCoautor
WHERE {
  ?docente a acad:Docente ;
           acad:nome ?nomeDocente .
  FILTER(CONTAINS(LCASE(?nomeDocente), "ana exemplo da silva"))

  ?publicacao a acad:Publicacao ;
              acad:tituloPublicacao ?tituloPublicacao ;
              acad:anoPublicacao ?anoPublicacao ;
              acad:temAutor ?docente ;
              acad:temAutor ?coautor .

  ?coautor acad:nome ?nomeCoautor .
  OPTIONAL { ?coautor acad:cargoOuFuncao ?papelCoautor . }
  OPTIONAL { ?publicacao acad:doi ?doi . }

  FILTER(?coautor != ?docente)
}
ORDER BY DESC(?anoPublicacao) ?tituloPublicacao ?nomeCoautor
```

### Resultado obtido (6 registro(s))

| `?tituloPublicacao` | `?anoPublicacao` | `?doi` | `?nomeDocente` | `?nomeCoautor` | `?papelCoautor` |
| --- | --- | --- | --- | --- | --- |
| Integração de Grafos de Conhecimento e Modelos de Linguagem na Iniciação Científica | 2025 | 10.1000/ufrrj.kg.2025.008 | Profa. Dra. Ana Exemplo da Silva | Mariana Costa Souza | Discente de Ciência da Computação |
| Integração de Grafos de Conhecimento e Modelos de Linguagem na Iniciação Científica | 2025 | 10.1000/ufrrj.kg.2025.008 | Profa. Dra. Ana Exemplo da Silva | Prof. Dr. Carlos Eduardo Mendes | Professor Adjunto |
| Protótipo de aplicação para organização semântica de dados acadêmicos | 2025 | 10.1000/ufrrj.web.2025.003 | Profa. Dra. Ana Exemplo da Silva | João Exemplo Pereira | Discente de Sistemas de Informação |
| Exemplo de publicação sobre dados conectados no ensino superior | 2024 | 10.1000/ufrrj.lod.2024.001 | Profa. Dra. Ana Exemplo da Silva | João Exemplo Pereira | Discente de Sistemas de Informação |
| Exemplo de publicação sobre dados conectados no ensino superior | 2024 | 10.1000/ufrrj.lod.2024.001 | Profa. Dra. Ana Exemplo da Silva | Prof. Dr. Carlos Eduardo Mendes | Professor Adjunto |
| Exemplo de estudo em representação do conhecimento e ontologias OWL | 2022 | 10.1000/ufrrj.owl.2022.015 | Profa. Dra. Ana Exemplo da Silva | Prof. Dr. Carlos Eduardo Mendes | Professor Adjunto |

---

## 6. Quais pessoas estão vinculadas a uma unidade acadêmica específica, independentemente de serem docentes ou discentes?

**Arquivo:** `consultas/consulta06.rq`

**Classes e propriedades utilizadas:** Demonstra Property Paths SPARQL 1.1 (`(acad:lotadoEm/acad:parteDeUnidade)|(acad:matriculadoEm/acad:oferecidoPorUnidade)`) sobre a superclasse `acad:Pessoa`, unificando docentes e discentes vinculados ao Instituto de Ciências Exatas (ICEx).

### Consulta SPARQL
```sparql
# Consulta 06 — Quais pessoas estão vinculadas a uma unidade acadêmica específica,
# independentemente de serem docentes ou discentes?
# Usa Property Paths combinando (lotadoEm/parteDeUnidade) para docentes e
# (matriculadoEm/oferecidoPorUnidade) para discentes, unificados pela superclasse acad:Pessoa.

PREFIX acad: <https://davidsonwasserman.github.io/trabalho-web-semantica/ontologia/ontologia.owl#>

SELECT DISTINCT ?pessoa ?nomePessoa ?tipoVinculo ?cargo ?nomeUnidade ?siglaUnidade
WHERE {
  ?unidade a acad:UnidadeAcademica ;
           acad:nomeOrganizacao ?nomeUnidade ;
           acad:sigla ?siglaUnidade .
  FILTER(?siglaUnidade = "ICEx")

  ?pessoa (acad:lotadoEm/acad:parteDeUnidade)|(acad:matriculadoEm/acad:oferecidoPorUnidade) ?unidade ;
          acad:nome ?nomePessoa ;
          a ?tipoVinculo .

  OPTIONAL { ?pessoa acad:cargoOuFuncao ?cargo . }
  FILTER(?tipoVinculo IN (acad:Docente, acad:Discente))
}
ORDER BY ?tipoVinculo ?nomePessoa
```

### Resultado obtido (4 registro(s))

| `?pessoa` | `?nomePessoa` | `?tipoVinculo` | `?cargo` | `?nomeUnidade` | `?siglaUnidade` |
| --- | --- | --- | --- | --- | --- |
| recurso:DiscenteJoaoPereira | João Exemplo Pereira | acad:Discente | Discente de Sistemas de Informação | Instituto de Ciências Exatas | ICEx |
| recurso:DiscenteMarianaSouza | Mariana Costa Souza | acad:Discente | Discente de Ciência da Computação | Instituto de Ciências Exatas | ICEx |
| recurso:DocenteCarlosMendes | Prof. Dr. Carlos Eduardo Mendes | acad:Docente | Professor Adjunto | Instituto de Ciências Exatas | ICEx |
| recurso:DocenteAnaSilva | Profa. Dra. Ana Exemplo da Silva | acad:Docente | Professora Associada | Instituto de Ciências Exatas | ICEx |

---
