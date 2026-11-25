#!/usr/bin/env python3
"""
Gerador e validador unificado do Portal Semântico de Perfis Acadêmicos (UFRRJ).

Lê `codigo-fonte/dados_perfis.json` e realiza:
1. Geração determinística do grafo RDF/Turtle `ontologia/dados.ttl`;
2. Geração das páginas HTML individuais em `exemplos/perfis/*.html` com JSON-LD e `<link rel="alternate">`;
3. Validação sintática via `rdflib` de `ontologia.owl`, `taxonomia_pessoas.ttl`, `dados.ttl` e de todos os JSON-LD;
4. Execução das 6 consultas SPARQL (`consultas/consulta01.rq` .. `consulta06.rq`) sobre a união dos grafos;
5. Geração do relatório `consultas/resultados/resultados_sparql.md` e do diretório `index.html`.
"""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path
from typing import Any

import rdflib


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_JSON_PATH = ROOT_DIR / "codigo-fonte" / "dados_perfis.json"
ONTOLOGIA_TTL_PATH = ROOT_DIR / "ontologia" / "ontologia.ttl"
ONTOLOGIA_OWL_PATH = ROOT_DIR / "ontologia" / "ontologia.owl"
SKOS_PATH = ROOT_DIR / "ontologia" / "taxonomia_pessoas.ttl"
DADOS_TTL_PATH = ROOT_DIR / "ontologia" / "dados.ttl"
PERFIS_DIR = ROOT_DIR / "exemplos" / "perfis"
CONSULTAS_DIR = ROOT_DIR / "consultas"
RESULTADOS_MD_PATH = CONSULTAS_DIR / "resultados" / "resultados_sparql.md"
INDEX_HTML_PATH = ROOT_DIR / "index.html"
DOCUMENTACAO_HTML_PATH = ROOT_DIR / "documentacao.html"
ARTEFATOS_HTML_PATH = ROOT_DIR / "artefatos.html"
REPO_GITHUB_BASE = "https://github.com/DavidsonWasserman/trabalho-web-semantica/blob/main"


PERGUNTAS_COMPETENCIA = {
    "consulta01.rq": {
        "numero": 1,
        "pergunta": "Quais são os docentes cadastrados e seus respectivos departamentos ou unidades acadêmicas?",
        "explicacao": (
            "Utiliza as classes `acad:Docente`, `acad:Departamento` e `acad:UnidadeAcademica` "
            "conectadas pelas propriedades de objeto `acad:lotadoEm` e `acad:parteDeUnidade`, "
            "além das propriedades de dados `acad:nome`, `acad:cargoOuFuncao`, `acad:nomeOrganizacao` e `acad:sigla`."
        ),
    },
    "consulta02.rq": {
        "numero": 2,
        "pergunta": "Quais discentes pertencem a determinado curso?",
        "explicacao": (
            "Relaciona `acad:Discente` a `acad:Curso` por meio de `acad:matriculadoEm`, "
            "navegando até `acad:UnidadeAcademica` via `acad:oferecidoPorUnidade` e filtrando por "
            "curso (`acad:nomeCurso` contendo 'sistemas de informação')."
        ),
    },
    "consulta03.rq": {
        "numero": 3,
        "pergunta": "Quais docentes atuam em determinada área de pesquisa?",
        "explicacao": (
            "Conecta `acad:Docente` à classe `acad:AreaConhecimento` (subclasse de `skos:Concept`) "
            "via `acad:atuaEmArea`, filtrando pela área 'Dados Abertos' e recuperando as referências "
            "externas LOD (Wikidata e DBpedia) ligadas por `skos:exactMatch`."
        ),
    },
    "consulta04.rq": {
        "numero": 4,
        "pergunta": "Quais docentes e discentes participam de um mesmo projeto de pesquisa?",
        "explicacao": (
            "Consulta multi-entidade que cruza três classes distintas (`acad:ProjetoPesquisa`, "
            "`acad:Docente` e `acad:Discente`) através da propriedade `acad:participaDeProjeto`, "
            "recuperando ainda o curso do discente via `acad:matriculadoEm`."
        ),
    },
    "consulta05.rq": {
        "numero": 5,
        "pergunta": "Quais publicações estão associadas a determinado docente e quem são seus coautores, quando essa informação estiver representada?",
        "explicacao": (
            "Utiliza `acad:Publicacao` e `acad:temAutor` ligando tanto o docente alvo "
            "(Profa. Dra. Ana Exemplo da Silva) quanto os demais autores (`?coautor != ?docente`), "
            "retornando metadados bibliográficos (`acad:tituloPublicacao`, `acad:anoPublicacao`, `acad:doi`) e o papel de cada coautor."
        ),
    },
    "consulta06.rq": {
        "numero": 6,
        "pergunta": "Quais pessoas estão vinculadas a uma unidade acadêmica específica, independentemente de serem docentes ou discentes?",
        "explicacao": (
            "Demonstra Property Paths SPARQL 1.1 (`(acad:lotadoEm/acad:parteDeUnidade)|(acad:matriculadoEm/acad:oferecidoPorUnidade)`) "
            "sobre a superclasse `acad:Pessoa`, unificando docentes e discentes vinculados ao Instituto de Ciências Exatas (ICEx)."
        ),
    },
}


