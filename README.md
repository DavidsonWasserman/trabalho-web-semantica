# Portal Semântico de Perfis Acadêmicos e Linked Open Data — UFRRJ

Trabalho prático da disciplina **Web Semântica e Linked Open Data** (Departamento de Computação / Instituto de Ciências Exatas — UFRRJ), ministrada pelo Prof. Tiago Cruz de França.

- **Repositório Git:** `git@github.com:DavidsonWasserman/trabalho-web-semantica.git`
- **Endereço Público (GitHub Pages):** https://davidsonwasserman.github.io/trabalho-web-semantica/
- **Status Atual:** Versão Inicial (`v0.1`) — estrutura completa ponta a ponta preparada para alinhamento em 18/11 e evolução final para entrega em 01/12.

---

## Integrantes

- **Davidson Wasserman** — Graduando em Sistemas de Informação (UFRRJ)
- **Nicolas Duarte** — Graduando em Sistemas de Informação (UFRRJ)
---

## Endereços Públicos (URIs e Artefatos)

| Recurso | URL Pública (GitHub Pages) |
| :--- | :--- |
| **Portal Web (Diretório de Perfis)** | `https://davidsonwasserman.github.io/trabalho-web-semantica/` |
| **Ontologia de Aplicação (OWL 2 / RDF/XML)** | `https://davidsonwasserman.github.io/trabalho-web-semantica/ontologia/ontologia.owl` |
| **Ontologia de Aplicação (OWL 2 / Turtle)** | `https://davidsonwasserman.github.io/trabalho-web-semantica/ontologia/ontologia.ttl` |
| **Vocabulário Controlado (W3C SKOS)** | `https://davidsonwasserman.github.io/trabalho-web-semantica/ontologia/taxonomia_pessoas.ttl` |
| **Grafo de Dados RDF (Instâncias + LOD)** | `https://davidsonwasserman.github.io/trabalho-web-semantica/ontologia/dados.ttl` |
| **Docente 1 (Profa. Dra. Ana Exemplo da Silva)** | `https://davidsonwasserman.github.io/trabalho-web-semantica/exemplos/perfis/ana-silva.html` |
| **Docente 2 (Prof. Dr. Carlos Eduardo Mendes)** | `https://davidsonwasserman.github.io/trabalho-web-semantica/exemplos/perfis/carlos-mendes.html` |
| **Discente 1 (João Exemplo Pereira)** | `https://davidsonwasserman.github.io/trabalho-web-semantica/exemplos/perfis/joao-pereira.html` |
| **Discente 2 (Mariana Costa Souza)** | `https://davidsonwasserman.github.io/trabalho-web-semantica/exemplos/perfis/mariana-souza.html` |

---

## Estrutura do Repositório

```text
TrabalhoWebSemantica/
├── README.md
├── index.html                        # Diretório público gerado automaticamente
├── estilos.css                       # Folha de estilos baseada no modelo do professor
├── foto-exemplo.svg                  # Avatar SVG para os perfis
├── paginaTrabalho/                   # Modelos HTML/CSS originais fornecidos pelo professor
├── proposta/
│   ├── descricao.md                  # Objetivo, público-alvo, funcionalidades e perfis
│   ├── requisitos.md                 # Requisitos funcionais, semânticos e perguntas de competência
│   └── decisoes-modelagem.md         # URIs, política LOD/sameAs, licença e Declaração de IA
├── documentacao/
│   ├── dicionario-dados.md           # Entidades, tipos XSD, cardinalidades e regras
│   ├── vocabularios.md               # Pesquisa FOAF, Schema.org, VIVO, BIBO, DCTerms e SKOS
│   ├── ontologia.md                  # Classes, propriedades, restrições OWL e inferências
│   ├── diagrama.mmd                  # Fonte Mermaid do diagrama da ontologia
│   └── diagrama.svg                  # Diagrama visual da ontologia
├── ontologia/
│   ├── ontologia.owl                 # Ontologia OWL 2 (RDF/XML) gerada a partir do Turtle
│   ├── ontologia.ttl                 # Ontologia OWL 2 (Turtle) compatível com Protégé/HermiT
│   ├── taxonomia_pessoas.ttl         # Taxonomia facetada SKOS (Vínculo, Atuação, Condição)
│   └── dados.ttl                     # Grafo RDF completo (1.013 triplas no grafo unificado)
├── consultas/
│   ├── consulta01.rq ... consulta06.rq
│   └── resultados/
│       └── resultados_sparql.md      # Consultas, resultados e explicação das classes/propriedades
├── exemplos/
│   └── perfis/                       # Páginas HTML individuais geradas com JSON-LD embutido
└── codigo-fonte/
    ├── dados_perfis.json             # Fonte de dados estruturada única
    └── build.py                      # Script Python gerador e validador (RDF/HTML/SPARQL)
```

---

## Como Reproduzir a Demonstração e Executar as Consultas SPARQL

### Pré-requisitos
- Python 3.10+ com a biblioteca `rdflib` instalada:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install rdflib
  ```

### Executar o Build Completo + Validação OWL/RDF + Consultas SPARQL
```bash
python3 codigo-fonte/build.py
```

O script executa automaticamente:
1. Geração de `ontologia/dados.ttl` a partir de `codigo-fonte/dados_perfis.json`;
2. Geração de `index.html` e das 4 páginas em `exemplos/perfis/*.html` (com JSON-LD embutido e `<link rel="alternate" type="text/turtle">`);
3. Validação sintática de `ontologia.owl`, `taxonomia_pessoas.ttl`, `dados.ttl` e dos blocos JSON-LD;
4. Execução das 6 consultas SPARQL (`consultas/consulta01.rq` .. `consulta06.rq`) sobre a união dos grafos e atualização de `consultas/resultados/resultados_sparql.md`.

### Visualizar Localmente via Servidor HTTP
```bash
python3 -m http.server 8000
```
Acesse `http://localhost:8000/` no navegador.

---

## Proveniência, Licença e Uso de IA

- **Licença:** [Creative Commons Atribuição 4.0 Internacional (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).
- **Declaração de Uso de Ferramentas de IA:** Documentada integralmente na Seção 5 de [proposta/decisoes-modelagem.md](proposta/decisoes-modelagem.md), detalhando ferramentas, prompts, partes assistidas e validação pela dupla.
