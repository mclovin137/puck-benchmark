#!/usr/bin/env python3
"""Auditoria fail-closed dos manifests comuns de dependências do benchmark."""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path


TARGETS = (
    ("C1", "Maven", "scenarios/c1-specialists-economy/backend", "directory"),
    ("C1", "npm", "scenarios/c1-specialists-economy/frontend", "directory"),
    ("C2", "Maven", "scenarios/c2-specialists-advanced/backend", "directory"),
    ("C2", "npm", "scenarios/c2-specialists-advanced/frontend", "directory"),
    ("C3", "Maven", "scenarios/c3-manager-economy/backend", "directory"),
    ("C3", "npm", "scenarios/c3-manager-economy/frontend", "directory"),
    ("C4", "Maven", "scenarios/c4-manager-advanced/backend", "directory"),
    ("C4", "npm", "scenarios/c4-manager-advanced/frontend", "directory"),
    ("avaliador Python", "PyPI", "benchmark/requirements.txt", "lockfile"),
)
SEVERITIES = {"LOW": 1, "MEDIUM": 2, "MODERATE": 2, "HIGH": 3, "CRITICAL": 4}


class AuditError(Exception):
    pass


def _severity(vuln: dict, group: dict) -> str:
    details = vuln.get("database_specific")
    raw_value = details.get("severity", "") if isinstance(details, dict) else ""
    value = str(raw_value).upper()
    if value and value not in SEVERITIES:
        return "UNKNOWN"
    raw = group.get("max_severity")
    if raw is None:
        if not value:
            return "UNKNOWN"
        return "MODERATE" if value == "MEDIUM" else value
    try:
        score = float(raw)
    except (TypeError, ValueError):
        return "UNKNOWN"
    if not math.isfinite(score) or not 0 <= score <= 10:
        return "UNKNOWN"
    if score >= 9:
        score_severity = "CRITICAL"
    elif score >= 7:
        score_severity = "HIGH"
    elif score >= 4:
        score_severity = "MODERATE"
    else:
        score_severity = "LOW"
    if not value:
        return score_severity
    normalized = "MODERATE" if value == "MEDIUM" else value
    return max((normalized, score_severity), key=lambda level: SEVERITIES[level])


def _load_triage(path: Path) -> None:
    if not path.exists():
        raise AuditError("arquivo de triagem ausente; cobertura fail-closed")
    try:
        records = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AuditError("arquivo de triagem inválido") from exc
    if records != []:
        raise AuditError("triagem não habilitada sem binding de código; highs/críticos permanecem bloqueantes")


def _run(scanner: Path, target: Path, mode: str) -> dict:
    args = ([str(scanner), "scan", "source", "-r", str(target)] if mode == "directory"
            else [str(scanner), "scan", "source", "--lockfile", str(target)])
    args += ["--format", "json", "--all-packages", "--all-vulns", "--verbosity", "error"]
    try:
        completed = subprocess.run(
            args,
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AuditError("scanner indisponível ou excedeu o limite") from exc
    if completed.returncode not in (0, 1):
        raise AuditError("scanner terminou com erro; resultado não confiável")
    try:
        data = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise AuditError("scanner não produziu relatório JSON válido") from exc
    if not isinstance(data, dict) or not isinstance(data.get("results"), list) or not data["results"]:
        raise AuditError("relatório do scanner ausente ou sem resultados")
    packages = []
    package_count = 0
    finding_count = 0
    for source in data["results"]:
        if not isinstance(source, dict) or not isinstance(source.get("packages"), list):
            raise AuditError("estrutura de relatório inesperada")
        for entry in source["packages"]:
            package = entry.get("package") if isinstance(entry, dict) else None
            if not isinstance(package, dict) or not isinstance(package.get("name"), str) or not package["name"]:
                raise AuditError("pacote sem nome no relatório")
            version = package.get("version", "")
            if not isinstance(version, str):
                version = ""
            package_count += 1
            vulns = entry.get("vulnerabilities", [])
            groups = entry.get("groups", [])
            if not isinstance(vulns, list) or not isinstance(groups, list):
                raise AuditError("lista de vulnerabilidades inválida")
            group_by_id = {}
            for group in groups:
                if not isinstance(group, dict) or not isinstance(group.get("ids"), list):
                    raise AuditError("grupo de vulnerabilidades inválido")
                for identifier in group["ids"]:
                    group_by_id[identifier] = group
            for vuln in vulns:
                if not isinstance(vuln, dict) or not isinstance(vuln.get("id"), str):
                    raise AuditError("vulnerabilidade sem identificador")
                finding_count += 1
                packages.append({"package": package["name"], "version": version,
                                 "id": vuln["id"], "aliases": vuln.get("aliases", []),
                                 "severity": _severity(vuln, group_by_id.get(vuln["id"], {}))})
    if completed.returncode == 1 and finding_count == 0:
        raise AuditError("scanner retornou código 1 sem achados")
    if completed.returncode == 0 and finding_count:
        raise AuditError("scanner retornou código 0 com achados")
    return {"packages": package_count, "findings": packages}


def audit(root: Path, scanner: Path, triage_path: Path, report_path: Path) -> tuple[dict, int]:
    _load_triage(triage_path)
    report = {"schema_version": 1, "scanner": "OSV-Scanner 2.7.0", "sources": [], "status": "failed"}
    unresolved = []
    for scenario, ecosystem, relative, mode in TARGETS:
        target = root / relative
        expected = target.is_dir() if mode == "directory" else target.is_file()
        if not expected:
            raise AuditError(f"fonte de dependências ausente: {scenario} {ecosystem}")
        result = _run(scanner, target, mode)
        source = {"scenario": scenario, "ecosystem": ecosystem, "manifest": relative,
                  "package_count": result["packages"], "findings": []}
        if result["packages"] == 0:
            raise AuditError(f"nenhum pacote reconhecido: {scenario} {ecosystem}")
        for finding in result["findings"]:
            severity = finding["severity"]
            high = severity in ("HIGH", "CRITICAL", "UNKNOWN")
            disposition = "pendente" if high else "observado"
            if high:
                unresolved.append(f"{scenario}/{ecosystem}:{finding['package']}@{finding['version']}:{finding['id']}:{severity}")
            item = {"package": finding["package"], "version": finding["version"],
                    "advisory": finding["id"], "severity": severity, "triage": disposition}
            source["findings"].append(item)
        report["sources"].append(source)
    report["status"] = "failed" if unresolved else "passed"
    report["untriaged_high_critical"] = unresolved
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report, 1 if unresolved else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--scanner", type=Path, required=True)
    parser.add_argument("--triage", type=Path)
    parser.add_argument("--report", type=Path, default=Path("dependency-audit.json"))
    args = parser.parse_args()
    root = args.root.resolve()
    triage = args.triage or root / "experiment/dependency-triage.json"
    try:
        report, code = audit(root, args.scanner.resolve(), triage, args.report.resolve())
    except AuditError as exc:
        print(f"auditoria de dependências reprovada: {exc}", file=sys.stderr)
        return 2
    print(f"auditoria: {report['status']}; fontes={len(report['sources'])}; achados altos/críticos sem triagem={len(report['untriaged_high_critical'])}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
