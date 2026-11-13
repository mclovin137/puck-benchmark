#!/usr/bin/env python3
"""Auditoria fail-closed dos manifests comuns de dependências do benchmark."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
import tempfile
from types import ModuleType
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


def _advisory_sha256(vulnerability: dict) -> str:
    keys = ("id", "modified", "affected", "severity", "database_specific")
    if (not isinstance(vulnerability.get("id"), str) or not vulnerability["id"]
            or not isinstance(vulnerability.get("modified"), str) or not vulnerability["modified"]
            or not isinstance(vulnerability.get("affected"), list)):
        raise AuditError("advisory sem campos de segurança obrigatórios")
    try:
        content = json.dumps({key: vulnerability.get(key) for key in keys}, ensure_ascii=False,
                             sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise AuditError("campos de segurança do advisory inválidos") from exc
    return hashlib.sha256(content).hexdigest()


def _load_trusted_snapshot_module(source_root: Path, trusted_root: Path, trusted_sha: str):
    if not isinstance(trusted_sha, str) or len(trusted_sha) != 40 or any(c not in "0123456789abcdef" for c in trusted_sha):
        raise AuditError("trusted SHA deve conter 40 hex minúsculos")
    if source_root.is_symlink() or trusted_root.is_symlink():
        raise AuditError("source/trusted roots não podem ser symlink")
    try:
        source = source_root.resolve(strict=True)
        trusted = trusted_root.resolve(strict=True)
        if source == trusted or source in trusted.parents or trusted in source.parents:
            raise AuditError("source e trusted roots devem ser repositórios separados")
        script = Path(__file__)
        helper = trusted / "scripts/ci/dependency_snapshot.py"
        if script.is_symlink() or helper.is_symlink():
            raise AuditError("avaliador/helper confiável não pode ser symlink")
        script_relative = script.resolve(strict=True).relative_to(trusted).as_posix()
        helper_relative = helper.resolve(strict=True).relative_to(trusted).as_posix()
    except (OSError, ValueError) as exc:
        raise AuditError("avaliador/helper fora do trusted root") from exc
    if script_relative != "scripts/ci/dependency-audit.py" or helper_relative != "scripts/ci/dependency_snapshot.py":
        raise AuditError("caminho do avaliador/helper diverge do layout confiável")

    def git(args, input_bytes=None):
        try:
            result = subprocess.run(["git", "-C", str(trusted), *args], input=input_bytes,
                                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                    timeout=20, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise AuditError("Git confiável indisponível") from exc
        if result.returncode != 0 or len(result.stdout) > 16_000_000:
            raise AuditError("verificação Git confiável falhou")
        return result.stdout

    top = Path(git(["rev-parse", "--show-toplevel"]).decode("utf-8", "strict").strip()).resolve(strict=True)
    head = git(["rev-parse", "HEAD"]).decode("ascii", "strict").strip()
    resolved_commit = git(["rev-parse", f"{trusted_sha}^{{commit}}"]).decode("ascii", "strict").strip()
    if top != trusted or head != trusted_sha or resolved_commit != trusted_sha:
        raise AuditError("trusted checkout não corresponde ao SHA fixado")
    dirty = git(["status", "--porcelain=v1", "-z", "--untracked-files=all", "--", "scripts/ci"])
    if dirty:
        raise AuditError("fontes do avaliador confiável modificadas")
    helper_source = None
    for relative, path in ((script_relative, script.resolve(strict=True)), (helper_relative, helper)):
        entry = git(["ls-tree", "-z", trusted_sha, "--", relative]).split(b"\0")
        entry = [part for part in entry if part]
        if len(entry) != 1:
            raise AuditError("arquivo do avaliador ausente no trusted SHA")
        try:
            metadata, repo_path = entry[0].split(b"\t", 1)
            mode, kind, object_id = metadata.decode("ascii").split(" ")
        except (ValueError, UnicodeError) as exc:
            raise AuditError("blob do avaliador inválido") from exc
        if repo_path.decode("utf-8", "strict") != relative or mode not in ("100644", "100755") or kind != "blob":
            raise AuditError("arquivo do avaliador não é blob regular confiável")
        content = path.read_bytes()
        worktree_oid = git(["hash-object", "--stdin"], input_bytes=content).decode("ascii", "strict").strip()
        if worktree_oid != object_id:
            raise AuditError("bytes do avaliador divergem do trusted SHA")
        if relative == helper_relative:
            helper_source = content

    name = "puck_trusted_dependency_snapshot"
    if helper_source is None:
        raise AuditError("helper confiável não pode ser carregado")
    module = ModuleType(name)
    module.__file__ = str(helper)
    module.__package__ = ""
    sys.modules[name] = module
    previous_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        # Executa os bytes conferidos no Git, sem selecionar bytecode de cache.
        exec(compile(helper_source, str(helper), "exec", dont_inherit=True), module.__dict__)
    except Exception as exc:
        sys.modules.pop(name, None)
        raise AuditError("helper confiável inválido") from exc
    finally:
        sys.dont_write_bytecode = previous_bytecode
    return module


def _run(scanner: Path, target: Path, mode: str) -> dict:
    args = ([str(scanner), "scan", "source", "-r", str(target)] if mode == "directory"
            else [str(scanner), "scan", "source", "--lockfile", str(target)])
    args += ["--format", "json", "--all-packages", "--all-vulns", "--verbosity", "error"]
    try:
        with tempfile.TemporaryDirectory(prefix="benchmark-osv-config-") as scratch:
            config = Path(scratch) / "osv-scanner.toml"
            config.write_text("", encoding="utf-8")
            completed = subprocess.run(
                [*args, "--config", str(config)],
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
                                 "severity": _severity(vuln, group_by_id.get(vuln["id"], {})),
                                 "advisory_sha256": _advisory_sha256(vuln),
                                 "ecosystem": package.get("ecosystem", "")})
    if completed.returncode == 1 and finding_count == 0:
        raise AuditError("scanner retornou código 1 sem achados")
    if completed.returncode == 0 and finding_count:
        raise AuditError("scanner retornou código 0 com achados")
    return {"packages": package_count, "findings": packages}


def audit(root: Path, scanner: Path, triage_path: Path, report_path: Path,
          snapshot_authorization=None, snapshot_module=None) -> tuple[dict, int]:
    if snapshot_authorization is None:
        _load_triage(triage_path)
    else:
        snapshot_module.assert_authorization_current(snapshot_authorization)
    report = {"schema_version": 1, "scanner": "OSV-Scanner 2.7.0", "sources": [], "status": "failed"}
    if snapshot_authorization is not None:
        report["snapshot_authorization"] = {
            "status": "active", "trusted_sha": snapshot_authorization.trusted_sha,
            "policy_sha256": snapshot_authorization.policy_sha256,
            "scanner_sha256": snapshot_authorization.scanner_sha256,
        }
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
            decision = (snapshot_module.decision_for(snapshot_authorization, scenario, finding)
                        if snapshot_authorization is not None else None)
            disposition = "aplicada" if decision else "pendente" if high else "observado"
            if high and not decision:
                unresolved.append(f"{scenario}/{ecosystem}:{finding['package']}@{finding['version']}:{finding['id']}:{severity}")
            item = {"package": finding["package"], "version": finding["version"],
                    "advisory": finding["id"], "advisory_sha256": finding["advisory_sha256"],
                    "severity": severity, "triage": disposition}
            if decision:
                item.update({"decision": decision["decision"], "decision_status": "active",
                             "reviewer": decision["reviewer"], "risk_residual": decision["risk_residual"],
                             "evidence": decision["evidence"]})
            source["findings"].append(item)
        report["sources"].append(source)
    if snapshot_authorization is not None:
        snapshot_module.assert_authorization_current(snapshot_authorization)
        report["snapshot_authorization"]["sources"] = [
            {"scenario": scenario, "source_sha256": snapshot_authorization.source_sha256[scenario],
             "graph_sha256": snapshot_authorization.graph_sha256[scenario]}
            for scenario in sorted(snapshot_authorization.source_sha256)
        ]
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
    parser.add_argument("--trusted-root", type=Path)
    parser.add_argument("--trusted-sha")
    args = parser.parse_args()
    root = args.root
    triage = args.triage or root / "experiment/dependency-triage.json"
    try:
        if (args.trusted_root is None) != (args.trusted_sha is None):
            raise AuditError("trusted-root e trusted-sha precisam ser fornecidos juntos")
        if args.trusted_root is None:
            report, code = audit(root.resolve(), args.scanner.resolve(), triage, args.report.resolve())
        else:
            if args.triage is not None:
                raise AuditError("triage candidato não é aceito no modo trusted")
            module = _load_trusted_snapshot_module(root, args.trusted_root, args.trusted_sha)
            helper_file = args.trusted_root / "scripts/ci/dependency_snapshot.py"
            scanner_path = args.scanner if args.scanner.is_absolute() else args.trusted_root / args.scanner
            snapshot = module.prepare_snapshot(root, args.trusted_root, args.trusted_sha,
                                               Path(__file__), helper_file, scanner_path)
            report, code = audit(root, scanner_path, triage, args.report,
                                 snapshot_authorization=snapshot, snapshot_module=module)
    except Exception as exc:
        if "module" in locals() and isinstance(exc, module.SnapshotError):
            print(f"auditoria de dependências reprovada: {exc}", file=sys.stderr)
            return 2
        if isinstance(exc, (AuditError, OSError)):
            print(f"auditoria de dependências reprovada: {exc}", file=sys.stderr)
            return 2
        raise
    print(f"auditoria: {report['status']}; fontes={len(report['sources'])}; achados altos/críticos sem triagem={len(report['untriaged_high_critical'])}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