def ttl_str(value: str) -> str:
    """Escapa uma string para literal Turtle com aspas duplas."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def esc(value: Any) -> str:
    """Escapa texto para HTML."""
    return html.escape(str(value), quote=True)


def md_code_to_html(text: str) -> str:
    """Escapa texto para HTML convertendo trechos entre crases em <code>...</code>."""
    parts = text.split("`")
    out: list[str] = []
    for idx, part in enumerate(parts):
        if idx % 2 == 1:
            out.append(f"<code>{esc(part)}</code>")
        else:
            out.append(esc(part))
    return "".join(out)


def generate_dados_ttl(data: dict[str, Any]) -> str:
    """Gera o conteúdo completo de `ontologia/dados.ttl` a partir do JSON estruturado."""
    proj = data["projeto"]
    ns_acad = proj["namespace_ontologia"]
    ns_pes = proj["namespace_skos"]
    ns_dados = proj["namespace_dados"]

    lines: list[str] = [
        f"@prefix acad:    <{ns_acad}> .",
        f"@prefix pes:     <{ns_pes}> .",
        f"@prefix recurso: <{ns_dados}> .",
        "@prefix foaf:    <http://xmlns.com/foaf/0.1/> .",
        "@prefix schema:  <https://schema.org/> .",
        "@prefix bibo:    <http://purl.org/ontology/bibo/> .",
        "@prefix dcterms: <http://purl.org/dc/terms/> .",
        "@prefix skos:    <http://www.w3.org/2004/02/skos/core#> .",
        "@prefix owl:     <http://www.w3.org/2002/07/owl#> .",
        "@prefix rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
        "@prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .",
        "@prefix xsd:     <http://www.w3.org/2001/XMLSchema#> .",
        "",
        "#################################################################",
        "#  Metadados do Conjunto de Dados (Linked Open Data)",
        "#################################################################",
        "",
        f"<{ns_dados[:-1]}>",
        "    a owl:Ontology ;",
        f"    owl:imports <{ns_acad[:-1]}> , <{ns_pes[:-1]}> ;",
        f"    dcterms:title {ttl_str(proj['titulo'])}@pt ;",
        f"    dcterms:description {ttl_str('Grafo RDF de perfis acadêmicos de docentes e discentes da UFRRJ com ligações LOD externas.')}@pt ;",
        f"    dcterms:source {ttl_str(proj['fonte'])}@pt ;",
        f"    dcterms:license <{proj['licenca']}> ;",
        f'    dcterms:modified "{proj["data_atualizacao"]}"^^xsd:date .',
        "",
        "#################################################################",
        "#  Instituições, Unidades Acadêmicas, Departamentos e Cursos",
        "#################################################################",
        "",
    ]

    for inst in data["instituicoes"]:
        lines.append(f"recurso:{inst['id']} a owl:NamedIndividual , acad:InstituicaoEnsino , schema:CollegeOrUniversity ;")
        lines.append(f"    acad:nomeOrganizacao {ttl_str(inst['nome'])} ;")
        lines.append(f"    schema:name {ttl_str(inst['nome'])} ;")
        lines.append(f"    acad:sigla {ttl_str(inst['sigla'])} ;")
        lines.append(f"    schema:url <{inst['url']}> ;")
        if inst.get("same_as"):
            same_list = " , ".join(f"<{u}>" for u in inst["same_as"])
            lines.append(f"    owl:sameAs {same_list} ;")
        if inst.get("see_also"):
            see_list = " , ".join(f"<{u}>" for u in inst["see_also"])
            lines.append(f"    rdfs:seeAlso {see_list} ;")
        lines[-1] = lines[-1].rstrip(" ;") + " ."
        lines.append("")

    for uni in data["unidades_academicas"]:
        lines.append(f"recurso:{uni['id']} a owl:NamedIndividual , acad:UnidadeAcademica ;")
        lines.append(f"    acad:nomeOrganizacao {ttl_str(uni['nome'])} ;")
        lines.append(f"    acad:sigla {ttl_str(uni['sigla'])} ;")
        lines.append(f"    acad:pertenceAInstituicao recurso:{uni['instituicao_id']} ;")
        if uni.get("see_also"):
            see_list = " , ".join(f"<{u}>" for u in uni["see_also"])
            lines.append(f"    rdfs:seeAlso {see_list} ;")
        lines[-1] = lines[-1].rstrip(" ;") + " ."
        lines.append("")

    for dep in data["departamentos"]:
        lines.append(f"recurso:{dep['id']} a owl:NamedIndividual , acad:Departamento ;")
        lines.append(f"    acad:nomeOrganizacao {ttl_str(dep['nome'])} ;")
        lines.append(f"    acad:sigla {ttl_str(dep['sigla'])} ;")
        lines.append(f"    acad:parteDeUnidade recurso:{dep['unidade_id']} ;")
        lines.append(f"    acad:pertenceAInstituicao recurso:{dep['instituicao_id']} ;")
        if dep.get("see_also"):
            see_list = " , ".join(f"<{u}>" for u in dep["see_also"])
            lines.append(f"    rdfs:seeAlso {see_list} ;")
        lines[-1] = lines[-1].rstrip(" ;") + " ."
        lines.append("")

    for curso in data["cursos"]:
        lines.append(f"recurso:{curso['id']} a owl:NamedIndividual , acad:Curso ;")
        lines.append(f"    acad:nomeCurso {ttl_str(curso['nome'])} ;")
        lines.append(f"    acad:modalidadeCurso {ttl_str(curso['modalidade'])} ;")
        lines.append(f"    acad:oferecidoPorUnidade recurso:{curso['unidade_id']} ;")
        if curso.get("close_match"):
            cm_list = " , ".join(f"<{u}>" for u in curso["close_match"])
            lines.append(f"    skos:closeMatch {cm_list} ;")
        lines[-1] = lines[-1].rstrip(" ;") + " ."
        lines.append("")

    lines.extend([
        "#################################################################",
        "#  Áreas de Conhecimento (com links LOD Wikidata / DBpedia)",
        "#################################################################",
        "",
    ])
    for area in data["areas_conhecimento"]:
        lines.append(f"recurso:{area['id']} a owl:NamedIndividual , acad:AreaConhecimento , skos:Concept ;")
        lines.append(f"    acad:nomeArea {ttl_str(area['nome'])} ;")
        lines.append(f"    skos:prefLabel {ttl_str(area['nome'])}@pt ;")
        if area.get("exact_match"):
            em_list = " , ".join(f"<{u}>" for u in area["exact_match"])
            lines.append(f"    skos:exactMatch {em_list} ;")
        lines[-1] = lines[-1].rstrip(" ;") + " ."
        lines.append("")

    lines.extend([
        "#################################################################",
        "#  Disciplinas, Projetos de Pesquisa e Grupos de Pesquisa",
        "#################################################################",
        "",
    ])
    for disc in data["disciplinas"]:
        lines.append(f"recurso:{disc['id']} a owl:NamedIndividual , acad:Disciplina ;")
        lines.append(f"    acad:nomeDisciplina {ttl_str(disc['nome'])} ;")
        lines.append(f"    acad:codigoDisciplina {ttl_str(disc['codigo'])} .")
        lines.append("")

    for prj in data["projetos_pesquisa"]:
        lines.append(f"recurso:{prj['id']} a owl:NamedIndividual , acad:ProjetoPesquisa ;")
        lines.append(f"    acad:tituloProjeto {ttl_str(prj['titulo'])} ;")
        lines.append(f"    acad:descricaoProjeto {ttl_str(prj['descricao'])} ;")
        lines.append(f"    acad:coordenadoPor recurso:{prj['coordenador_id']} ;")
        if prj.get("see_also"):
            see_list = " , ".join(f"<{u}>" for u in prj["see_also"])
            lines.append(f"    rdfs:seeAlso {see_list} ;")
        lines[-1] = lines[-1].rstrip(" ;") + " ."
        lines.append("")

    for grp in data["grupos_pesquisa"]:
        lines.append(f"recurso:{grp['id']} a owl:NamedIndividual , acad:GrupoPesquisa ;")
        lines.append(f"    acad:nomeOrganizacao {ttl_str(grp['nome'])} ;")
        lines.append(f"    acad:pertenceAInstituicao recurso:{grp['instituicao_id']} .")
        lines.append("")

    lines.extend([
        "#################################################################",
        "#  Publicações e Trabalhos Acadêmicos (Coautorias)",
        "#################################################################",
        "",
    ])
    for pub in data["publicacoes"]:
        lines.append(f"recurso:{pub['id']} a owl:NamedIndividual , acad:Publicacao ;")
        lines.append(f"    acad:tituloPublicacao {ttl_str(pub['titulo'])} ;")
        lines.append(f"    acad:citacaoBibliografica {ttl_str(pub['citacao'])} ;")
        lines.append(f"    acad:anoPublicacao {pub['ano']} ;")
        if pub.get("doi"):
            lines.append(f"    acad:doi {ttl_str(pub['doi'])} ;")
            lines.append(f"    bibo:doi {ttl_str(pub['doi'])} ;")
        autores_list = " , ".join(f"recurso:{a}" for a in pub["autores"])
        lines.append(f"    acad:temAutor {autores_list} ;")
        if pub.get("see_also"):
            see_list = " , ".join(f"<{u}>" for u in pub["see_also"])
            lines.append(f"    rdfs:seeAlso {see_list} ;")
        lines[-1] = lines[-1].rstrip(" ;") + " ."
        lines.append("")

    lines.extend([
        "#################################################################",
        "#  Perfis de Docentes e Discentes + Formações + Redes Externas",
        "#################################################################",
        "",
    ])
    for perfil in data["perfis"]:
        # Declara explicitamente classe específica + classe base + acad:Pessoa
        # para compatibilidade com consultas SPARQL com ou sem raciocinador ativo.
        if perfil["tipo_perfil"] == "docente":
            classes = ["owl:NamedIndividual", "acad:Docente", "acad:Pessoa"]
        else:
            classes = ["owl:NamedIndividual", perfil["classe_owl"], "acad:Discente", "acad:Pessoa"]

        lines.append(f"recurso:{perfil['id']} a {' , '.join(classes)} ;")
        lines.append(f"    acad:nome {ttl_str(perfil['nome'])} ;")
        lines.append(f"    foaf:name {ttl_str(perfil['nome'])} ;")
        lines.append(f"    acad:cargoOuFuncao {ttl_str(perfil['cargo'])} ;")
        lines.append(f"    acad:email {ttl_str(perfil['email'])} ;")
        lines.append(f"    foaf:mbox <mailto:{perfil['email']}> ;")
        lines.append(f"    acad:apresentacao {ttl_str(perfil['apresentacao'])} ;")
        lines.append(f'    acad:paginaPessoal "{perfil["pagina_pessoal"]}"^^xsd:anyURI ;')
        lines.append(f'    foaf:homepage <{perfil["pagina_pessoal"]}> ;')
        lines.append(f'    acad:orcid "{perfil["orcid"]}"^^xsd:anyURI ;')
        lines.append(f'    acad:lattes "{perfil["lattes"]}"^^xsd:anyURI ;')
        lines.append(f"    rdfs:seeAlso <{perfil['orcid']}> , <{perfil['lattes']}> ;")
        lines.append(f"    acad:vinculadoAUnidade recurso:{perfil['unidade_id']} ;")

        if perfil["tipo_perfil"] == "docente":
            lines.append(f"    acad:lotadoEm recurso:{perfil['departamento_id']} ;")
            if perfil.get("areas_atuacao"):
                areas_str = " , ".join(f"recurso:{a}" for a in perfil["areas_atuacao"])
                lines.append(f"    acad:atuaEmArea {areas_str} ;")
            if perfil.get("disciplinas"):
                disc_str = " , ".join(f"recurso:{d}" for d in perfil["disciplinas"])
                lines.append(f"    acad:leciona {disc_str} ;")
        else:
            lines.append(f"    acad:matriculadoEm recurso:{perfil['curso_id']} ;")
            lines.append(f"    acad:anoIngresso {perfil['ano_ingresso']} ;")
            lines.append(f"    acad:periodoAtual {ttl_str(perfil['periodo_atual'])} ;")

        if perfil.get("areas_interesse"):
            int_str = " , ".join(f"recurso:{a}" for a in perfil["areas_interesse"])
            lines.append(f"    acad:temInteresseEm {int_str} ;")
        if perfil.get("projetos"):
            prj_str = " , ".join(f"recurso:{p}" for p in perfil["projetos"])
            lines.append(f"    acad:participaDeProjeto {prj_str} ;")
        if perfil.get("grupos"):
            grp_str = " , ".join(f"recurso:{g['grupo_id']}" for g in perfil["grupos"])
            lines.append(f"    acad:membroDeGrupo {grp_str} ;")
        if perfil.get("classificacoes_skos"):
            skos_str = " , ".join(perfil["classificacoes_skos"])
            lines.append(f"    acad:possuiClassificacaoSKOS {skos_str} ;")
        if perfil.get("formacoes"):
            form_str = " , ".join(f"recurso:{f['id']}" for f in perfil["formacoes"])
            lines.append(f"    acad:possuiFormacao {form_str} ;")
        if perfil.get("redes"):
            rede_str = " , ".join(f"recurso:{r['id']}" for r in perfil["redes"])
            lines.append(f"    acad:possuiPerfilRede {rede_str} ;")

        lines[-1] = lines[-1].rstrip(" ;") + " ."
        lines.append("")

        for f in perfil.get("formacoes", []):
            lines.append(f"recurso:{f['id']} a owl:NamedIndividual , acad:FormacaoAcademica ;")
            lines.append(f"    acad:grauFormacao {ttl_str(f['grau'])} ;")
            lines.append(f"    acad:cursoFormacao {ttl_str(f['curso'])} ;")
            lines.append(f"    acad:anoConclusao {f['ano_conclusao']} ;")
            lines.append(f"    acad:descricaoFormacao {ttl_str(f['descricao'])} ;")
            lines.append(f"    acad:realizadaEmInstituicao recurso:{f['instituicao_id']} .")
            lines.append("")

        for r in perfil.get("redes", []):
            lines.append(f"recurso:{r['id']} a owl:NamedIndividual , acad:RedeAcademica ;")
            lines.append(f"    acad:nomeRede {ttl_str(r['nome'])} ;")
            lines.append(f'    acad:urlRede "{r["url"]}"^^xsd:anyURI .')
            lines.append("")

    return "\n".join(lines)


def build_jsonld_for_profile(
    perfil: dict[str, Any],
    data: dict[str, Any],
    lookup: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Monta um bloco JSON-LD Schema.org + acad + pes válido para embutir no HTML do perfil."""
    proj = data["projeto"]
    inst = lookup["instituicoes"][perfil["instituicao_id"]]
    uni = lookup["unidades"][perfil["unidade_id"]]

    knows_about = [
        {
            "@id": f"{proj['namespace_dados']}{aid}",
            "@type": "DefinedTerm",
            "name": lookup["areas"][aid]["nome"],
            "sameAs": lookup["areas"][aid].get("exact_match", []),
        }
        for aid in perfil.get("areas_interesse", [])
    ]

    same_as_links = [
        perfil["orcid"],
        perfil["lattes"],
    ]

    jsonld: dict[str, Any] = {
        "@context": {
            "@vocab": "https://schema.org/",
            "acad": proj["namespace_ontologia"],
            "pes": proj["namespace_skos"],
            "recurso": proj["namespace_dados"],
        },
        "@id": f"{proj['namespace_dados']}{perfil['id']}",
        "@type": ["Person", f"acad:{'Docente' if perfil['tipo_perfil'] == 'docente' else 'Discente'}"],
        "name": perfil["nome"],
        "jobTitle": perfil["cargo"],
        "email": f"mailto:{perfil['email']}",
        "url": perfil["pagina_pessoal"],
        "description": perfil["apresentacao"],
        "sameAs": same_as_links,
        "affiliation": {
            "@id": f"{proj['namespace_dados']}{inst['id']}",
            "@type": "CollegeOrUniversity",
            "name": inst["nome"],
            "alternateName": inst["sigla"],
            "sameAs": inst.get("same_as", []),
        },
        "memberOf": {
            "@id": f"{proj['namespace_dados']}{uni['id']}",
            "@type": "Organization",
            "name": uni["nome"],
        },
        "knowsAbout": knows_about,
        "additionalType": perfil.get("classificacoes_skos", []),
    }

    if perfil["tipo_perfil"] == "docente":
        dep = lookup["departamentos"][perfil["departamento_id"]]
        jsonld["worksFor"] = {
            "@id": f"{proj['namespace_dados']}{dep['id']}",
            "@type": "Organization",
            "name": dep["nome"],
        }
    else:
        curso = lookup["cursos"][perfil["curso_id"]]
        jsonld["hasCredential"] = {
            "@type": "EducationalOccupationalCredential",
            "name": curso["nome"],
        }

    return jsonld


