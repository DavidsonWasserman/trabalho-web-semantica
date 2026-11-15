# Dicionário de Dados do Domínio Acadêmico

Este dicionário descreve todas as entidades, atributos literais (Datatype Properties) e relacionamentos (Object Properties) que compõem o domínio dos perfis acadêmicos de docentes e discentes da UFRRJ, assegurando coerência entre a fonte JSON (`codigo-fonte/dados_perfis.json`), a ontologia OWL (`ontologia/ontologia.owl`) e o grafo RDF (`ontologia/dados.ttl`).

---

## 1. Entidades (Classes)

| Entidade / Classe OWL | Significado no Domínio | Regra / Restrição Principal |
| :--- | :--- | :--- |
| `acad:Pessoa` | Superclasse que representa qualquer membro da comunidade universitária. | Alinhada a `foaf:Person` e `schema:Person`; disjunta de organizações, publicações e projetos. |
| `acad:Docente` | Professor/pesquisador do quadro acadêmico. | Subclasse de `acad:Pessoa`; deve possuir lotação em pelo menos 1 `acad:Departamento`. |
| `acad:Discente` | Estudante matriculado em curso regular da universidade. | Subclasse de `acad:Pessoa`; deve possuir matrícula em pelo menos 1 `acad:Curso`. |
| `acad:DiscenteGraduacao` | Discente vinculado a curso de graduação (bacharelado/licenciatura/tecnologia). | Subclasse de `acad:Discente`. |
| `acad:DiscentePosGraduacao` | Discente vinculado a mestrado ou doutorado. | Subclasse de `acad:Discente`. |
| `acad:InstituicaoEnsino` | Universidade ou instituição de ensino superior (ex.: UFRRJ). | Subclasse de `acad:OrganizacaoAcademica` e `schema:CollegeOrUniversity`. |
| `acad:UnidadeAcademica` | Instituto, faculdade ou centro acadêmico (ex.: ICEx). | Subclasse de `acad:OrganizacaoAcademica`; pertence a 1 instituição. |
| `acad:Departamento` | Departamento acadêmico-administrativo (ex.: Departamento de Computação). | Subclasse de `acad:OrganizacaoAcademica`; parte de 1 unidade acadêmica. |
| `acad:GrupoPesquisa` | Grupo ou núcleo formal de pesquisa e extensão. | Subclasse de `acad:OrganizacaoAcademica`. |
| `acad:Curso` | Curso de graduação ou programa de pós-graduação. | Subclasse de `schema:EducationalOccupationalProgram`; oferecido por 1 unidade acadêmica. |
| `acad:AreaConhecimento` | Tema científico, especialidade ou área de interesse. | Subclasse de `skos:Concept`; ligada a bases externas via `skos:exactMatch`. |
| `acad:Disciplina` | Componente curricular ministrado por docentes. | Subclasse de `schema:Course`. |
| `acad:ProjetoPesquisa` | Projeto formal de pesquisa, desenvolvimento ou extensão. | Subclasse de `foaf:Project` e `schema:ResearchProject`; possui pelo menos 1 participante. |
| `acad:Publicacao` | Artigo, trabalho completo ou produção acadêmica/técnica. | Subclasse de `bibo:AcademicArticle` e `schema:ScholarlyArticle`; exige 1 título, 1 ano e ≥ 1 autor. |
| `acad:FormacaoAcademica` | Titulação acadêmica (graduação, mestrado, doutorado) de uma pessoa. | Classe de reificação associando grau, curso, instituição e ano. |
| `acad:RedeAcademica` | Perfil externo em serviço acadêmico ou rede profissional. | Classe auxiliar contendo nome da rede e URL externa. |

---

## 2. Atributos Literais (Datatype Properties)

