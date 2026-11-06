#!/usr/bin/env python3
"""Métricas de eficiência do fluxo a partir de PRs integrados e execuções de CI (stdlib, sem LLM).

Uso:
  metricas-fluxo.py --repo dono/repo [--dias 30] [--saida metricas.json] [--resumo $GITHUB_STEP_SUMMARY]
  metricas-fluxo.py --entrada fixture.json ...   # testes: {"prs": [...], "runs": {"<branch>": [...]}}

Sem rede além do `gh` (GH_TOKEN do Actions). Mede, por PR: horas até o merge, commits totais e de
retrabalho (após a primeira revisão), execuções e falhas de CI, tamanho e participação de arquivos de
documentação vs código/teste/config. Metas são de acompanhamento, não gate.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import statistics
import subprocess
import sys

DOC_EXT = (".md", ".mdx", ".rst", ".adoc", ".txt", ".puml", ".svg")
TESTE_MARCAS = ("test", "tests", "spec", "__tests__")
CONFIG_EXT = (".json", ".toml", ".yml", ".yaml", ".ini", ".cfg")
METAS = {"horas_ate_merge_mediana": 48, "commits_apos_abertura_mediana": 2, "taxa_falha_ci": 0.25,
         "participacao_documentacao": 0.40}


def _data(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def categoria(caminho: str) -> str:
    c = caminho.lower()
    partes = c.split("/")
    nome = partes[-1]
    if nome.endswith(DOC_EXT) or "docs" in partes[:-1]:
        return "documentacao"
    if any(p in TESTE_MARCAS for p in partes[:-1]) or nome.startswith("test_") or "_test." in nome \
            or ".test." in nome or ".spec." in nome:
        return "teste"
    if nome.endswith(CONFIG_EXT) or ".github" in partes:
        return "configuracao"
    return "codigo"


def por_pr(pr: dict, runs: list[dict]) -> dict:
    criado, integrado = _data(pr["createdAt"]), _data(pr["mergedAt"])
    revisoes = sorted(_data(r["submittedAt"]) for r in pr.get("reviews", []) if r.get("submittedAt"))
    commits = [_data(c["committedDate"]) for c in pr.get("commits", []) if c.get("committedDate")]
    # Retrabalho: commits depois da abertura do PR (rodadas de correção pós-revisão, inclusive
    # revisões de agentes feitas fora do GitHub) e, quando houver review no GitHub, depois da primeira.
    apos_abertura = sum(1 for c in commits if c > criado)
    retrabalho = sum(1 for c in commits if revisoes and c > revisoes[0])
    arquivos = [f["path"] for f in pr.get("files", [])]
    cats = {k: 0 for k in ("codigo", "teste", "documentacao", "configuracao")}
    for a in arquivos:
        cats[categoria(a)] += 1
    ci = [r for r in runs if r.get("event") in {"pull_request", "push"}]
    falhas = sum(1 for r in ci if r.get("conclusion") in {"failure", "timed_out", "startup_failure"})
    return {
        "numero": pr["number"],
        "horas_ate_merge": round((integrado - criado).total_seconds() / 3600, 2),
        "commits": len(commits),
        "commits_apos_abertura": apos_abertura,
        "retrabalho_commits": retrabalho,
        "revisoes": len(revisoes),
        "ci_execucoes": len(ci),
        "ci_falhas": falhas,
        "linhas": int(pr.get("additions", 0)) + int(pr.get("deletions", 0)),
        "arquivos": len(arquivos),
        "arquivos_por_categoria": cats,
        "nivel": next((l["name"].split(":", 1)[1] for l in pr.get("labels", []) if l["name"].startswith("nivel:")), "n/d"),
    }


def agregar(itens: list[dict]) -> dict:
    if not itens:
        return {"amostras": 0, "nota": "sem PRs integrados na janela; métricas n/d"}
    med = lambda k: statistics.median(i[k] for i in itens)
    ci_total = sum(i["ci_execucoes"] for i in itens)
    arq = {k: sum(i["arquivos_por_categoria"][k] for i in itens) for k in ("codigo", "teste", "documentacao", "configuracao")}
    total_arq = sum(arq.values()) or 1
    resumo = {
        "amostras": len(itens),
        "horas_ate_merge_mediana": med("horas_ate_merge"),
        "commits_mediana": med("commits"),
        "commits_apos_abertura_mediana": med("commits_apos_abertura"),
        "retrabalho_commits_mediana": med("retrabalho_commits"),
        "revisoes_mediana": med("revisoes"),
        "taxa_falha_ci": round(sum(i["ci_falhas"] for i in itens) / ci_total, 3) if ci_total else None,
        "participacao_por_categoria": {k: round(v / total_arq, 3) for k, v in arq.items()},
    }
    resumo["participacao_documentacao"] = resumo["participacao_por_categoria"]["documentacao"]
    resumo["alertas"] = [f"{k} acima da meta ({resumo[k]} > {v})" for k, v in METAS.items()
                         if resumo.get(k) is not None and resumo[k] > v]
    return resumo


def coletar(repo: str, dias: int) -> tuple[list[dict], dict]:
    desde = (dt.date.today() - dt.timedelta(days=dias)).isoformat()
    # Lista leve + detalhe por PR: a consulta aninhada estoura o limite de nós do GraphQL do GitHub.
    leves = json.loads(subprocess.run(
        ["gh", "pr", "list", "-R", repo, "--state", "merged", "--search", f"merged:>={desde}",
         "--limit", "200", "--json", "number,createdAt,mergedAt,headRefName,additions,deletions,labels"],
        check=True, capture_output=True, text=True).stdout)
    prs = []
    for leve in leves:
        detalhe = json.loads(subprocess.run(
            ["gh", "pr", "view", str(leve["number"]), "-R", repo, "--json", "commits,reviews,files"],
            check=True, capture_output=True, text=True).stdout)
        prs.append({**leve, **detalhe})
    runs = {}
    for pr in prs:
        runs[pr["headRefName"]] = json.loads(subprocess.run(
            ["gh", "run", "list", "-R", repo, "--branch", pr["headRefName"], "--limit", "100",
             "--json", "conclusion,event,workflowName"], check=True, capture_output=True, text=True).stdout)
    return prs, runs


def markdown(resumo: dict, itens: list[dict], dias: int) -> str:
    linhas = [f"## Métricas do fluxo ({dias} dias)", ""]
    if not resumo.get("amostras"):
        return "\n".join(linhas + [resumo.get("nota", "n/d")]) + "\n"
    linhas += ["| Métrica | Valor | Meta |", "|---|---|---|"]
    for k, meta in [("horas_ate_merge_mediana", "≤ 48"), ("commits_apos_abertura_mediana", "≤ 2"),
                    ("revisoes_mediana", "—"), ("taxa_falha_ci", "≤ 0,25"), ("participacao_documentacao", "≤ 0,40")]:
        linhas.append(f"| {k} | {resumo[k]} | {meta} |")
    linhas += ["", "Arquivos por categoria: " + ", ".join(f"{k} {v:.0%}" for k, v in resumo["participacao_por_categoria"].items()),
               "", "Alertas: " + ("; ".join(resumo["alertas"]) or "nenhum"), "",
               f"Amostras: {resumo['amostras']} PRs. Metas de acompanhamento, não gate."]
    return "\n".join(linhas) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo")
    ap.add_argument("--dias", type=int, default=30)
    ap.add_argument("--entrada")
    ap.add_argument("--saida", default="metricas-fluxo.json")
    ap.add_argument("--resumo")
    a = ap.parse_args()
    if a.entrada:
        dados = json.load(open(a.entrada, encoding="utf-8"))
        prs, runs = dados["prs"], dados.get("runs", {})
    elif a.repo:
        prs, runs = coletar(a.repo, a.dias)
    else:
        ap.error("--repo ou --entrada")
    itens = [por_pr(pr, runs.get(pr.get("headRefName", ""), [])) for pr in prs if pr.get("mergedAt")]
    resumo = agregar(itens)
    json.dump({"janela_dias": a.dias, "resumo": resumo, "prs": itens}, open(a.saida, "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)
    texto = markdown(resumo, itens, a.dias)
    if a.resumo:
        open(a.resumo, "a", encoding="utf-8").write(texto)
    print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