def render_profile_html(
    perfil: dict[str, Any],
    data: dict[str, Any],
    lookup: dict[str, dict[str, Any]],
) -> str:
    """Gera a página HTML individual de um perfil a partir da estrutura do professor."""
    proj = data["projeto"]
    inst = lookup["instituicoes"][perfil["instituicao_id"]]
    uni = lookup["unidades"][perfil["unidade_id"]]
    is_docente = perfil["tipo_perfil"] == "docente"

    jsonld = build_jsonld_for_profile(perfil, data, lookup)
    jsonld_str = json.dumps(jsonld, ensure_ascii=False, indent=2)

    # Navegação superior para os demais perfis e para o diretório
    nav_links = ['<a href="../../index.html">← Diretório de Perfis</a>']
    for p in data["perfis"]:
        active = " (atual)" if p["id"] == perfil["id"] else ""
        nav_links.append(f'<a href="{p["slug"]}.html">{esc(p["nome"].split(" ")[0])} {esc(p["nome"].split(" ")[-1])}{active}</a>')
    nav_links.append('<a href="../../documentacao.html">Documentação &amp; Diagrama</a>')
    nav_links.append('<a href="../../artefatos.html">Ontologia, RDF &amp; SPARQL</a>')

    # Formação acadêmica
    formacoes_html = "\n".join(
        f"<li><strong>{esc(f['grau'])} em {esc(f['curso'])}</strong> — {esc(f['instituicao_nome'])} ({esc(f['ano_conclusao'])}).</li>"
        if is_docente
        else f"<li><strong>{esc(f['curso'])}</strong> — {esc(f['instituicao_nome'])}.</li><li>Ingresso: {esc(perfil['ano_ingresso'])} · Período atual: {esc(perfil['periodo_atual'])}.</li>"
        for f in perfil.get("formacoes", [])
    )

    # Áreas com links LOD para Wikidata quando disponível
    areas_ids = perfil.get("areas_atuacao", []) if is_docente else perfil.get("areas_interesse", [])
    areas_items: list[str] = []
    for aid in areas_ids:
        area = lookup["areas"][aid]
        ext = area.get("exact_match", [])
        if ext:
            areas_items.append(
                f'<li><a href="{esc(ext[0])}" target="_blank" rel="noopener noreferrer" title="Recurso ligado na Wikidata (skos:exactMatch)">{esc(area["nome"])} ↗</a></li>'
            )
        else:
            areas_items.append(f"<li>{esc(area['nome'])}</li>")
    areas_html = "\n".join(areas_items)

    # Disciplinas (somente docente)
    disciplinas_section = ""
    if is_docente:
        disc_items = "\n".join(
            f"<li>{esc(lookup['disciplinas'][did]['nome'])} ({esc(lookup['disciplinas'][did]['codigo'])})</li>"
            for did in perfil.get("disciplinas", [])
        )
        disciplinas_section = (
            '<section class="card"><h2>Disciplinas</h2>'
            f'<ul class="clean-list">{disc_items}</ul></section>'
        )

    # Projetos e grupos de pesquisa
    projetos_items: list[str] = []
    for pid in perfil.get("projetos", []):
        pr = lookup["projetos"][pid]
        projetos_items.append(
            f"<li><strong>{esc(pr['titulo'])}</strong> — {esc(pr['descricao'])}</li>"
        )
    for g in perfil.get("grupos", []):
        grp = lookup["grupos"][g["grupo_id"]]
        projetos_items.append(
            f"<li><strong>{esc(grp['nome'])}</strong> — {esc(g['papel'])}.</li>"
        )
    for ativ in perfil.get("atividades_extra", []):
        projetos_items.append(f"<li>{esc(ativ)}</li>")
    projetos_html = "\n".join(projetos_items)

    # Publicações onde o perfil é autor + links para coautores
    pubs_perfil = [
        pub for pub in data["publicacoes"] if perfil["id"] in pub.get("autores", [])
    ]
    pub_items: list[str] = []
    for pub in pubs_perfil:
        coautores_links = []
        for aid in pub["autores"]:
            if aid != perfil["id"]:
                coautor = lookup["perfis"][aid]
                coautores_links.append(
                    f'<a href="{esc(coautor["slug"])}.html">{esc(coautor["nome"])}</a>'
                )
        coautor_txt = (
            f"<br><small>Coautores: {', '.join(coautores_links)}</small>"
            if coautores_links
            else ""
        )
        doi_txt = f" · DOI: <code>{esc(pub['doi'])}</code>" if pub.get("doi") else ""
        pub_items.append(f"<li>{esc(pub['citacao'])}{doi_txt}{coautor_txt}</li>")
    pubs_html = "\n".join(pub_items) if pub_items else "<li>Nenhuma publicação cadastrada.</li>"

    # Vínculo institucional
    if is_docente:
        dep = lookup["departamentos"][perfil["departamento_id"]]
        dep_ou_curso_label = "Departamento"
        dep_ou_curso_val = dep["nome"]
    else:
        curso = lookup["cursos"][perfil["curso_id"]]
        dep_ou_curso_label = "Curso"
        dep_ou_curso_val = curso["nome"]

    # Classificações SKOS
    skos_tags = "\n".join(
        f"<li><code>{esc(s)}</code></li>" for s in perfil.get("classificacoes_skos", [])
    )

    # Redes externas
    redes_html = "\n".join(
        f'<li><a href="{esc(r["url"])}" rel="me" target="_blank" rel="noopener noreferrer">{esc(r["nome"])}</a></li>'
        for r in perfil.get("redes", [])
    )

    recurso_uri = f"{proj['namespace_dados']}{perfil['id']}"
    eyebrow_label = "Perfil de docente" if is_docente else "Perfil de discente"
    areas_title = "Áreas de atuação e interesses" if is_docente else "Áreas de interesse"
    proj_title = "Projetos e grupos de pesquisa" if is_docente else "Projetos, grupos e atividades"
    pubs_title = "Publicações selecionadas" if is_docente else "Produções e trabalhos"
    list_tag = "ol" if is_docente else "ul"

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Perfil acadêmico semântico de {esc(perfil['nome'])} — {esc(inst['sigla'])}.">
  <title>{esc(perfil['nome'])} | {esc(inst['sigla'])}</title>
  <link rel="stylesheet" href="../../estilos.css">
  <link rel="alternate" type="text/turtle" href="../../ontologia/dados.ttl" title="Dados RDF (Turtle)">
  <script type="application/ld+json">
{jsonld_str}
  </script>
