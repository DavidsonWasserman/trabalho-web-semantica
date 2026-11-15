# Pesquisa de Ontologias, Metadados e Vocabulários Controlados

## 1. Metodologia de Pesquisa e Avaliação
Em conformidade com as boas práticas de engenharia ontológica (como o método *Ontology Development 101* e os princípios de Linked Open Data de Tim Berners-Lee), antes de criar termos novos foram pesquisados os principais vocabulários padronizados e ontologias acadêmicas existentes na Web Semântica. O critério de seleção adotado foi a **adequação semântica ao problema de perfis acadêmicos universitários**, evitando tanto a reinvenção de conceitos universais quanto o excesso de complexidade desnecessária.

---

## 2. Ontologias e Vocabulários Avaliados

| Vocabulário / Ontologia | Prefixo e Namespace | Escopo Principal | Avaliação de Adequação | Decisão no Projeto |
| :--- | :--- | :--- | :--- | :--- |
| **FOAF** (*Friend of a Friend*) | `foaf: <http://xmlns.com/foaf/0.1/>` | Pessoas, grupos, organizações, documentos e projetos. | **Alta** para identificação básica (`Person`, `Organization`, `Project`, `name`, `mbox`, `homepage`), porém insuficiente para relações universitárias específicas (lotação em departamento, matrícula em curso). | **Reutilizado e alinhado:** `acad:Pessoa ⊑ foaf:Person`, `acad:OrganizacaoAcademica ⊑ foaf:Organization`, `acad:ProjetoPesquisa ⊑ foaf:Project`, `acad:nome ⊑ foaf:name`. |
| **Schema.org** | `schema: <https://schema.org/>` | Marcação estruturada para motores de busca (JSON-LD/SEO). | **Muito Alta** para interoperabilidade web (`Person`, `CollegeOrUniversity`, `ScholarlyArticle`, `Course`, `ResearchProject`, `knowsAbout`), mas focado em descoberta web e menos rígido em inferência OWL DL. | **Reutilizado e alinhado:** embutido em JSON-LD em todas as páginas HTML e alinhado via `rdfs:subClassOf` na ontologia OWL. |
| **W3C SKOS** (*Simple Knowledge Organization System*) | `skos: <http://www.w3.org/2004/02/skos/core#>` | Tesauros, taxonomias facetadas e mapeamentos conceituais. | **Ideal** para padronizar vínculos institucionais, atuações e áreas do conhecimento sem ambiguidade, além de fornecer `skos:exactMatch` e `skos:closeMatch` para ligar áreas à Wikidata/DBpedia. | **Adotado diretamente:** base do arquivo `ontologia/taxonomia_pessoas.ttl` e da classe `acad:AreaConhecimento ⊑ skos:Concept`. |
| **BIBO** (*Bibliographic Ontology*) | `bibo: <http://purl.org/ontology/bibo/>` | Representação de citações e documentos bibliográficos em RDF. | **Alta** para publicações científicas (`bibo:AcademicArticle`, `bibo:doi`). | **Reutilizado e alinhado:** `acad:Publicacao ⊑ bibo:AcademicArticle` e uso direto de `bibo:doi`. |
| **Dublin Core Terms** | `dcterms: <http://purl.org/dc/terms/>` | Metadados descritivos, proveniência e licenciamento de recursos. | **Essencial** para descrever título, criador, fonte, data de modificação e licença de reutilização do grafo LOD. | **Adotado diretamente:** metadados de proveniência em `ontologia.owl`, `taxonomia_pessoas.ttl` e `dados.ttl`. |
| **VIVO Ontology** (`vivo:`) | `vivo: <http://vivoweb.org/ontology/core#>` | Ecossistema acadêmico completo (currículos, bolsas, comitês, posições temporais). | **Abrangente, porém muito pesada** para um portal demonstrativo enxuto: depende de dezenas de classes intermediárias (BFO/IAO/OBO) e relações n-árias complexas (*Positions*, *Authorship*) que dificultam consultas SPARQL didáticas. | **Referência conceitual sem importação integral:** inspiramo-nos na separação entre Pessoa, Organização, Projeto e Publicação do VIVO, optando por uma ontologia de aplicação própria (`acad:`) mais leve e direta. |

---

## 3. Taxonomia Facetada e Vocabulário Controlado (`taxonomia_pessoas.ttl`)

Para evitar o erro comum de modelar pessoas universitárias em uma árvore rígida e excludente (onde um indivíduo só poderia estar em uma única categoria), adotamos e integramos ao projeto a **Taxonomia Facetada em W3C SKOS** (`pes:EsquemaPessoas`), organizada em **três facetas ortogonais**:

1. **Faceta 1 — `pes:Vinculo` (Quem a pessoa é formalmente na instituição):**
   - `pes:Docente` (`skos:altLabel`: *"Professor"*, *"Corpo docente"*)
   - `pes:Discente` (`skos:altLabel`: *"Aluno"*, *"Estudante"*)
     - `pes:Graduando` (*Discente de graduação*)
     - `pes:Especializando` (*Discente de especialização*)
     - `pes:Mestrando` (*Discente de mestrado*)
     - `pes:Doutorando` (*Discente de doutorado*)
   - `pes:TecnicoAdministrativo`, `pes:Terceirizado`, `pes:ColaboradorExterno`, `pes:Egresso`.
2. **Faceta 2 — `pes:Atuacao` (Quais papéis acadêmicos desempenha):**
   - `pes:Pesquisador`, `pes:Extensionista`, `pes:Orientador`, `pes:Gestor`, `pes:Empreendedor`, `pes:ProfissionalAutonomo`.
3. **Faceta 3 — `pes:Condicao` (Modalidade de fomento/apoio):**
   - `pes:Bolsista`, `pes:Voluntario`.

### Como a Taxonomia Controlada resolve problemas práticos
- **Multiclassificação limpa:** um único estudante pode receber `pes:Graduando` (vínculo), `pes:Pesquisador` (atuação) e `pes:Bolsista` (condição) via `acad:possuiClassificacaoSKOS`, sem explodir o número de subclasses OWL.
- **Padronização terminológica:** termos preferenciais (`skos:prefLabel`) como *"Discente"* e *"Docente"* convivem com termos alternativos de busca (`skos:altLabel`: *"Aluno"*, *"Estudante"*, *"Professor"*), além de notas de escopo (`skos:scopeNote`) que vetam termos ambíguos.
- **Mapeamento para Schema.org:** conceitos SKOS carregam alinhamentos `skos:closeMatch` (ex.: `pes:Discente skos:closeMatch schema:Student`).

---

## 4. Conclusão da Escolha Híbrida
A combinação de **Ontologia de Aplicação OWL 2 (`acad:`)** + **Alinhamento a FOAF/Schema.org/BIBO/DCTerms** + **Taxonomia SKOS (`pes:`)** atinge o melhor equilíbrio entre rigor lógico (compatível com raciocinadores OWL), clareza nas 6 consultas SPARQL e aderência direta ao ecossistema de Linked Open Data na Web.