| Campo / Propriedade | Domínio | Tipo XSD | Obrigatoriedade / Cardinalidade | Significado e Regras |
| :--- | :--- | :--- | :--- | :--- |
| `acad:nome` | `acad:Pessoa` | `xsd:string` | Obrigatório (`1`) | Nome completo de exibição da pessoa (subpropriedade de `foaf:name`). |
| `acad:email` | `acad:Pessoa` | `xsd:string` | Recomendado (`0..n`) | E-mail institucional ou demonstrativo; nunca usar e-mails privados sensíveis. |
| `acad:cargoOuFuncao` | `acad:Pessoa` | `xsd:string` | Obrigatório (`1`) | Cargo docente (ex.: *Professora Associada*) ou descrição de vínculo discente. |
| `acad:apresentacao` | `acad:Pessoa` | `xsd:string` | Obrigatório (`1`) | Texto livre de apresentação acadêmica e trajetória. |
| `acad:paginaPessoal` | `acad:Pessoa` | `xsd:anyURI` | Opcional (`0..1`) | URL da página web pessoal ou página pública do perfil. |
| `acad:orcid` | `acad:Pessoa` | `xsd:anyURI` | Recomendado (`0..1`) | URI oficial do identificador persistente ORCID (`https://orcid.org/...`). |
| `acad:lattes` | `acad:Pessoa` | `xsd:anyURI` | Recomendado (`0..1`) | URI do Currículo Lattes no CNPq. |
| `acad:anoIngresso` | `acad:Discente` | `xsd:integer` | Obrigatório para discentes (`0..1`) | Ano de ingresso no curso (formato inteiro, compatível com OWL 2/HermiT). |
| `acad:periodoAtual` | `acad:Discente` | `xsd:string` | Opcional (`0..1`) | Período letivo corrente do discente (ex.: `"5º período"`). |
| `acad:nomeOrganizacao` | `acad:OrganizacaoAcademica` | `xsd:string` | Obrigatório (`1`) | Denominação oficial da instituição, unidade, departamento ou grupo. |
| `acad:sigla` | `acad:OrganizacaoAcademica` | `xsd:string` | Opcional (`0..1`) | Sigla institucional (ex.: `"UFRRJ"`, `"ICEx"`). |
| `acad:nomeCurso` | `acad:Curso` | `xsd:string` | Obrigatório (`1`) | Nome completo do curso de graduação ou pós-graduação. |
| `acad:modalidadeCurso` | `acad:Curso` | `xsd:string` | Recomendado (`0..1`) | Nível/modalidade (ex.: `"Graduação — Bacharelado"`). |
| `acad:nomeArea` | `acad:AreaConhecimento` | `xsd:string` | Obrigatório (`1`) | Rótulo padronizado da área em português. |
| `acad:nomeDisciplina` | `acad:Disciplina` | `xsd:string` | Obrigatório (`1`) | Nome do componente curricular ministrado. |
| `acad:codigoDisciplina` | `acad:Disciplina` | `xsd:string` | Opcional (`0..1`) | Código institucional da disciplina (ex.: `"IC801"`). |
| `acad:tituloProjeto` | `acad:ProjetoPesquisa` | `xsd:string` | Obrigatório (`1`) | Título oficial do projeto de pesquisa/extensão. |
| `acad:descricaoProjeto` | `acad:ProjetoPesquisa` | `xsd:string` | Recomendado (`0..1`) | Resumo do escopo e objetivos do projeto. |
| `acad:tituloPublicacao` | `acad:Publicacao` | `xsd:string` | Obrigatório (`1`, Funcional) | Título da obra ou produção acadêmica. |
| `acad:citacaoBibliografica` | `acad:Publicacao` | `xsd:string` | Obrigatório (`1`) | Referência bibliográfica formatada para exibição na página. |
| `acad:anoPublicacao` | `acad:Publicacao` | `xsd:integer` | Obrigatório (`1`, Funcional) | Ano de publicação em inteiro (`xsd:integer`). |
| `acad:doi` | `acad:Publicacao` | `xsd:string` | Opcional (`0..1`) | Identificador Digital de Objeto (DOI), complementado por `bibo:doi`. |
| `acad:grauFormacao` | `acad:FormacaoAcademica` | `xsd:string` | Obrigatório (`1`) | Nível da titulação (*Graduação*, *Mestrado*, *Doutorado*). |
| `acad:cursoFormacao` | `acad:FormacaoAcademica` | `xsd:string` | Obrigatório (`1`) | Nome do curso ou área da titulação. |
| `acad:anoConclusao` | `acad:FormacaoAcademica` | `xsd:integer` | Opcional (`0..1`) | Ano de conclusão (ou previsão de conclusão). |
| `acad:nomeRede` | `acad:RedeAcademica` | `xsd:string` | Obrigatório (`1`) | Nome da plataforma externa (ex.: `LinkedIn`, `ResearchGate`). |
| `acad:urlRede` | `acad:RedeAcademica` | `xsd:anyURI` | Obrigatório (`1`) | Endereço URL do perfil na plataforma externa. |