</head>
<body>
  <header class="site-header">
    <div class="header-inner">
      <a href="../../index.html" class="site-title">{esc(inst['nome'])} ({esc(inst['sigla'])})</a>
      <p class="site-subtitle">Diretório Semântico de Perfis Acadêmicos · {esc(uni['nome'])} ({esc(uni['sigla'])})</p>
      <nav class="top-nav" aria-label="Navegação entre perfis">
        {' '.join(nav_links)}
      </nav>
    </div>
  </header>

  <main>
    <section class="profile-heading" aria-labelledby="nome">
      <img class="profile-photo" src="../../foto-exemplo.svg" alt="Avatar ilustrativo de {esc(perfil['nome'])}">
      <div>
        <p class="eyebrow">{eyebrow_label}</p>
        <h1 id="nome">{esc(perfil['nome'])}</h1>
        <p class="role">{esc(perfil['cargo'])}</p>
        <p class="quick-info">{esc(perfil['resumo_topo'])}</p>
      </div>
    </section>

    <div class="layout">
      <div>
        <section class="card">
          <h2>Apresentação</h2>
          <p>{esc(perfil['apresentacao'])}</p>
        </section>

        <section class="card">
          <h2>Formação acadêmica</h2>
          <ul class="clean-list">
            {formacoes_html}
          </ul>
        </section>

        <section class="card">
          <h2>{areas_title}</h2>
          <ul class="tag-list">
            {areas_html}
          </ul>
          <p class="note">Links marcados com ↗ apontam para conceitos equivalentes na Wikidata (<code>skos:exactMatch</code>).</p>
        </section>

        {disciplinas_section}

        <section class="card">
          <h2>{proj_title}</h2>
          <ul class="clean-list">
            {projetos_html}
          </ul>
        </section>

        <section class="card">
          <h2>{pubs_title}</h2>
          <{list_tag} class="clean-list">
            {pubs_html}
          </{list_tag}>
        </section>
      </div>

      <aside>
        <section class="card">
          <h2>Vínculo institucional</h2>
          <dl class="contact-list">
            <div><dt>Instituição</dt><dd><a href="{esc(inst['same_as'][0])}" target="_blank" rel="noopener noreferrer">{esc(inst['sigla'])} — {esc(inst['nome'])}</a></dd></div>
            <div><dt>Unidade</dt><dd>{esc(uni['nome'])} ({esc(uni['sigla'])})</dd></div>
            <div><dt>{dep_ou_curso_label}</dt><dd>{esc(dep_ou_curso_val)}</dd></div>
            <div><dt>E-mail</dt><dd><a href="mailto:{esc(perfil['email'])}">{esc(perfil['email'])}</a></dd></div>
          </dl>
        </section>

        <section class="card">
          <h2>Metadados Semânticos &amp; LOD</h2>
          <p class="note">URI do recurso no grafo RDF:</p>
          <p class="lod-uri">{esc(recurso_uri)}</p>
          <p class="note">Classificação SKOS (<code>pes:</code>):</p>
          <ul class="tag-list">
            {skos_tags}
          </ul>
          <p class="note" style="margin-top:.75rem;">
            <a href="../../ontologia/dados.ttl">Baixar dados.ttl</a> ·
            <a href="../../ontologia/ontologia.ttl">Ontologia (Turtle)</a> ·
            <a href="../../ontologia/ontologia.owl">Ontologia (RDF/XML)</a>
          </p>
        </section>

        <section class="card">
          <h2>Redes e perfis acadêmicos</h2>
          <ul class="social-links">
            {redes_html}
          </ul>
          <p class="note">Identificadores acadêmicos conectados via <code>rdfs:seeAlso</code> e <code>schema:sameAs</code>.</p>
        </section>
      </aside>
    </div>
  </main>

  <footer class="site-footer">
    Perfil gerado automaticamente a partir de <code>codigo-fonte/dados_perfis.json</code> e alinhado à ontologia OWL/RDF do projeto · Licença: <a href="{esc(proj['licenca'])}" target="_blank" rel="noopener noreferrer">{esc(proj['licenca_nome'])}</a> · Atualizado em {esc(proj['data_atualizacao'])}.
  </footer>
