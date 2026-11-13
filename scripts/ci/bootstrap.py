#!/usr/bin/env python3
"""Verifica a árvore mínima de bootstrap e audita as duas fontes de dependência."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


SOURCE_COMMIT = "219d50f920ba9fbcd107e202d5661185d11e5676"
INITIAL_MAIN = "c5d985cbb5adff2983325bc3feeb4c90856d2b3a"
OSV_SCANNER_SHA256 = "160c6253e2922e9e0a6a9771c5c4c40a4b3c6090b34a3cdd5e80c96cc2e4218b"
OSV_VERSION = "2.7.0"
MAX_FILES = 30
PROCESS_TIMEOUT_SECONDS = 120

IMPORT_PATHS = (
    ".github/workflows/pentest.yml",
    "scripts/pentest/guards.py",
    "scripts/pentest/preflight.py",
    "scripts/pentest/report.py",
    "scripts/pentest/run-ci.py",
    "scripts/pentest/zap-plan.py",
    "benchmark/pentest/README.md",
    "benchmark/pentest/gateway.py",
    "benchmark/pentest/package.json",
    "benchmark/pentest/package-lock.json",
    "benchmark/pentest/policy.json",
    "benchmark/pentest/runner.Dockerfile",
    "benchmark/pentest/tests/test_guards.py",
    "benchmark/pentest/triagem.json",
    "benchmark/pentest/ui-security.cjs",
    "benchmark/scripts/install_tools.py",
)

ALLOWLIST = frozenset(
    IMPORT_PATHS
    + (
        ".gitignore",
        ".gitleaks.toml",
        "AGENTS.md",
        "CHANGELOG.md",
        "README.md",
        "docs/rules.md",
        "docs/lib.md",
        "docs/roadmap.md",
        "docs/verificacao.md",
        "docs/bootstrap-security.md",
        "scripts/ci/bootstrap.py",
        "benchmark/bootstrap/test_bootstrap.py",
        ".github/workflows/bootstrap-a0.yml",
        "bootstrap-manifest.json",
    )
)

ROOT = Path(__file__).resolve().parents[2]


class BootstrapError(Exception):
    """Falha fechada com mensagem sanitizada para a saída do CLI."""


def _git(repo: Path, *args: str) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo), *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=PROCESS_TIMEOUT_SECONDS,
            text=True,
            encoding="utf-8",
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise BootstrapError("git_operation_failed") from exc
    return completed.stdout.strip()


def _valid_sha(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value) is not None


def _commit_exists(repo: Path, sha: str) -> bool:
    if not _valid_sha(sha):
        return False
    try:
        _git(repo, "cat-file", "-e", f"{sha}^{{commit}}")
    except BootstrapError:
        return False
    return True


def _tree(repo: Path, commit: str) -> dict[str, tuple[str, str, str]]:
    """Mapeia caminho para modo, tipo e object id sem perder nomes com espaços."""
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo), "ls-tree", "-r", "-z", "--full-tree", commit],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=PROCESS_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise BootstrapError("tree_read_failed") from exc
    entries: dict[str, tuple[str, str, str]] = {}
    for record in completed.stdout.split(b"\0"):
        if not record:
            continue
        try:
            metadata, raw_path = record.split(b"\t", 1)
            mode, kind, oid = metadata.decode("ascii").split(" ")
            path = raw_path.decode("utf-8", errors="strict")
        except (ValueError, UnicodeDecodeError) as exc:
            raise BootstrapError("invalid_tree_record") from exc
        if path in entries:
            raise BootstrapError("duplicate_tree_path")
        entries[path] = (mode, kind, oid)
    return entries


def _blob(repo: Path, oid: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "cat-file", "blob", oid],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=PROCESS_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise BootstrapError("blob_read_failed") from exc
    return result.stdout


def _validate_tree(repo: Path, commit: str) -> dict[str, tuple[str, str, str]]:
    entries = _tree(repo, commit)
    paths = set(entries)
    if paths != ALLOWLIST:
        raise BootstrapError("tree_paths_mismatch")
    for path, (mode, kind, _oid) in entries.items():
        if mode != "100644" or kind != "blob":
            raise BootstrapError("tree_entry_type_or_mode_invalid")
    return entries


def _check_manifest(repo: Path, candidate: dict[str, tuple[str, str, str]]) -> None:
    manifest_entry = candidate.get("bootstrap-manifest.json")
    if manifest_entry is None:
        raise BootstrapError("manifest_missing")
    try:
        manifest = json.loads(_blob(repo, manifest_entry[2]))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BootstrapError("manifest_invalid_json") from exc
    if not isinstance(manifest, dict) or set(manifest) != {
        "schema_version", "source_commit", "initial_main", "imports"
    }:
        raise BootstrapError("manifest_schema_invalid")
    if manifest["schema_version"] != 1:
        raise BootstrapError("manifest_schema_version_invalid")
    if manifest["source_commit"] != SOURCE_COMMIT:
        raise BootstrapError("manifest_source_commit_mismatch")
    if manifest["initial_main"] != INITIAL_MAIN:
        raise BootstrapError("manifest_initial_main_mismatch")
    declared = manifest["imports"]
    if not isinstance(declared, dict) or set(declared) != set(IMPORT_PATHS):
        raise BootstrapError("manifest_import_allowlist_mismatch")

    source = _tree(repo, SOURCE_COMMIT)
    for path in IMPORT_PATHS:
        candidate_mode, candidate_kind, candidate_oid = candidate[path]
        source_entry = source.get(path)
        if source_entry is None or source_entry[:2] != ("100644", "blob"):
            raise BootstrapError("trusted_source_import_missing")
        source_bytes = _blob(repo, source_entry[2])
        candidate_bytes = _blob(repo, candidate_oid)
        expected_digest = hashlib.sha256(source_bytes).hexdigest()
        declaration = declared.get(path)
        if not isinstance(declaration, dict) or set(declaration) != {"mode", "sha256"}:
            raise BootstrapError("manifest_import_entry_invalid")
        if declaration.get("mode") != "100644" or declaration.get("sha256") != expected_digest:
            raise BootstrapError("manifest_import_digest_mismatch")
        if candidate_mode != source_entry[0] or candidate_bytes != source_bytes:
            raise BootstrapError("trusted_import_changed")


def _check_ancestry(repo: Path, base: str, head: str) -> None:
    if not _commit_exists(repo, INITIAL_MAIN):
        raise BootstrapError("initial_main_object_missing")
    if not _commit_exists(repo, base) or not _commit_exists(repo, head):
        raise BootstrapError("base_or_head_commit_missing")
    try:
        _git(repo, "merge-base", "--is-ancestor", INITIAL_MAIN, base)
        _git(repo, "merge-base", "--is-ancestor", base, head)
    except BootstrapError as exc:
        raise BootstrapError("unexpected_commit_ancestry") from exc
    try:
        history = _git(repo, "rev-list", "--topo-order", head, "^" + INITIAL_MAIN).splitlines()
    except BootstrapError as exc:
        raise BootstrapError("history_read_failed") from exc
    for commit in history:
        try:
            _git(repo, "merge-base", "--is-ancestor", INITIAL_MAIN, commit)
        except BootstrapError as exc:
            raise BootstrapError("historical_commit_outside_initial_line") from exc
        entries = _tree(repo, commit)
        for path, (mode, kind, _oid) in entries.items():
            if path not in ALLOWLIST:
                raise BootstrapError("historical_path_outside_allowlist")
            if mode != "100644" or kind != "blob":
                raise BootstrapError("historical_entry_type_or_mode_invalid")
    if base != INITIAL_MAIN:
        _validate_tree(repo, base)


def _changed_path_count(repo: Path, base: str, head: str) -> int:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo), "diff", "--no-ext-diff", "--name-only", "-z", base, head],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=PROCESS_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise BootstrapError("diff_read_failed") from exc
    return len([item for item in completed.stdout.split(b"\0") if item])


def _event_repository_name(obj: Any) -> str | None:
    return obj.get("full_name") if isinstance(obj, dict) else None


def _validate_event(
    repo: Path,
    base: str,
    head: str,
    event: dict[str, Any] | None,
    environment: dict[str, str],
) -> tuple[str | None, str]:
    """Valida contexto de GitHub e retorna SHA da árvore de merge, se houver."""
    if "GITHUB_ACTIONS" not in environment:
        return None, base
    if environment.get("GITHUB_ACTIONS", "").lower() != "true":
        raise BootstrapError("github_actions_context_invalid")
    if event is None:
        event_path = environment.get("GITHUB_EVENT_PATH")
        if not event_path:
            raise BootstrapError("github_event_missing")
        try:
            event = json.loads(Path(event_path).read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise BootstrapError("github_event_invalid") from exc
    if not isinstance(event, dict):
        raise BootstrapError("github_event_invalid")
    repository = environment.get("GITHUB_REPOSITORY")
    event_name = environment.get("GITHUB_EVENT_NAME")
    if not repository or not event_name:
        raise BootstrapError("github_context_incomplete")

    if event_name == "pull_request":
        pr = event.get("pull_request")
        if not isinstance(pr, dict):
            raise BootstrapError("pull_request_event_missing")
        base_info, head_info = pr.get("base"), pr.get("head")
        if not isinstance(base_info, dict) or not isinstance(head_info, dict):
            raise BootstrapError("pull_request_refs_invalid")
        base_ref, head_ref = base_info.get("ref"), head_info.get("ref")
        base_sha, head_sha = base_info.get("sha"), head_info.get("sha")
        if base_sha != base or head_sha != head:
            raise BootstrapError("pull_request_sha_mismatch")
        if _event_repository_name(base_info.get("repo")) != repository:
            raise BootstrapError("pull_request_base_repository_mismatch")
        if _event_repository_name(head_info.get("repo")) != repository:
            raise BootstrapError("pull_request_fork_forbidden")
        allowed_refs = {
            ("main", "integration/pentest-bootstrap", INITIAL_MAIN),
            ("integration/pentest-bootstrap", "feat/pentest-bootstrap", None),
        }
        if not any(
            base_ref == expected_base and head_ref == expected_head
            and (expected_sha is None or base_sha == expected_sha)
            for expected_base, expected_head, expected_sha in allowed_refs
        ):
            raise BootstrapError("pull_request_ref_pair_invalid")
        checkout_sha = environment.get("GITHUB_SHA")
        checked_out = _git(repo, "rev-parse", "HEAD")
        if not _valid_sha(checkout_sha) or checked_out != checkout_sha:
            raise BootstrapError("pull_request_merge_checkout_mismatch")
        parents = _git(repo, "rev-list", "--parents", "-n", "1", checkout_sha).split()[1:]
        if len(parents) != 2 or parents[0] != base_sha or parents[1] != head_sha:
            raise BootstrapError("pull_request_merge_parents_invalid")
        return checkout_sha, base

    if event_name == "push":
        ref = environment.get("GITHUB_REF")
        if ref not in {
            "refs/heads/integration/pentest-bootstrap",
            "refs/heads/main",
        }:
            raise BootstrapError("push_ref_invalid")
        before = event.get("before")
        if not _valid_sha(before) or before == "0" * 40:
            raise BootstrapError("push_before_invalid")
        if base != before:
            raise BootstrapError("push_base_mismatch")
        effective_base = before
        checkout_sha = environment.get("GITHUB_SHA")
        if checkout_sha != head or _git(repo, "rev-parse", "HEAD") != head:
            raise BootstrapError("push_head_mismatch")
        return None, effective_base
    raise BootstrapError("github_event_type_forbidden")


def verify_repository(
    repo: Path,
    base: str,
    head: str,
    *,
    event: dict[str, Any] | None = None,
    environment: dict[str, str] | None = None,
) -> None:
    env = dict(os.environ if environment is None else environment)
    if not _valid_sha(base) or not _valid_sha(head):
        raise BootstrapError("base_or_head_sha_invalid")
    merge_sha, effective_base = _validate_event(repo, base, head, event, env)
    _check_ancestry(repo, effective_base, head)
    if _changed_path_count(repo, effective_base, head) > MAX_FILES:
        raise BootstrapError("base_head_file_limit_exceeded")
    if _changed_path_count(repo, INITIAL_MAIN, head) > MAX_FILES:
        raise BootstrapError("cumulative_file_limit_exceeded")
    candidate = _validate_tree(repo, head)
    _check_manifest(repo, candidate)
    if merge_sha:
        _check_ancestry(repo, effective_base, merge_sha)
        if _changed_path_count(repo, INITIAL_MAIN, merge_sha) > MAX_FILES:
            raise BootstrapError("merge_file_limit_exceeded")
        merged = _validate_tree(repo, merge_sha)
        _check_manifest(repo, merged)


def _npm_expected(lock_bytes: bytes) -> set[tuple[str, str, str]]:
    try:
        lock = json.loads(lock_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BootstrapError("npm_lock_invalid") from exc
    packages = lock.get("packages") if isinstance(lock, dict) else None
    if not isinstance(packages, dict):
        raise BootstrapError("npm_lock_packages_missing")
    expected: set[tuple[str, str, str]] = set()
    for location, info in packages.items():
        if not location:
            continue
        if not isinstance(info, dict):
            raise BootstrapError("npm_lock_package_invalid")
        name = info.get("name")
        if not isinstance(name, str) or not name:
            # npm lock v3 may omit package.name for scoped/nested entries.
            parts = location.split("node_modules/")
            name = parts[-1] if len(parts) > 1 else ""
        version = info.get("version")
        if not name or not isinstance(version, str) or not version:
            raise BootstrapError("npm_lock_package_unpinned")
        expected.add((name, version, "npm"))
    if not expected:
        raise BootstrapError("npm_lock_coverage_empty")
    return expected


def _pypdf_requirement(dockerfile: bytes) -> bytes:
    try:
        text = dockerfile.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BootstrapError("dockerfile_encoding_invalid") from exc
    matches = re.findall(r"(?im)(?:^|\s)pypdf\s*==\s*([A-Za-z0-9.!+_-]+)", text)
    if matches != ["6.21.4"]:
        raise BootstrapError("pypdf_pin_mismatch")
    return b"pypdf==6.21.4\n"


def _scanner_path(path: Path) -> Path:
    tools_dir = (ROOT / ".private" / "tools").resolve()
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise BootstrapError("scanner_missing") from exc
    try:
        resolved.relative_to(tools_dir)
    except ValueError as exc:
        raise BootstrapError("scanner_path_forbidden") from exc
    try:
        if path.is_symlink() or not resolved.is_file() or not os.access(resolved, os.X_OK):
            raise BootstrapError("scanner_file_invalid")
        data = resolved.read_bytes()
    except OSError as exc:
        raise BootstrapError("scanner_read_failed") from exc
    if hashlib.sha256(data).hexdigest() != OSV_SCANNER_SHA256:
        raise BootstrapError("scanner_checksum_mismatch")
    return resolved


def _package_set(output: Any) -> tuple[set[tuple[str, str, str]], int]:
    results = output.get("results") if isinstance(output, dict) else None
    if not isinstance(results, list) or not results:
        raise BootstrapError("scanner_results_missing")
    observed: set[tuple[str, str, str]] = set()
    advisory_ids: set[str] = set()
    for result in results:
        if not isinstance(result, dict) or not isinstance(result.get("packages"), list):
            raise BootstrapError("scanner_result_invalid")
        source = result.get("source")
        if not isinstance(source, dict) or source.get("type") != "lockfile":
            raise BootstrapError("scanner_source_invalid")
        for item in result["packages"]:
            package = item.get("package") if isinstance(item, dict) else None
            if not isinstance(package, dict):
                raise BootstrapError("scanner_package_invalid")
            name, version, ecosystem = (
                package.get("name"), package.get("version"), package.get("ecosystem")
            )
            if (
                not isinstance(name, str) or not name
                or not isinstance(version, str) or not version
                or not isinstance(ecosystem, str) or not ecosystem
            ):
                raise BootstrapError("scanner_package_invalid")
            observed.add((name, version, ecosystem.lower()))
            vulnerabilities = item.get("vulnerabilities", [])
            if not isinstance(vulnerabilities, list):
                raise BootstrapError("scanner_vulnerabilities_invalid")
            for vulnerability in vulnerabilities:
                if not isinstance(vulnerability, dict) or not isinstance(vulnerability.get("id"), str):
                    raise BootstrapError("scanner_vulnerability_invalid")
                advisory_ids.add(vulnerability["id"])
            groups = item.get("groups", [])
            if not isinstance(groups, list):
                raise BootstrapError("scanner_groups_invalid")
            for group in groups:
                identifiers = group.get("ids", []) if isinstance(group, dict) else None
                if not isinstance(identifiers, list):
                    raise BootstrapError("scanner_group_invalid")
                if any(not isinstance(identifier, str) or not identifier for identifier in identifiers):
                    raise BootstrapError("scanner_group_invalid")
                advisory_ids.update(identifiers)
    if not observed:
        raise BootstrapError("scanner_coverage_empty")
    return observed, len(advisory_ids)


def _run_scanner(
    scanner: Path,
    lockfile: Path,
    config: Path,
    temp_home: Path,
    timeout_seconds: int,
) -> tuple[int | None, bytes, bool]:
    command = [
        str(scanner), "scan", "source", "--lockfile", str(lockfile),
        "--format", "json", "--all-packages", "--all-vulns",
        "--verbosity", "error", "--config", str(config),
    ]
    env = {
        "PATH": "/usr/bin:/bin",
        "HOME": str(temp_home),
        "TMPDIR": str(temp_home),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
    }
    try:
        result = subprocess.run(
            command,
            cwd=temp_home,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return None, b"", True
    except OSError:
        return None, b"", False
    # Keep only bounded stdout in memory; output is parsed, never logged.
    if len(result.stdout) > 8 * 1024 * 1024:
        return result.returncode, b"", False
    return result.returncode, result.stdout, False


def _write_report(path: Path, report: dict[str, Any]) -> None:
    payload = (json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if path.exists() and path.is_symlink():
        raise BootstrapError("report_path_symlink_forbidden")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix="bootstrap-report-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    except OSError as exc:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise BootstrapError("report_write_failed") from exc


def run_audit(
    scanner_path: Path,
    report_path: Path,
    *,
    timeout_seconds: int = 90,
) -> int:
    """Executa scan separado para npm lock e o pypdf pin confirmado no Dockerfile."""
    if timeout_seconds < 1 or timeout_seconds > 300:
        raise BootstrapError("scanner_timeout_invalid")
    scanner = _scanner_path(scanner_path)
    npm_path = ROOT / "benchmark" / "pentest" / "package-lock.json"
    dockerfile_path = ROOT / "benchmark" / "pentest" / "runner.Dockerfile"
    try:
        npm_original = npm_path.read_bytes()
        dockerfile_original = dockerfile_path.read_bytes()
    except OSError as exc:
        raise BootstrapError("audit_source_missing") from exc
    npm_expected = _npm_expected(npm_original)
    pypi_lock = _pypdf_requirement(dockerfile_original)
    input_hashes = {
        "npm": hashlib.sha256(npm_original).hexdigest(),
        "pypi": hashlib.sha256(pypi_lock).hexdigest(),
    }
    report_sources: list[dict[str, Any]] = []
    failures: list[str] = []

    with tempfile.TemporaryDirectory(prefix="bootstrap-osv-") as temp_name:
        temp_root = Path(temp_name)
        npm_copy = temp_root / "package-lock.json"
        pypi_copy = temp_root / "requirements.txt"
        config = temp_root / "osv-config.toml"
        npm_copy.write_bytes(npm_original)
        pypi_copy.write_bytes(pypi_lock)
        config.write_text("", encoding="utf-8")
        if hashlib.sha256(npm_copy.read_bytes()).hexdigest() != input_hashes["npm"]:
            raise BootstrapError("npm_lock_copy_mismatch")
        if hashlib.sha256(pypi_copy.read_bytes()).hexdigest() != input_hashes["pypi"]:
            raise BootstrapError("pypi_lock_copy_mismatch")

        for source_name, lockfile, expected in (
            ("npm", npm_copy, npm_expected),
            ("pypi", pypi_copy, {("pypdf", "6.21.4", "pypi")}),
        ):
            code, stdout, timed_out = _run_scanner(
                scanner, lockfile, config, temp_root, timeout_seconds
            )
            advisory_count = 0
            observed_count = 0
            source_failures: list[str] = []
            if timed_out:
                source_failures.append("scanner_timeout")
            elif code is None:
                source_failures.append("scanner_execution_failed")
            elif not stdout:
                source_failures.append("scanner_output_empty")
            else:
                try:
                    output = json.loads(stdout)
                    observed, advisory_count = _package_set(output)
                    observed_count = len(observed)
                    if observed != expected:
                        source_failures.append("package_coverage_mismatch")
                except (UnicodeDecodeError, json.JSONDecodeError, BootstrapError):
                    source_failures.append("scanner_output_invalid")
            if code != 0:
                source_failures.append("scanner_nonzero_exit")
            if advisory_count:
                source_failures.append("advisories_found")
            if code == 0 and advisory_count:
                source_failures.append("scanner_exit_findings_inconsistent")
            if code != 0 and advisory_count == 0 and "scanner_nonzero_exit" in source_failures:
                source_failures.append("scanner_exit_without_findings")
            if source_failures:
                failures.extend(f"{source_name}:{reason}" for reason in source_failures)
            report_sources.append(
                {
                    "source": source_name,
                    "input_sha256": input_hashes[source_name],
                    "expected_package_count": len(expected),
                    "observed_package_count": observed_count,
                    "advisory_count": advisory_count,
                    "status": "fail" if source_failures else "pass",
                    "errors": sorted(set(source_failures)),
                }
            )

        try:
            unchanged = (
                hashlib.sha256(npm_path.read_bytes()).hexdigest() == input_hashes["npm"]
                and hashlib.sha256(dockerfile_path.read_bytes()).hexdigest()
                == hashlib.sha256(dockerfile_original).hexdigest()
            )
        except OSError:
            unchanged = False
        if not unchanged:
            failures.append("source_changed_during_audit")

    final_report = {
        "schema_version": 1,
        "scanner": {"name": "OSV-Scanner", "version": OSV_VERSION, "sha256": OSV_SCANNER_SHA256},
        "sources": report_sources,
        "status": "fail" if failures else "pass",
        "errors": sorted(set(failures)),
    }
    _write_report(report_path, final_report)
    return 1 if failures else 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bootstrap A0: integridade de árvore e dependências")
    commands = parser.add_subparsers(dest="command", required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("--base", required=True)
    verify.add_argument("--head", required=True)
    audit = commands.add_parser("audit")
    audit.add_argument("--scanner", required=True)
    audit.add_argument("--report", required=True)
    return parser


def _audit_failure_report(reason: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "scanner": {"name": "OSV-Scanner", "version": OSV_VERSION, "sha256": OSV_SCANNER_SHA256},
        "sources": [
            {
                "source": source,
                "input_sha256": None,
                "expected_package_count": 0,
                "observed_package_count": 0,
                "advisory_count": 0,
                "status": "fail",
                "errors": [reason],
            }
            for source in ("npm", "pypi")
        ],
        "status": "fail",
        "errors": [reason],
    }


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "verify":
            verify_repository(ROOT, args.base, args.head)
            print("bootstrap tree verified")
            return 0
        return run_audit(Path(args.scanner), Path(args.report))
    except BootstrapError as exc:
        if args.command == "audit":
            try:
                _write_report(Path(args.report), _audit_failure_report(str(exc)))
            except BootstrapError:
                pass
        print(f"bootstrap check failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
