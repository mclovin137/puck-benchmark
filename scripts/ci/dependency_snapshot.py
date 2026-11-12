"""Mede snapshots e valida decisões exatas da política confiável de dependências."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


SCANNER_VERSION = "2.7.0"
SCANNER_SHA256 = "160c6253e2922e9e0a6a9771c5c4c40a4b3c6090b34a3cdd5e80c96cc2e4218b"
POLICY_PATH = "experiment/dependency-snapshot-policy.json"
GRAPH_MANIFEST_PATH = "experiment/evaluation/dependency-graphs/manifest.json"
ADVISORY_MANIFEST_PATH = "experiment/evaluation/dependency-advisories/manifest.json"
INSTALLER_PATH = "benchmark/scripts/install_tools.py"
SCENARIO_DIRS = {
    "C1": "scenarios/c1-specialists-economy",
    "C2": "scenarios/c2-specialists-advanced",
    "C3": "scenarios/c3-manager-economy",
    "C4": "scenarios/c4-manager-advanced",
}
COMMON_SNAPSHOT_PATHS = (
    "experiment/configs.yaml",
    "experiment/amendments",
    "benchmark/scripts/run_system_evaluation.py",
    "scripts/pentest",
    "benchmark/pentest/policy.json",
    ".github/workflows/ci.yml",
    ".github/workflows/pentest.yml",
)
ADVISORIES = {"GHSA-j9f9-w8pj-32f8", "GHSA-pc63-qcmh-9cmg"}
EXPECTED_PACKAGE = ("Maven", "org.springframework:spring-webmvc", "6.2.19")
TREE_TOOL = "org.apache.maven.plugins:maven-dependency-plugin:3.8.1:tree"
TREE_FIELDS = ("groupId", "artifactId", "version", "type", "scope", "classifier", "optional")
POLICY_ALLOWED_FIELDS = {"schema_version", "status", "issued_at", "expires_at", "scanner", "records"}
RECORD_FIELDS = {
    "scenario", "ecosystem", "package", "version", "advisory", "severity", "decision",
    "risk_residual", "reviewer", "status", "issued_at", "expires_at", "source_sha256",
    "graph_sha256", "advisory_sha256", "evidence",
}


class SnapshotError(Exception):
    """Falha de validação que nunca autoriza dispensar um finding."""


@dataclass(frozen=True)
class SnapshotAuthorization:
    trusted_sha: str
    policy_sha256: str
    scanner_sha256: str
    installer_sha256: str
    source_sha256: dict[str, str]
    graph_sha256: dict[str, str]
    records: dict[tuple[str, str], dict]
    policy_expires_at: str
    source_root: Path
    trusted_root: Path
    scanner_path: Path
    evaluator_file: Path
    helper_file: Path


def _fail(message: str) -> SnapshotError:
    return SnapshotError(message)


def _git(root: Path, args: list[str], *, input_bytes: bytes | None = None, limit: int = 16_000_000) -> bytes:
    try:
        result = subprocess.run(["git", "-C", str(root), "--literal-pathspecs", *args], input=input_bytes,
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                timeout=30, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise _fail("Git indisponível ou excedeu o limite") from exc
    if result.returncode != 0 or len(result.stdout) > limit:
        raise _fail("consulta Git falhou ou excedeu o limite")
    return result.stdout


def _sha40(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value) is not None


def _sha256(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _repo_root(path: Path) -> tuple[Path, str]:
    if path.is_symlink() or not path.is_dir():
        raise _fail("root Git inválido")
    resolved = path.resolve(strict=True)
    raw = _git(resolved, ["rev-parse", "--show-toplevel"]).decode("ascii", "strict").strip()
    top = Path(raw).resolve(strict=True)
    if top != resolved:
        raise _fail("root informado não é o topo do checkout Git")
    head = _git(resolved, ["rev-parse", "HEAD"]).decode("ascii", "strict").strip()
    if not _sha40(head):
        raise _fail("HEAD não é um SHA-1 completo")
    return resolved, head


def _git_path(path: str) -> str:
    if (not isinstance(path, str) or not path or len(path) > 512 or path.startswith("/") or "\\" in path
            or any(part in ("", ".", "..") for part in path.split("/"))
            or any(ord(char) < 32 or ord(char) == 127 or char in ":*?[]!" for char in path)):
        raise _fail("caminho Git não é relativo e canônico")
    return path


def _no_symlink_components(root: Path, relative: str) -> Path:
    relative = _git_path(relative)
    current = root
    for part in relative.split("/"):
        current = current / part
        try:
            if current.is_symlink():
                raise _fail("symlink em caminho de snapshot")
        except OSError as exc:
            raise _fail("caminho de snapshot inválido") from exc
    try:
        resolved = current.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError) as exc:
        raise _fail("caminho fora do root ou ausente") from exc
    return current


def _status_clean(root: Path, pathspecs: list[str]) -> None:
    result = _git(root, ["status", "--porcelain=v1", "-z", "--untracked-files=all", "--", *pathspecs])
    if result:
        raise _fail("worktree/index modificado no escopo confiável: " + ",".join(pathspecs))


def _tracked_files(root: Path, pathspecs: list[str]) -> list[tuple[str, str]]:
    data = _git(root, ["ls-files", "--stage", "-z", "--", *pathspecs])
    files = []
    for item in data.split(b"\0"):
        if not item:
            continue
        try:
            metadata, raw_path = item.split(b"\t", 1)
            mode, object_id, stage = metadata.decode("ascii").split(" ")
            relative = raw_path.decode("utf-8", "strict")
        except (ValueError, UnicodeError) as exc:
            raise _fail("índice Git malformado") from exc
        _git_path(relative)
        if mode not in ("100644", "100755") or stage != "0" or not _sha40(object_id):
            raise _fail("arquivo de snapshot não regular ou merge não resolvido")
        files.append((relative, object_id))
    return files


def _git_blob_matches(root: Path, relative: str, object_id: str, expected_sha: str | None = None) -> bytes:
    path = _no_symlink_components(root, relative)
    try:
        info = path.stat()
        if not path.is_file() or info.st_size > 20_000_000:
            raise _fail("arquivo do snapshot não regular ou excede o limite")
        content = path.read_bytes()
    except OSError as exc:
        raise _fail("arquivo do snapshot não pode ser lido") from exc
    try:
        actual_oid = _git(root, ["hash-object", "--stdin"], input_bytes=content).decode("ascii", "strict").strip()
    except UnicodeError as exc:
        raise _fail("identidade de blob Git inválida") from exc
    if actual_oid != object_id:
        raise _fail("bytes do worktree divergem do Git blob confiável")
    digest = hashlib.sha256(content).hexdigest()
    if expected_sha is not None and digest != expected_sha:
        raise _fail("digest de evidência diverge dos bytes confiáveis")
    return content


def _committed_file(root: Path, commit: str, relative: str, expected_sha: str | None = None) -> bytes:
    relative = _git_path(relative)
    _status_clean(root, [relative])
    entries = _git(root, ["ls-tree", "-z", commit, "--", relative]).split(b"\0")
    entries = [entry for entry in entries if entry]
    if len(entries) != 1:
        raise _fail("arquivo confiável ausente ou ambíguo no commit")
    try:
        meta, listed_path = entries[0].split(b"\t", 1)
        mode, kind, object_id = meta.decode("ascii").split(" ")
        if listed_path.decode("utf-8", "strict") != relative or kind != "blob" or mode not in ("100644", "100755"):
            raise _fail("arquivo confiável não é blob regular")
    except (ValueError, UnicodeError) as exc:
        raise _fail("entrada Git inválida para arquivo confiável") from exc
    if not _sha40(object_id):
        raise _fail("object id Git inválido")
    return _git_blob_matches(root, relative, object_id, expected_sha)


def _snapshot_paths(scenario: str) -> list[str]:
    if scenario not in SCENARIO_DIRS:
        raise _fail("cenário desconhecido")
    return [SCENARIO_DIRS[scenario], *COMMON_SNAPSHOT_PATHS]


def measure_source_sha256(root: Path, scenario: str) -> str:
    root, _ = _repo_root(root)
    paths = _snapshot_paths(scenario)
    _status_clean(root, paths)
    tracked = _tracked_files(root, paths)
    if not tracked:
        raise _fail("escopo de snapshot sem arquivos rastreados")
    digest = hashlib.sha256()
    for relative, object_id in sorted(tracked, key=lambda pair: pair[0].encode("utf-8")):
        content = _git_blob_matches(root, relative, object_id)
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(content).hexdigest().encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def canonical_json(value: object) -> bytes:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise _fail("JSON não pode ser canonicalizado") from exc


def canonical_maven_node(node: object) -> dict:
    if not isinstance(node, dict) or set(node) not in (set(TREE_FIELDS), set(TREE_FIELDS) | {"children"}):
        raise _fail("nó Maven fora do formato fixado")
    if any(not isinstance(node[field], str) for field in TREE_FIELDS):
        raise _fail("campo Maven não é string")
    result = {field: node[field] for field in TREE_FIELDS}
    children = node.get("children", [])
    if not isinstance(children, list):
        raise _fail("children Maven não é lista")
    if children:
        canonical_children = [canonical_maven_node(child) for child in children]
        result["children"] = sorted(canonical_children, key=canonical_json)
    return result


def canonical_maven_tree(data: object) -> tuple[bytes, int, int, list[str]]:
    root = canonical_maven_node(data)
    nodes = 0
    edges = 0
    spring_versions: set[str] = set()

    def visit(node: dict) -> None:
        nonlocal nodes, edges
        nodes += 1
        if node["groupId"] == "org.springframework" and node["artifactId"] == "spring-webmvc":
            spring_versions.add(node["version"])
        children = node.get("children", [])
        edges += len(children)
        for child in children:
            visit(child)

    visit(root)
    return canonical_json(root), nodes, edges, sorted(spring_versions)


def advisory_sha256(vuln: dict) -> str:
    keys = ("id", "modified", "affected", "severity", "database_specific")
    if (not isinstance(vuln.get("id"), str) or not vuln["id"]
            or not isinstance(vuln.get("modified"), str) or not vuln["modified"]
            or not isinstance(vuln.get("affected"), list)):
        raise _fail("advisory sem campos de segurança obrigatórios")
    selected = {key: vuln.get(key) for key in keys}
    if not isinstance(selected["id"], str) or not selected["id"]:
        raise _fail("id do advisory inválido")
    return hashlib.sha256(canonical_json(selected)).hexdigest()


def _utc(value: object) -> dt.datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise _fail("timestamp deve ser UTC RFC3339 terminado em Z")
    try:
        parsed = dt.datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise _fail("timestamp UTC inválido") from exc
    if parsed.utcoffset() != dt.timedelta(0):
        raise _fail("timestamp não está em UTC")
    return parsed


def _valid_interval(issued: object, expires: object, now: dt.datetime) -> bool:
    start, end = _utc(issued), _utc(expires)
    return start < end and end - start <= dt.timedelta(days=30) and start <= now < end


def _safe_roots(source_root: Path, trusted_root: Path) -> tuple[Path, Path]:
    if source_root.is_symlink() or trusted_root.is_symlink():
        raise _fail("root não pode ser symlink")
    source, _ = _repo_root(source_root)
    trusted, _ = _repo_root(trusted_root)
    if source == trusted or source in trusted.parents or trusted in source.parents:
        raise _fail("source e trusted roots devem ser repositórios separados")
    return source, trusted


def _check_trusted_file(root: Path, sha: str, relative: str) -> bytes:
    _status_clean(root, [relative])
    return _committed_file(root, sha, relative)


def verify_trusted_checkout(trusted_root: Path, trusted_sha: str, source_root: Path,
                            evaluator_file: Path, helper_file: Path) -> tuple[Path, Path]:
    if not _sha40(trusted_sha):
        raise _fail("trusted SHA deve conter exatamente 40 hex minúsculos")
    source, trusted = _safe_roots(source_root, trusted_root)
    _, head = _repo_root(trusted)
    if head != trusted_sha:
        raise _fail("trusted SHA diverge do HEAD")
    for file in (evaluator_file, helper_file):
        if file.is_symlink():
            raise _fail("avaliador confiável não pode ser symlink")
        try:
            relative = file.resolve(strict=True).relative_to(trusted).as_posix()
        except (OSError, ValueError) as exc:
            raise _fail("__file__ ou helper fora do trusted root") from exc
        _check_trusted_file(trusted, trusted_sha, relative)
    # O avaliador não admite alterações nas próprias fontes de confiança nem no policy/evidence.
    for scenario in SCENARIO_DIRS:
        _status_clean(trusted, _snapshot_paths(scenario))
    _status_clean(trusted, ["scripts/ci", INSTALLER_PATH, POLICY_PATH, GRAPH_MANIFEST_PATH,
                            "experiment/evaluation/dependency-graphs", ADVISORY_MANIFEST_PATH,
                            "experiment/evaluation/dependency-advisories"])
    return source, trusted


def measure_scanner_binary(trusted_root: Path, scanner_path: Path) -> str:
    if scanner_path.is_symlink():
        raise _fail("scanner não pode ser symlink")
    root = trusted_root.resolve(strict=True)
    path = scanner_path if scanner_path.is_absolute() else root / scanner_path
    try:
        relative = path.absolute().relative_to(root).as_posix()
    except ValueError as exc:
        raise _fail("scanner fora do trusted root") from exc
    path = _no_symlink_components(root, relative)
    try:
        if not path.is_file() or path.stat().st_size > 100_000_000:
            raise _fail("binário do scanner ausente, não regular ou grande demais")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise _fail("binário do scanner não pode ser lido") from exc
    if digest != SCANNER_SHA256:
        raise _fail("digest real do scanner diverge do pin A-002")
    return digest


def read_trusted_policy(trusted_root: Path, trusted_sha: str) -> tuple[dict, str]:
    raw = _check_trusted_file(trusted_root, trusted_sha, POLICY_PATH)
    try:
        policy = json.loads(raw)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise _fail("política confiável inválida") from exc
    return policy, hashlib.sha256(raw).hexdigest()


def _manifest_records(trusted_root: Path, trusted_sha: str, source_root: Path) -> dict[str, dict]:
    raw = _check_trusted_file(trusted_root, trusted_sha, GRAPH_MANIFEST_PATH)
    try:
        manifest = json.loads(raw)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise _fail("manifest de grafo inválido") from exc
    if not isinstance(manifest, dict) or manifest.get("tool") != TREE_TOOL or manifest.get("format") != "json":
        raise _fail("ferramenta/formato do grafo divergem do contrato")
    expected_canonicalization = "Recursively sort child nodes by canonical JSON; preserve string fields; JSON sort_keys=true, separators comma/colon, UTF-8. Optional children omitted when empty."
    if manifest.get("canonicalization") != expected_canonicalization:
        raise _fail("regra de canonicalização do grafo divergente")
    records = manifest.get("records")
    if not isinstance(records, list) or len(records) != 4:
        raise _fail("manifest deve conter exatamente quatro árvores")
    by_scenario = {}
    for record in records:
        if not isinstance(record, dict):
            raise _fail("registro de árvore inválido")
        scenario = record.get("scenario")
        if not isinstance(scenario, str) or scenario not in SCENARIO_DIRS or scenario in by_scenario:
            raise _fail("cenário duplicado/desconhecido no manifest")
        if record.get("source_directory") != SCENARIO_DIRS[scenario] + "/backend":
            raise _fail("diretório de grafo divergente")
        if not _sha40(record.get("scenario_git_tree")) or not _sha256(record.get("source_pom_sha256")):
            raise _fail("digest/árvore de fonte inválido no manifest")
        if not _sha256(record.get("canonical_tree_sha256")):
            raise _fail("digest de árvore inválido no manifest")
        tree_file = _git_path(record.get("tree_file"))
        if tree_file != f"experiment/evaluation/dependency-graphs/{scenario.lower()}.json":
            raise _fail("caminho de árvore fora da lista fixada")
        tree_bytes = _check_trusted_file(trusted_root, trusted_sha, tree_file)
        try:
            tree = json.loads(tree_bytes)
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise _fail("árvore confiável inválida") from exc
        canonical, nodes, edges, versions = canonical_maven_tree(tree)
        if hashlib.sha256(canonical).hexdigest() != record["canonical_tree_sha256"]:
            raise _fail("árvore canônica diverge do manifest")
        if nodes != record.get("reported_nodes") or edges != record.get("reported_edges"):
            raise _fail("topologia de grafo diverge do manifest")
        if versions != record.get("spring_webmvc_versions"):
            raise _fail("versão Maven do componente diverge do manifest")
        scenario_tree = _git(trusted_root, ["rev-parse", f"{trusted_sha}:{SCENARIO_DIRS[scenario]}"]).decode("ascii", "strict").strip()
        source_tree = _git(source_root, ["rev-parse", f"HEAD:{SCENARIO_DIRS[scenario]}"]).decode("ascii", "strict").strip()
        if scenario_tree != record["scenario_git_tree"] or source_tree != record["scenario_git_tree"]:
            raise _fail("árvore de cenário diverge da evidência confiável")
        pom = source_root / SCENARIO_DIRS[scenario] / "backend/pom.xml"
        if pom.is_symlink() or not pom.is_file() or hashlib.sha256(pom.read_bytes()).hexdigest() != record["source_pom_sha256"]:
            raise _fail("POM da fonte diverge do manifest")
        by_scenario[scenario] = record
    if set(by_scenario) != set(SCENARIO_DIRS):
        raise _fail("manifest não cobre C1–C4")
    return by_scenario


def _advisory_records(trusted_root: Path, trusted_sha: str) -> dict[str, str]:
    raw = _check_trusted_file(trusted_root, trusted_sha, ADVISORY_MANIFEST_PATH)
    try:
        manifest = json.loads(raw)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise _fail("manifest de advisories inválido") from exc
    records = manifest.get("records") if isinstance(manifest, dict) else None
    if not isinstance(records, list) or len(records) != 2:
        raise _fail("manifest deve conter exatamente os dois advisories A-002")
    by_id = {}
    for record in records:
        if not isinstance(record, dict):
            raise _fail("registro de advisory inválido")
        advisory = record.get("advisory")
        if not isinstance(advisory, str) or advisory not in ADVISORIES or advisory in by_id:
            raise _fail("advisory duplicado/desconhecido no manifest")
        digest = record.get("security_fields_sha256")
        if not _sha256(digest):
            raise _fail("digest de metadados OSV inválido")
        relative = f"experiment/evaluation/dependency-advisories/{advisory}.json"
        raw_advisory = _check_trusted_file(trusted_root, trusted_sha, relative)
        try:
            data = json.loads(raw_advisory)
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise _fail("JSON primário do advisory inválido") from exc
        if not isinstance(data, dict) or data.get("id") != advisory:
            raise _fail("identidade do JSON primário diverge")
        actual = advisory_sha256(data)
        if actual != digest or data.get("modified") != record.get("modified"):
            raise _fail("metadados OSV divergem do manifest confiável")
        by_id[advisory] = digest
    if set(by_id) != ADVISORIES:
        raise _fail("manifest não cobre os dois advisories A-002")
    return by_id


def _bind_primary_advisories(records: dict, primary_hashes: dict[str, str]) -> None:
    for record in records.values():
        if record["advisory_sha256"] != primary_hashes.get(record["advisory"]):
            raise _fail("digest do registro diverge do advisory primário confiável")


def _maven_tree(source_root: Path, scenario: str, timeout: int = 300) -> tuple[str, str]:
    if scenario not in SCENARIO_DIRS:
        raise _fail("cenário Maven desconhecido")
    backend = source_root / SCENARIO_DIRS[scenario] / "backend"
    source_pom = backend / "pom.xml"
    if backend.is_symlink() or not backend.is_dir() or source_pom.is_symlink() or not source_pom.is_file():
        raise _fail("diretório Maven ou POM inválido")
    try:
        with tempfile.TemporaryDirectory(prefix="dependency-tree-") as temp:
            temporary = Path(temp)
            project = temporary / "project"
            project.mkdir(mode=0o700)
            isolated_pom = project / "pom.xml"
            pom_bytes = source_pom.read_bytes()
            isolated_pom.write_bytes(pom_bytes)
            output = temporary / "tree.json"
            repo = temporary / "repository"
            home = temporary / "home"
            home.mkdir(mode=0o700)
            settings = temporary / "settings.xml"
            settings.write_text("<settings xmlns=\"http://maven.apache.org/SETTINGS/1.2.0\"></settings>\n", encoding="utf-8")
            args = ["mvn", "-B", "--no-transfer-progress", "-s", str(settings), "-gs", str(settings),
                    "-f", str(isolated_pom),
                    TREE_TOOL, "-DoutputType=json", f"-DoutputFile={output}",
                    f"-Dmaven.repo.local={repo}", f"-Duser.home={home}"]
            env = {key: os.environ[key] for key in ("PATH", "JAVA_HOME") if key in os.environ}
            env.update({"HOME": str(home), "USERPROFILE": str(home), "MAVEN_OPTS": "", "MAVEN_ARGS": "",
                        "JAVA_TOOL_OPTIONS": "", "MAVEN_CONFIG": str(temporary), "LANG": "C.UTF-8"})
            try:
                result = subprocess.run(args, cwd=project, env={**env, "MAVEN_PROJECTBASEDIR": str(project)}, stdin=subprocess.DEVNULL,
                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                        timeout=timeout, check=False)
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise _fail("Maven indisponível ou excedeu o limite") from exc
            if result.returncode != 0 or output.is_symlink() or not output.is_file() or output.stat().st_size > 20_000_000:
                raise _fail("Maven não produziu uma árvore regular válida")
            try:
                data = json.loads(output.read_bytes())
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                raise _fail("JSON de árvore Maven inválido") from exc
            canonical, _, _, versions = canonical_maven_tree(data)
            if versions != ["6.2.19"]:
                raise _fail("árvore Maven não contém a versão Spring esperada")
            return hashlib.sha256(canonical).hexdigest(), hashlib.sha256(pom_bytes).hexdigest()
    except SnapshotError:
        raise
    except OSError as exc:
        raise _fail("não foi possível processar a árvore Maven") from exc


def _validate_evidence(root: Path, trusted_sha: str, record: dict) -> None:
    evidence = record.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        raise _fail("registro sem evidência")
    seen = set()
    for item in evidence:
        if not isinstance(item, dict) or set(item) != {"path", "sha256"}:
            raise _fail("identidade de evidência inválida")
        path = _git_path(item["path"])
        if path in seen or not _sha256(item["sha256"]):
            raise _fail("evidência duplicada ou digest inválido")
        seen.add(path)
        _committed_file(root, trusted_sha, path, item["sha256"])


def _expected_identity(scenario: str, advisory: str) -> tuple:
    if not isinstance(scenario, str) or not isinstance(advisory, str):
        raise _fail("identidade de exceção inválida")
    if scenario not in SCENARIO_DIRS or advisory not in ADVISORIES:
        raise _fail("identidade de exceção fora da lista fixa")
    return scenario, "Maven", EXPECTED_PACKAGE[1], EXPECTED_PACKAGE[2], advisory


def _validate_policy(policy: object, scanner_sha: str, installer_sha: str,
                     source_sha: dict[str, str], graph_sha: dict[str, str],
                     trusted_root: Path, trusted_sha: str, now: dt.datetime) -> tuple[str, dict]:
    if not isinstance(policy, dict) or set(policy) != POLICY_ALLOWED_FIELDS:
        raise _fail("política ausente, incompleta ou com campos extras")
    if policy.get("schema_version") != 1 or policy.get("status") != "active":
        raise _fail("política não está ativa")
    if not _valid_interval(policy.get("issued_at"), policy.get("expires_at"), now):
        raise _fail("política expirada ou validade superior a 30 dias")
    scanner = policy.get("scanner")
    if not isinstance(scanner, dict) or set(scanner) != {"name", "version", "binary_sha256", "installer_sha256"}:
        raise _fail("identidade de scanner inválida na política")
    if (scanner.get("name") != "OSV-Scanner" or scanner.get("version") != SCANNER_VERSION
            or scanner.get("binary_sha256") != scanner_sha or scanner_sha != SCANNER_SHA256
            or scanner.get("installer_sha256") != installer_sha):
        raise _fail("scanner/instalador diverge da medição confiável")
    records = policy.get("records")
    if not isinstance(records, list) or len(records) != 8:
        raise _fail("política ativa exige exatamente oito decisões")
    expected = {_expected_identity(scenario, advisory) for scenario in SCENARIO_DIRS for advisory in ADVISORIES}
    found = {}
    for record in records:
        if not isinstance(record, dict) or set(record) != RECORD_FIELDS:
            raise _fail("registro incompleto ou com campos extras")
        identity = _expected_identity(record.get("scenario"), record.get("advisory"))
        if identity in found or identity not in expected:
            raise _fail("registro duplicado ou identidade não permitida")
        if any(record.get(key) != value for key, value in zip(("scenario", "ecosystem", "package", "version", "advisory"), identity)):
            raise _fail("identidade do registro divergente")
        if record.get("severity") != "CRITICAL" or record.get("decision") != "not_reachable_in_reviewed_snapshot":
            raise _fail("decisão/severidade não corresponde à política fixa")
        if not isinstance(record.get("risk_residual"), str) or not record["risk_residual"].strip():
            raise _fail("risco residual ausente")
        residual = record["risk_residual"]
        if (len(residual) > 500 or any(ord(char) < 32 or ord(char) == 127 for char in residual)
                or re.search(r"(?i)(/home/|/tmp/|[a-z]:\\|bearer\s|gh[pousr]_|sk-[a-z0-9])", residual)):
            raise _fail("risco residual fora do formato publicável")
        if record.get("reviewer") != "neo" or record.get("status") != "active":
            raise _fail("registro sem aprovação Neo ativa")
        if not _valid_interval(record.get("issued_at"), record.get("expires_at"), now):
            raise _fail("registro expirado ou validade superior a 30 dias")
        for field, values in (("source_sha256", source_sha), ("graph_sha256", graph_sha)):
            digest = record.get(field)
            if not _sha256(digest) or digest != values.get(record["scenario"]):
                raise _fail(f"{field} diverge da medição")
        if not _sha256(record.get("advisory_sha256")):
            raise _fail("digest de advisory inválido")
        _validate_evidence(trusted_root, trusted_sha, record)
        found[identity] = record
    if set(found) != expected:
        raise _fail("faltam decisões exatas para C1–C4/A-002")
    return hashlib.sha256(canonical_json(policy)).hexdigest(), found


def prepare_snapshot(source_root: Path, trusted_root: Path, trusted_sha: str,
                     evaluator_file: Path, helper_file: Path, scanner_path: Path,
                     *, now: dt.datetime | None = None,
                     maven_runner: Callable[[Path, str], tuple[str, str]] | None = None) -> SnapshotAuthorization:
    source, trusted = verify_trusted_checkout(trusted_root, trusted_sha, source_root, evaluator_file, helper_file)
    now = now or dt.datetime.now(dt.timezone.utc)
    if now.tzinfo is None or now.utcoffset() != dt.timedelta(0):
        raise _fail("relógio de validação deve estar em UTC")
    scanner_sha = measure_scanner_binary(trusted, scanner_path)
    installer_bytes = _check_trusted_file(trusted, trusted_sha, INSTALLER_PATH)
    installer_sha = hashlib.sha256(installer_bytes).hexdigest()
    policy, policy_sha = read_trusted_policy(trusted, trusted_sha)
    primary_hashes = _advisory_records(trusted, trusted_sha)
    source_sha = {scenario: measure_source_sha256(source, scenario) for scenario in SCENARIO_DIRS}
    manifest = _manifest_records(trusted, trusted_sha, source)
    runner = maven_runner or _maven_tree
    graph_sha = {}
    for scenario, record in manifest.items():
        digest, pom_sha = runner(source, scenario)
        if digest != record["canonical_tree_sha256"] or pom_sha != record["source_pom_sha256"]:
            raise _fail("grafo Maven medido diverge do snapshot confiável")
        graph_sha[scenario] = digest
    # Detecta mutação feita durante a extração do grafo antes de aceitar qualquer registro.
    for scenario, digest in source_sha.items():
        if measure_source_sha256(source, scenario) != digest:
            raise _fail("fonte mudou durante a medição")
    _, records = _validate_policy(policy, scanner_sha, installer_sha,
                                  source_sha, graph_sha, trusted, trusted_sha, now)
    _bind_primary_advisories(records, primary_hashes)
    # Policy/evidence/measurement scopes must remain immutable until evaluation starts.
    verify_trusted_checkout(trusted, trusted_sha, source, evaluator_file, helper_file)
    if measure_scanner_binary(trusted, scanner_path) != scanner_sha:
        raise _fail("binário scanner mudou durante a medição")
    return SnapshotAuthorization(trusted_sha, policy_sha, scanner_sha, installer_sha, source_sha, graph_sha,
                                 records, policy["expires_at"], source, trusted, scanner_path,
                                 evaluator_file, helper_file)


def assert_authorization_current(snapshot: SnapshotAuthorization) -> None:
    verify_trusted_checkout(snapshot.trusted_root, snapshot.trusted_sha, snapshot.source_root,
                            snapshot.evaluator_file, snapshot.helper_file)
    if measure_scanner_binary(snapshot.trusted_root, snapshot.scanner_path) != snapshot.scanner_sha256:
        raise _fail("binário scanner mudou durante a auditoria")
    policy, policy_sha = read_trusted_policy(snapshot.trusted_root, snapshot.trusted_sha)
    if policy_sha != snapshot.policy_sha256:
        raise _fail("política mudou durante a auditoria")
    installer = _check_trusted_file(snapshot.trusted_root, snapshot.trusted_sha, INSTALLER_PATH)
    primary_hashes = _advisory_records(snapshot.trusted_root, snapshot.trusted_sha)
    _, records = _validate_policy(policy, snapshot.scanner_sha256, hashlib.sha256(installer).hexdigest(),
                                  snapshot.source_sha256, snapshot.graph_sha256,
                                  snapshot.trusted_root, snapshot.trusted_sha, dt.datetime.now(dt.timezone.utc))
    _bind_primary_advisories(records, primary_hashes)
    for scenario, expected in snapshot.source_sha256.items():
        if measure_source_sha256(snapshot.source_root, scenario) != expected:
            raise _fail("fonte mudou durante a auditoria")


def decision_for(snapshot: SnapshotAuthorization, scenario: str, finding: dict) -> dict | None:
    if finding.get("severity") != "CRITICAL":
        return None
    now = dt.datetime.now(dt.timezone.utc)
    if _utc(snapshot.policy_expires_at) <= now:
        return None
    try:
        identity = _expected_identity(scenario, finding.get("id"))
    except SnapshotError:
        return None
    record = snapshot.records.get(identity)
    if record is None:
        return None
    if not _valid_interval(record.get("issued_at"), record.get("expires_at"), now):
        return None
    if (finding.get("ecosystem") != identity[1] or finding.get("package") != identity[2]
            or finding.get("version") != identity[3]
            or finding.get("advisory_sha256") != record["advisory_sha256"]
            or snapshot.source_sha256.get(scenario) != record["source_sha256"]
            or snapshot.graph_sha256.get(scenario) != record["graph_sha256"]):
        return None
    return {"decision": record["decision"], "risk_residual": record["risk_residual"],
            "reviewer": record["reviewer"], "evidence": record["evidence"],
            "policy_sha256": snapshot.policy_sha256}