</body>
</html>
"""


def run_sparql_queries(graph: rdflib.Graph) -> list[dict[str, Any]]:
    """Executa as 6 consultas SPARQL de `consultas/consulta01.rq`..`consulta06.rq`."""
    results: list[dict[str, Any]] = []
    for filename, meta in sorted(PERGUNTAS_COMPETENCIA.items()):
        rq_path = CONSULTAS_DIR / filename
        query_text = rq_path.read_text(encoding="utf-8")
        qres = graph.query(query_text)
        vars_list = [str(v) for v in qres.vars]
        rows: list[list[str]] = []
        for row in qres:
            formatted_row: list[str] = []
            for cell in row:
                if cell is None:
                    formatted_row.append("-")
                elif isinstance(cell, rdflib.URIRef):
                    formatted_row.append(str(cell))
                else:
                    formatted_row.append(str(cell))
            rows.append(formatted_row)
        results.append({
            "arquivo": filename,
            "numero": meta["numero"],
            "pergunta": meta["pergunta"],
            "explicacao": meta["explicacao"],
            "sparql": query_text.strip(),
            "vars": vars_list,
            "rows": rows,
        })
    return results


def compact_uri(val: str, proj: dict[str, Any]) -> str:
    """Abrevia prefixos longos para exibição legível nas tabelas Markdown e HTML."""
    replacements = [
        (proj["namespace_dados"], "recurso:"),
        (proj["namespace_ontologia"], "acad:"),
        (proj["namespace_skos"], "pes:"),
        ("http://www.wikidata.org/entity/", "wd:"),
        ("http://dbpedia.org/resource/", "dbr:"),
    ]
    for full, prefix in replacements:
        if val.startswith(full):
            return val.replace(full, prefix, 1)
    return val


def generate_resultados_md(sparql_results: list[dict[str, Any]], proj: dict[str, Any]) -> str:
    """Gera `consultas/resultados/resultados_sparql.md` com as 6 perguntas, queries e tabelas."""
    lines: list[str] = [
        "# Resultados das Consultas SPARQL (Perguntas de Competência)",
        "",
        "Este documento foi gerado automaticamente por `codigo-fonte/build.py` utilizando `rdflib` sobre a união dos grafos:",
        "- `ontologia/ontologia.ttl` (e sua contraparte RDF/XML em `ontologia/ontologia.owl`)",
        "- `ontologia/taxonomia_pessoas.ttl`",
        "- `ontologia/dados.ttl`",
        "",
        f"**Data da última execução:** {proj['data_atualizacao']}",
        "",
        "---",
        "",
    ]

    for item in sparql_results:
        lines.append(f"## {item['numero']}. {item['pergunta']}")
        lines.append("")
        lines.append(f"**Arquivo:** `consultas/{item['arquivo']}`")
        lines.append("")
        lines.append(f"**Classes e propriedades utilizadas:** {item['explicacao']}")
        lines.append("")
        lines.append("### Consulta SPARQL")
        lines.append("```sparql")
        lines.append(item["sparql"])
        lines.append("```")
        lines.append("")
        lines.append(f"### Resultado obtido ({len(item['rows'])} registro(s))")
        lines.append("")
        if item["rows"]:
            header = "| " + " | ".join(f"`{v}`" for v in item["vars"]) + " |"
            sep = "| " + " | ".join("---" for _ in item["vars"]) + " |"
            lines.append(header)
            lines.append(sep)
            for row in item["rows"]:
                cells = [compact_uri(c, proj).replace("|", "\\|") for c in row]
                lines.append("| " + " | ".join(cells) + " |")
        else:
            lines.append("*Nenhum resultado retornado.*")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def render_site_header(proj: dict[str, Any], active_page: str) -> str:
    """Renderiza o cabeçalho padrão das páginas principais do portal."""
    nav_items = [
        ("index.html", "Diretório de Perfis"),
        ("documentacao.html", "Documentação &amp; Diagrama"),
        ("artefatos.html", "Ontologia, RDF &amp; SPARQL"),
    ]
    nav_html = " ".join(
        f'<a href="{href}">{label}{" (atual)" if href == active_page else ""}</a>'
        for href, label in nav_items
    )
    return f"""  <header class="site-header">
    <div class="header-inner">
      <a href="index.html" class="site-title">{esc(proj['titulo'])}</a>
      <p class="site-subtitle">{esc(proj['subtitulo'])}</p>
      <nav class="top-nav" aria-label="Navegação principal">
        {nav_html}
        <a href="ontologia/dados.ttl">Dados RDF (bruto)</a>
        <a href="ontologia/ontologia.ttl">Ontologia (bruto)</a>
      </nav>
    </div>
  </header>"""


def render_documentacao_html(data: dict[str, Any]) -> str:
    """Gera `documentacao.html` na raiz com diagrama, vocabulários, dicionário e decisões."""
    proj = data["projeto"]
    header = render_site_header(proj, "documentacao.html")
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Documentação da Ontologia, Vocabulários e Decisões de Modelagem — {esc(proj['titulo'])}.">
  <title>Documentação &amp; Diagrama | {esc(proj['titulo'])}</title>
  <link rel="stylesheet" href="estilos.css">
</head>
<body>
{header}

  <main>
    <section class="card">
      <p class="eyebrow">Documentação Técnica e Modelagem Semântica</p>
      <h1>Diagrama, Ontologia e Vocabulários</h1>
      <p>
        Esta página reúne de forma visual a arquitetura semântica do portal. Os arquivos originais em Markdown também estão disponíveis no repositório GitHub para consulta detalhada.
      </p>
      <p>
        <a class="btn-outline" href="{REPO_GITHUB_BASE}/proposta/descricao.md" target="_blank" rel="noopener noreferrer">Proposta (descricao.md) ↗</a>
        <a class="btn-outline" href="{REPO_GITHUB_BASE}/proposta/decisoes-modelagem.md" target="_blank" rel="noopener noreferrer">Decisões e IA (decisoes-modelagem.md) ↗</a>
        <a class="btn-outline" href="{REPO_GITHUB_BASE}/documentacao/dicionario-dados.md" target="_blank" rel="noopener noreferrer">Dicionário de Dados ↗</a>
        <a class="btn-outline" href="{REPO_GITHUB_BASE}/documentacao/vocabularios.md" target="_blank" rel="noopener noreferrer">Vocabulários ↗</a>
        <a class="btn-outline" href="{REPO_GITHUB_BASE}/documentacao/ontologia.md" target="_blank" rel="noopener noreferrer">Ontologia (ontologia.md) ↗</a>
      </p>
    </section>

    <section class="card">
      <h2>1. Diagrama Conceitual e da Ontologia (<code>acad:</code>)</h2>
      <p class="note">Triângulos vazados indicam herança (<code>rdfs:subClassOf</code>); setas sólidas indicam propriedades de objeto (<code>owl:ObjectProperty</code>).</p>
      <div class="diagram-wrap">
        <img src="documentacao/diagrama.svg" alt="Diagrama da Ontologia de Perfis Acadêmicos (acad:)">
      </div>
    </section>

    <section class="card">
      <h2>2. Vocabulários Reutilizados e Taxonomia SKOS (<code>pes:</code>)</h2>
      <div style="overflow-x:auto;">
        <table class="data-table">
          <thead>
            <tr><th>Vocabulário</th><th>Prefixo</th><th>Uso e Alinhamento no Projeto</th></tr>
          </thead>
          <tbody>
            <tr><td><strong>FOAF</strong></td><td><code>foaf:</code></td><td>Base de agentes, organizações e projetos (<code>acad:Pessoa ⊑ foaf:Person</code>, <code>acad:nome ⊑ foaf:name</code>, <code>foaf:mbox</code>).</td></tr>
            <tr><td><strong>Schema.org</strong></td><td><code>schema:</code></td><td>Interoperabilidade web e JSON-LD embutido nas páginas (<code>Person</code>, <code>CollegeOrUniversity</code>, <code>ScholarlyArticle</code>, <code>knowsAbout</code>).</td></tr>
            <tr><td><strong>W3C SKOS</strong></td><td><code>skos:</code></td><td>Taxonomia facetada de pessoas (<code>pes:Vinculo</code>, <code>pes:Atuacao</code>, <code>pes:Condicao</code>) e ligação de áreas via <code>skos:exactMatch</code> / <code>skos:closeMatch</code>.</td></tr>
            <tr><td><strong>BIBO</strong></td><td><code>bibo:</code></td><td>Alinhamento bibliográfico (<code>acad:Publicacao ⊑ bibo:AcademicArticle</code>, <code>bibo:doi</code>).</td></tr>
            <tr><td><strong>DC Terms</strong></td><td><code>dcterms:</code></td><td>Metadados de proveniência, fonte, data de atualização e licença (CC BY 4.0).</td></tr>
            <tr><td><strong>VIVO (Referência)</strong></td><td><code>vivo:</code></td><td>Referência conceitual analisada na pesquisa; optamos por ontologia de aplicação própria mais enxuta em vez de importar o núcleo BFO/IAO completo.</td></tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="card">
      <h2>3. Decisões Críticas de Modelagem e Política LOD</h2>
      <ul class="clean-list">
        <li><strong>Hash URIs no GitHub Pages:</strong> Como o GitHub Pages é estático (sem HTTP 303), usamos Hash URIs apontando para os documentos publicados (<code>.../ontologia/dados.ttl#Recurso</code>) com <code>&lt;link rel="alternate" type="text/turtle"&gt;</code> no HTML.</li>
        <li><strong>Política criteriosa para <code>owl:sameAs</code>:</strong> <code>owl:sameAs</code> é usado exclusivamente para identidade estrita na <code>recurso:UFRRJ</code> (Wikidata <code>Q7834196</code> e DBpedia). Áreas usam <code>skos:exactMatch</code>, cursos usam <code>skos:closeMatch</code> e perfis demonstrativos usam <code>rdfs:seeAlso</code> para ORCID/Lattes/OpenAlex.</li>
        <li><strong>Não-disjunção entre Docente e Discente:</strong> <code>acad:Docente</code> e <code>acad:Discente</code> não foram declaradas disjuntas porque um docente pode estar matriculado em curso de pós-graduação.</li>
        <li><strong>Compatibilidade com Protégé / HermiT:</strong> Restrições de cardinalidade OWL utilizam <code>xsd:integer</code> (em vez de <code>xsd:gYear</code>) para evitar erros no raciocinador HermiT.</li>
        <li><strong>Classes Definidas (Inferência OWL):</strong> <code>acad:PesquisadorEmProjeto</code> e <code>acad:AutorAcademico</code> são inferidas automaticamente via <code>owl:equivalentClass</code>.</li>
      </ul>
    </section>

    <section class="card">
      <h2>4. Dicionário Resumido de Classes e Principais Propriedades</h2>
      <div style="overflow-x:auto;">
        <table class="data-table">
          <thead>
            <tr><th>Classe / Propriedade</th><th>Domínio → Alcance / Restrição</th><th>Descrição</th></tr>
          </thead>
          <tbody>
            <tr><td><code>acad:Docente</code></td><td><code>lotadoEm min 1 Departamento</code></td><td>Professor/pesquisador vinculado a departamento acadêmico.</td></tr>
            <tr><td><code>acad:Discente</code></td><td><code>matriculadoEm min 1 Curso</code></td><td>Estudante matriculado em graduação ou pós-graduação.</td></tr>
            <tr><td><code>acad:Publicacao</code></td><td><code>temAutor min 1 Pessoa</code>; <code>titulo</code> e <code>ano</code> (<code>1</code>)</td><td>Artigo/produção acadêmica permitindo consulta de coautorias.</td></tr>
            <tr><td><code>acad:lotadoEm</code> / <code>acad:parteDeUnidade</code></td><td><code>Docente → Departamento → UnidadeAcademica</code></td><td>Hierarquia institucional docente até o ICEx.</td></tr>
            <tr><td><code>acad:matriculadoEm</code> / <code>acad:oferecidoPorUnidade</code></td><td><code>Discente → Curso → UnidadeAcademica</code></td><td>Hierarquia institucional discente até o ICEx.</td></tr>
            <tr><td><code>acad:participaDeProjeto</code></td><td><code>Pessoa → ProjetoPesquisa</code></td><td>Liga docentes e discentes a projetos de pesquisa em comum.</td></tr>
            <tr><td><code>acad:possuiClassificacaoSKOS</code></td><td><code>Pessoa → skos:Concept</code></td><td>Associa o perfil aos conceitos facetados de <code>pes:</code>.</td></tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>

  <footer class="site-footer">
    Trabalho de Web Semântica e Linked Open Data — Departamento de Computação / ICEx / UFRRJ · Atualizado em {esc(proj['data_atualizacao'])}.
  </footer>
</body>
</html>
"""