---

## 3. Relacionamentos (Object Properties)

| Propriedade | Domínio | Alcance | Propriedade Inversa | Regras e Papel Semântico |
| :--- | :--- | :--- | :--- | :--- |
| `acad:lotadoEm` | `acad:Docente` | `acad:Departamento` | `acad:temDocenteLotado` | Todo docente possui ao menos 1 departamento de lotação (`min 1`). |
| `acad:matriculadoEm` | `acad:Discente` | `acad:Curso` | `acad:temDiscenteMatriculado` | Todo discente possui ao menos 1 curso ativo (`min 1`). |
| `acad:parteDeUnidade` | `acad:Departamento` | `acad:UnidadeAcademica` | `acad:possuiDepartamento` | **Funcional:** cada departamento pertence a exatamente 1 unidade acadêmica. |
| `acad:oferecidoPorUnidade` | `acad:Curso` | `acad:UnidadeAcademica` | `acad:ofereceCurso` | **Funcional:** vincula o curso à unidade ofertante (ex.: ICEx). |
| `acad:pertenceAInstituicao` | `acad:OrganizacaoAcademica` | `acad:InstituicaoEnsino` | — | **Funcional:** amarra unidades, departamentos e grupos à instituição mãe. |
| `acad:vinculadoAUnidade` | `acad:Pessoa` | `acad:UnidadeAcademica` | `acad:possuiPessoaVinculada` | Vínculo direto complementar ao caminho estrutural via departamento/curso. |
| `acad:atuaEmArea` | `acad:Docente` | `acad:AreaConhecimento` | — | Áreas principais de pesquisa e atuação científica do docente. |
| `acad:temInteresseEm` | `acad:Pessoa` | `acad:AreaConhecimento` | — | Áreas de interesse declaradas por docentes ou discentes. |
| `acad:leciona` | `acad:Docente` | `acad:Disciplina` | `acad:lecionadaPor` | Disciplinas atribuídas ao docente. |
| `acad:participaDeProjeto` | `acad:Pessoa` | `acad:ProjetoPesquisa` | `acad:temParticipante` | Relaciona docentes e discentes participantes ao mesmo projeto. |
| `acad:coordenadoPor` | `acad:ProjetoPesquisa` | `acad:Docente` | `acad:coordenaProjeto` | Indica o docente responsável pela coordenação (`coordenaProjeto ⊑ participaDeProjeto`). |
| `acad:membroDeGrupo` | `acad:Pessoa` | `acad:GrupoPesquisa` | `acad:temMembroGrupo` | Vínculo com grupos de pesquisa institucionais. |
| `acad:temAutor` | `acad:Publicacao` | `acad:Pessoa` | `acad:autorDe` | Liga uma publicação a todos os seus autores e coautores (`min 1`). |
| `acad:possuiFormacao` | `acad:Pessoa` | `acad:FormacaoAcademica` | — | Associa os registros de titulação acadêmica da pessoa. |
| `acad:realizadaEmInstituicao` | `acad:FormacaoAcademica` | `acad:InstituicaoEnsino` | — | Indica onde a formação foi cursada. |
| `acad:possuiClassificacaoSKOS` | `acad:Pessoa` | `skos:Concept` | — | Liga o perfil aos conceitos controlados da taxonomia facetada (`pes:`). |
| `acad:possuiPerfilRede` | `acad:Pessoa` | `acad:RedeAcademica` | — | Liga o perfil aos links de redes externas. |