def render_artefatos_html(data: dict[str, Any], sparql_results: list[dict[str, Any]]) -> str:
    """Gera `artefatos.html` exibindo ontologia, SKOS, dados RDF e queries SPARQL formatados."""
    proj = data["projeto"]
    header = render_site_header(proj, "artefatos.html")

    ont_ttl_txt = ONTOLOGIA_TTL_PATH.read_text(encoding="utf-8")
    ont_owl_txt = ONTOLOGIA_OWL_PATH.read_text(encoding="utf-8")
    skos_txt = SKOS_PATH.read_text(encoding="utf-8")
    dados_ttl_txt = DADOS_TTL_PATH.read_text(encoding="utf-8")

    sparql_sections: list[str] = []
    for item in sparql_results:
        headers = "".join(f"<th>{esc(v)}</th>" for v in item["vars"])
        body_rows = ""
        for r in item["rows"]:
            tds = "".join(f"<td><code>{esc(compact_uri(c, proj))}</code></td>" for c in r)
            body_rows += f"<tr>{tds}</tr>"
        sparql_sections.append(f"""
        <div class="sparql-item">
          <h3>{item['numero']}. {esc(item['pergunta'])}</h3>
          <p class="note">{md_code_to_html(item['explicacao'])}</p>
          <p>
            <a class="btn-outline" href="consultas/{esc(item['arquivo'])}">Arquivo bruto ({esc(item['arquivo'])})</a>
            <a class="btn-outline" href="{REPO_GITHUB_BASE}/consultas/{esc(item['arquivo'])}" target="_blank" rel="noopener noreferrer">Ver no GitHub ↗</a>
          </p>
          <pre class="code-box">{esc(item['sparql'])}</pre>
          <p class="note"><strong>Resultado obtido ({len(item['rows'])} registro(s)):</strong></p>
          <div style="overflow-x:auto;">
            <table class="data-table">
              <thead><tr>{headers}</tr></thead>
              <tbody>{body_rows}</tbody>
            </table>
          </div>
        </div>
        """)

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Visualizador de Ontologia OWL/Turtle, Taxonomia SKOS, Dados RDF e Consultas SPARQL — {esc(proj['titulo'])}.">
  <title>Ontologia, RDF &amp; SPARQL | {esc(proj['titulo'])}</title>
  <link rel="stylesheet" href="estilos.css">
</head>
<body>
{header}

  <main>
    <section class="card">
      <p class="eyebrow">Artefatos Legíveis por Máquina &amp; Evidências SPARQL</p>
      <h1>Ontologia OWL, SKOS, Dados RDF e Consultas</h1>
      <p>
        Arquivos <code>.ttl</code> e <code>.owl</code> são serializações formais de grafos semânticos (texto/XML). Abaixo você pode inspecionar o conteúdo completo diretamente no navegador com formatação legível ou acessar os arquivos originais para uso em ferramentas como Protégé e <code>rdflib</code>.
      </p>
      <p>
        <a class="btn-outline" href="#ontologia-ttl">Ontologia (Turtle)</a>
        <a class="btn-outline" href="#ontologia-owl">Ontologia (RDF/XML)</a>
        <a class="btn-outline" href="#skos-ttl">Taxonomia SKOS</a>
        <a class="btn-outline" href="#dados-ttl">Dados RDF</a>
        <a class="btn-outline" href="#consultas-sparql">6 Consultas SPARQL</a>
      </p>
    </section>

    <section class="card" id="ontologia-ttl">
      <h2>1. Ontologia de Aplicação — Serialização Turtle (<code>ontologia/ontologia.ttl</code>)</h2>
      <p>
        <a class="btn-outline" href="ontologia/ontologia.ttl">Abrir arquivo bruto (.ttl)</a>
        <a class="btn-outline" href="{REPO_GITHUB_BASE}/ontologia/ontologia.ttl" target="_blank" rel="noopener noreferrer">Ver no GitHub ↗</a>
      </p>
      <pre class="code-box">{esc(ont_ttl_txt)}</pre>
    </section>

    <section class="card" id="ontologia-owl">
      <h2>2. Ontologia de Aplicação — Serialização RDF/XML (<code>ontologia/ontologia.owl</code>)</h2>
      <p class="note">Gerado automaticamente a partir de <code>ontologia.ttl</code> em formato RDF/XML padrão.</p>
      <p>
        <a class="btn-outline" href="ontologia/ontologia.owl">Abrir arquivo bruto (.owl)</a>
        <a class="btn-outline" href="{REPO_GITHUB_BASE}/ontologia/ontologia.owl" target="_blank" rel="noopener noreferrer">Ver no GitHub ↗</a>
      </p>
      <pre class="code-box">{esc(ont_owl_txt)}</pre>
    </section>

    <section class="card" id="skos-ttl">
      <h2>3. Taxonomia Facetada e Vocabulário Controlado SKOS (<code>ontologia/taxonomia_pessoas.ttl</code>)</h2>
      <p>
        <a class="btn-outline" href="ontologia/taxonomia_pessoas.ttl">Abrir arquivo bruto (.ttl)</a>
        <a class="btn-outline" href="{REPO_GITHUB_BASE}/ontologia/taxonomia_pessoas.ttl" target="_blank" rel="noopener noreferrer">Ver no GitHub ↗</a>
      </p>
      <pre class="code-box">{esc(skos_txt)}</pre>
    </section>

    <section class="card" id="dados-ttl">
      <h2>4. Grafo de Dados dos Perfis e Links LOD (<code>ontologia/dados.ttl</code>)</h2>
      <p>
        <a class="btn-outline" href="ontologia/dados.ttl">Abrir arquivo bruto (.ttl)</a>
        <a class="btn-outline" href="{REPO_GITHUB_BASE}/ontologia/dados.ttl" target="_blank" rel="noopener noreferrer">Ver no GitHub ↗</a>
      </p>
      <pre class="code-box">{esc(dados_ttl_txt)}</pre>
    </section>

    <section class="card" id="consultas-sparql">
      <h2>5. As 6 Consultas SPARQL e Resultados Validados</h2>
      <p>
        <a class="btn-outline" href="{REPO_GITHUB_BASE}/consultas/resultados/resultados_sparql.md" target="_blank" rel="noopener noreferrer">Ver relatório Markdown no GitHub ↗</a>
      </p>
      {''.join(sparql_sections)}
    </section>
  </main>

  <footer class="site-footer">
    Trabalho de Web Semântica e Linked Open Data — Departamento de Computação / ICEx / UFRRJ · Atualizado em {esc(proj['data_atualizacao'])}.
  </footer>
</body>
</html>
"""


def render_index_html(
    data: dict[str, Any],
    sparql_results: list[dict[str, Any]],
    triples_count: int,
) -> str:
    """Gera o `index.html` público na raiz do repositório."""
    proj = data["projeto"]
    header = render_site_header(proj, "index.html")

    docentes_cards: list[str] = []
    discentes_cards: list[str] = []
    for p in data["perfis"]:
        card = f"""
        <article class="profile-card">
          <div>
            <p class="eyebrow">{'Docente' if p['tipo_perfil'] == 'docente' else 'Discente'}</p>
            <h3>{esc(p['nome'])}</h3>
            <p class="role">{esc(p['cargo'])}</p>
            <p class="note">{esc(p['resumo_topo'])}</p>
            <p class="lod-uri">{esc(proj['namespace_dados'])}{esc(p['id'])}</p>
          </div>
          <div>
            <a class="btn" href="exemplos/perfis/{esc(p['slug'])}.html">Abrir perfil semântico</a>
          </div>
        </article>
        """
        if p["tipo_perfil"] == "docente":
            docentes_cards.append(card)
        else:
            discentes_cards.append(card)

    sparql_blocks: list[str] = []
    for item in sparql_results:
        headers = "".join(f"<th>{esc(v)}</th>" for v in item["vars"])
        body_rows = ""
        for r in item["rows"]:
            tds = "".join(f"<td><code>{esc(compact_uri(c, proj))}</code></td>" for c in r)
            body_rows += f"<tr>{tds}</tr>"
        sparql_blocks.append(f"""
        <div class="sparql-item">
          <p><strong>{item['numero']}. {esc(item['pergunta'])}</strong> (<a href="artefatos.html#consultas-sparql">ver query completa</a> · <a href="consultas/{esc(item['arquivo'])}">{esc(item['arquivo'])}</a> — {len(item['rows'])} resultado(s))</p>
          <p class="note">{md_code_to_html(item['explicacao'])}</p>
          <div style="overflow-x:auto;">
            <table class="data-table">
              <thead><tr>{headers}</tr></thead>
              <tbody>{body_rows}</tbody>
            </table>
          </div>
        </div>
        """)

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{esc(proj['titulo'])} — Trabalho de Web Semântica e Linked Open Data (UFRRJ).">
  <title>{esc(proj['titulo'])}</title>
  <link rel="stylesheet" href="estilos.css">
  <link rel="alternate" type="text/turtle" href="ontologia/dados.ttl" title="Dados RDF (Turtle)">
</head>
<body>
{header}

  <main>
    <section class="card">
      <p class="eyebrow">Web Semântica e Linked Open Data · UFRRJ</p>
      <h1>Perfis Acadêmicos Conectados</h1>
      <p>
        Portal demonstrativo construído a partir de fonte de dados estruturada única (<code>codigo-fonte/dados_perfis.json</code>),
        com ontologia própria em <strong>OWL 2</strong> (<code>acad:</code>), vocabulário controlado em <strong>W3C SKOS</strong> (<code>pes:</code>),
        serialização <strong>RDF/Turtle</strong>, JSON-LD embutido nas páginas e ligações com <strong>Wikidata</strong>, <strong>DBpedia</strong>, <strong>ORCID</strong> e <strong>Lattes</strong>.
      </p>
      <p class="note">
        Total no grafo unificado validado com <code>rdflib</code>: <strong>{triples_count} triplas RDF</strong> ·
        Licença: <a href="{esc(proj['licenca'])}" target="_blank" rel="noopener noreferrer">{esc(proj['licenca_nome'])}</a> ·
        Atualizado em {esc(proj['data_atualizacao'])}.
      </p>
      <p>
        <a class="btn-outline" href="documentacao.html">Ver Diagrama &amp; Documentação</a>
        <a class="btn-outline" href="artefatos.html">Inspecionar Ontologia, RDF &amp; SPARQL</a>
      </p>
    </section>

    <section class="card">
      <h2>Perfis de Docentes</h2>
      <div class="grid-cards">
        {''.join(docentes_cards)}
      </div>
    </section>

    <section class="card">
      <h2>Perfis de Discentes</h2>
      <div class="grid-cards">
        {''.join(discentes_cards)}
      </div>
    </section>

    <section class="card">
      <h2>Artefatos Semânticos e Linked Open Data</h2>
      <ul class="clean-list">
        <li><strong>Visualizador de Artefatos (Código Formatado):</strong> <a href="artefatos.html"><code>artefatos.html</code></a> · <a href="documentacao.html"><code>documentacao.html</code></a></li>
        <li><strong>Ontologia de Aplicação (OWL 2):</strong> <a href="ontologia/ontologia.ttl"><code>ontologia/ontologia.ttl</code> (Turtle)</a> · <a href="ontologia/ontologia.owl"><code>ontologia/ontologia.owl</code> (RDF/XML)</a></li>
        <li><strong>Taxonomia Facetada e Vocabulário Controlado (SKOS):</strong> <a href="ontologia/taxonomia_pessoas.ttl"><code>ontologia/taxonomia_pessoas.ttl</code></a></li>
        <li><strong>Grafo de Dados e Perfis (RDF / Turtle):</strong> <a href="ontologia/dados.ttl"><code>ontologia/dados.ttl</code></a></li>
        <li><strong>Consultas SPARQL (Perguntas de Competência 01 a 06):</strong> <a href="artefatos.html#consultas-sparql">Ver queries e resultados</a> · <a href="{REPO_GITHUB_BASE}/consultas/resultados/resultados_sparql.md" target="_blank" rel="noopener noreferrer">Markdown no GitHub ↗</a></li>
        <li><strong>Links Externos LOD:</strong> UFRRJ (<a href="http://www.wikidata.org/entity/Q7834196" target="_blank" rel="noopener noreferrer">Wikidata Q7834196</a>, <a href="http://dbpedia.org/resource/Federal_Rural_University_of_Rio_de_Janeiro" target="_blank" rel="noopener noreferrer">DBpedia</a>), áreas de conhecimento via <code>skos:exactMatch</code> e ORCID/Lattes.</li>
      </ul>
    </section>

    <section class="card">
      <h2>Perguntas de Competência Executadas via SPARQL</h2>
      <p class="note">Resultados gerados em tempo de build pelo script <code>codigo-fonte/build.py</code> diretamente sobre os arquivos OWL/RDF do repositório.</p>
      {''.join(sparql_blocks)}
    </section>
  </main>

  <footer class="site-footer">
    Trabalho de Web Semântica e Linked Open Data — Departamento de Computação / ICEx / UFRRJ.
  </footer>
</body>
</html>
"""


def main() -> int:
    data = json.loads(DATA_JSON_PATH.read_text(encoding="utf-8"))
    proj = data["projeto"]

    lookup = {
        "instituicoes": {i["id"]: i for i in data["instituicoes"]},
        "unidades": {u["id"]: u for u in data["unidades_academicas"]},
        "departamentos": {d["id"]: d for d in data["departamentos"]},
        "cursos": {c["id"]: c for c in data["cursos"]},
        "areas": {a["id"]: a for a in data["areas_conhecimento"]},
        "disciplinas": {d["id"]: d for d in data["disciplinas"]},
        "projetos": {p["id"]: p for p in data["projetos_pesquisa"]},
        "grupos": {g["id"]: g for g in data["grupos_pesquisa"]},
        "perfis": {p["id"]: p for p in data["perfis"]},
    }

    # 1. Gerar ontologia/dados.ttl
    dados_ttl = generate_dados_ttl(data)
    DADOS_TTL_PATH.write_text(dados_ttl, encoding="utf-8")
    print(f"[OK] Gerado {DADOS_TTL_PATH.relative_to(ROOT_DIR)}")

    # 2. Gerar páginas HTML individuais dos perfis e validar cada JSON-LD
    PERFIS_DIR.mkdir(parents=True, exist_ok=True)
    for perfil in data["perfis"]:
        html_content = render_profile_html(perfil, data, lookup)
        out_file = PERFIS_DIR / f"{perfil['slug']}.html"
        out_file.write_text(html_content, encoding="utf-8")

        # Valida JSON-LD embutido com rdflib
        jsonld_obj = build_jsonld_for_profile(perfil, data, lookup)
        g_jld = rdflib.Graph()
        g_jld.parse(data=json.dumps(jsonld_obj), format="json-ld")
        print(f"[OK] Gerado {out_file.relative_to(ROOT_DIR)} (JSON-LD válido: {len(g_jld)} triplas)")

    # 3. Gerar ontologia.owl (RDF/XML) a partir de ontologia.ttl (Turtle) e validar ambos + SKOS + dados.ttl
    g_ont_ttl = rdflib.Graph().parse(str(ONTOLOGIA_TTL_PATH), format="turtle")
    g_ont_ttl.serialize(destination=str(ONTOLOGIA_OWL_PATH), format="xml", encoding="utf-8")
    print(f"[OK] Gerado {ONTOLOGIA_OWL_PATH.relative_to(ROOT_DIR)} (RDF/XML)")

    g_ont_xml = rdflib.Graph().parse(str(ONTOLOGIA_OWL_PATH), format="xml")
    print(f"[OK] Validado {ONTOLOGIA_OWL_PATH.relative_to(ROOT_DIR)} (RDF/XML): {len(g_ont_xml)} triplas")

    combined_graph = rdflib.Graph()
    for path in (ONTOLOGIA_TTL_PATH, SKOS_PATH, DADOS_TTL_PATH):
        g_part = rdflib.Graph().parse(str(path), format="turtle")
        print(f"[OK] Validado {path.relative_to(ROOT_DIR)}: {len(g_part)} triplas")
        combined_graph += g_part

    print(f"[OK] Grafo unificado total: {len(combined_graph)} triplas")

    # 4. Executar as 6 consultas SPARQL
    sparql_results = run_sparql_queries(combined_graph)
    for item in sparql_results:
        count = len(item["rows"])
        print(f"[OK] {item['arquivo']} -> {count} resultado(s)")
        if count == 0:
            print(f"[ERRO] Consulta {item['arquivo']} retornou 0 resultados!", file=sys.stderr)
            return 1

    # 5. Gravar resultados_sparql.md e index.html
    RESULTADOS_MD_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTADOS_MD_PATH.write_text(generate_resultados_md(sparql_results, proj), encoding="utf-8")
    print(f"[OK] Gerado {RESULTADOS_MD_PATH.relative_to(ROOT_DIR)}")

    INDEX_HTML_PATH.write_text(
        render_index_html(data, sparql_results, len(combined_graph)),
        encoding="utf-8",
    )
    print(f"[OK] Gerado {INDEX_HTML_PATH.relative_to(ROOT_DIR)}")

    DOCUMENTACAO_HTML_PATH.write_text(
        render_documentacao_html(data),
        encoding="utf-8",
    )
    print(f"[OK] Gerado {DOCUMENTACAO_HTML_PATH.relative_to(ROOT_DIR)}")

    ARTEFATOS_HTML_PATH.write_text(
        render_artefatos_html(data, sparql_results),
        encoding="utf-8",
    )
    print(f"[OK] Gerado {ARTEFATOS_HTML_PATH.relative_to(ROOT_DIR)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
