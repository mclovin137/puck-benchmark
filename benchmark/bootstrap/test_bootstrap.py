"""Testes do verificador e da auditoria de dependências do bootstrap."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import tomllib
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "ci" / "bootstrap.py"
SPEC = importlib.util.spec_from_file_location("bootstrap", SCRIPT)
assert SPEC and SPEC.loader
bootstrap = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = bootstrap
SPEC.loader.exec_module(bootstrap)
PINNED_SOURCE_COMMIT = bootstrap.SOURCE_COMMIT
PINNED_INITIAL_MAIN = bootstrap.INITIAL_MAIN

PATCHED_IMPORTS = ("benchmark/pentest/policy.json",)
PATCHED_CONTROL_FILES = (
    "scripts/ci/bootstrap.py",
    "benchmark/bootstrap/test_bootstrap.py",
    "docs/rules.md",
    "docs/verificacao.md",
    "docs/roadmap.md",
    "CHANGELOG.md",
    "docs/bootstrap-security.md",
)


def git(repo: Path, *args: str, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    return result.stdout.strip()


def git_entry(repo: Path, commit: str, relative: str) -> tuple[str, str, str]:
    record = git(repo, "ls-tree", commit, "--", relative)
    mode, kind, oid, _path = record.split(None, 3)
    return mode, kind, oid


def blob(repo: Path, oid: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(repo), "cat-file", "blob", oid])


def _tree_paths(repo: Path, commit: str) -> set[str]:
    return set(git(repo, "ls-tree", "-r", "--name-only", commit).splitlines())


def write_manifest(repo: Path, source: str, initial_main: str) -> None:
    imports = {}
    for relative in bootstrap.IMPORT_PATHS:
        data = (repo / relative).read_bytes()
        imports[relative] = {
            "mode": "100644",
            "sha256": hashlib.sha256(data).hexdigest(),
        }
    (repo / "bootstrap-manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_commit": source,
                "initial_main": initial_main,
                "imports": imports,
            },
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )


class VerifyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.name", "Test")
        git(self.repo, "config", "user.email", "test@example.invalid")

        # A v0.1.0-like main is a populated, closed 30-file tree.
        for relative in bootstrap.ALLOWLIST:
            path = self.repo / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            if relative in bootstrap.IMPORT_PATHS:
                path.write_bytes(("baseline:" + relative + "\n").encode())
            else:
                path.write_text("baseline fixture\n", encoding="utf-8")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "nonempty main baseline")
        self.initial = git(self.repo, "rev-parse", "HEAD")
        bootstrap.INITIAL_MAIN = self.initial

        # The source commit changes only the build-context policy import.
        git(self.repo, "switch", "-qc", "source")
        for relative in PATCHED_IMPORTS:
            path = self.repo / relative
            path.write_bytes(("runtime-fix:" + relative + "\n").encode())
        git(self.repo, "add", *PATCHED_IMPORTS)
        git(self.repo, "commit", "-qm", "trusted source")
        self.source = git(self.repo, "rev-parse", "HEAD")
        bootstrap.SOURCE_COMMIT = self.source

        git(self.repo, "switch", "-q", "--detach", self.initial)
        for relative in PATCHED_IMPORTS:
            path = self.repo / relative
            path.write_bytes(("runtime-fix:" + relative + "\n").encode())
        for relative in PATCHED_CONTROL_FILES:
            path = self.repo / relative
            path.write_text("patch fixture\n", encoding="utf-8")
        write_manifest(self.repo, self.source, self.initial)
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "candidate")
        self.head = git(self.repo, "rev-parse", "HEAD")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def verify(self, head: str | None = None, event=None, base: str | None = None) -> None:
        bootstrap.verify_repository(
            self.repo,
            base or self.initial,
            head or self.head,
            event=event,
            environment={},
        )

    def commit_tree(self, tree: str, *parents: str) -> str:
        command = ["git", "-C", str(self.repo), "commit-tree", tree]
        for parent in parents:
            command.extend(("-p", parent))
        result = subprocess.run(
            command,
            check=True,
            input=b"synthetic merge\n",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return result.stdout.decode("ascii").strip()

    def test_constants_pin_the_new_admitted_source_and_main(self) -> None:
        self.assertEqual(PINNED_SOURCE_COMMIT, "908047555ea8808d7c263f42adb62692a043a225")
        self.assertEqual(PINNED_INITIAL_MAIN, "4c5ff7eb01c439a4d42ee2dbeb6127f6263fedb4")

    def test_accepts_one_import_patch_over_nonempty_main_and_preserves_other_imports(self) -> None:
        self.verify()
        self.assertEqual(len(bootstrap.ALLOWLIST), 30)
        self.assertEqual(len(_tree_paths(self.repo, self.initial)), 30)
        changed = set(git(self.repo, "diff", "--name-only", self.initial, self.head).splitlines())
        changed_imports = changed.intersection(bootstrap.IMPORT_PATHS)
        self.assertEqual(changed_imports, set(PATCHED_IMPORTS))
        self.assertEqual(len(changed), 9)
        for relative in set(bootstrap.IMPORT_PATHS) - set(PATCHED_IMPORTS):
            before = git_entry(self.repo, self.initial, relative)
            after = git_entry(self.repo, self.head, relative)
            self.assertEqual(before[:2], after[:2])
            self.assertEqual(blob(self.repo, before[2]), blob(self.repo, after[2]))

    def test_rejects_source_side_parent_with_forbidden_ancestor(self) -> None:
        git(self.repo, "switch", "-q", "--detach", self.initial)
        forbidden = self.repo / "scenarios" / "hidden" / "app.py"
        forbidden.parent.mkdir(parents=True)
        forbidden.write_text("outside candidate tree\n", encoding="utf-8")
        git(self.repo, "add", "scenarios/hidden/app.py")
        git(self.repo, "commit", "-qm", "forbidden ancestor")

        for relative in bootstrap.IMPORT_PATHS:
            path = self.repo / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(("source:" + relative + "\n").encode())
        git(self.repo, "add", *bootstrap.IMPORT_PATHS)
        git(self.repo, "commit", "-qm", "source descendant of forbidden ancestor")
        source = git(self.repo, "rev-parse", "HEAD")
        bootstrap.SOURCE_COMMIT = source

        git(self.repo, "switch", "-q", "--detach", self.initial)
        for relative in bootstrap.ALLOWLIST:
            path = self.repo / relative
            if relative in bootstrap.IMPORT_PATHS:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(("source:" + relative + "\n").encode())
            elif relative != "bootstrap-manifest.json":
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("fixture\n", encoding="utf-8")
        write_manifest(self.repo, source, self.initial)
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "closed candidate independent from source")
        head = git(self.repo, "rev-parse", "HEAD")
        self.verify(head)

        is_source_ancestor = subprocess.run(
            ["git", "-C", str(self.repo), "merge-base", "--is-ancestor", source, head],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode == 0
        self.assertFalse(is_source_ancestor)
        merge_tree = git(self.repo, "rev-parse", f"{head}^{{tree}}")
        unsafe_merge = self.commit_tree(merge_tree, head, source)

        with self.assertRaises(bootstrap.BootstrapError):
            self.verify(unsafe_merge)

    def test_rejects_extra_path_and_candidate_application_tree(self) -> None:
        (self.repo / "scenarios" / "other" / "app.py").parent.mkdir(
            parents=True, exist_ok=True
        )
        (self.repo / "scenarios" / "other" / "app.py").write_text("x\n")
        git(self.repo, "add", "scenarios/other/app.py")
        git(self.repo, "commit", "-qm", "extra app")
        with self.assertRaises(bootstrap.BootstrapError):
            self.verify(git(self.repo, "rev-parse", "HEAD"))

    def test_rejects_changed_import_even_if_manifest_hash_is_updated(self) -> None:
        relative = bootstrap.IMPORT_PATHS[0]
        (self.repo / relative).write_text("tampered\n", encoding="utf-8")
        write_manifest(self.repo, self.source, self.initial)
        git(self.repo, "add", relative, "bootstrap-manifest.json")
        git(self.repo, "commit", "-qm", "tamper with hash")
        with self.assertRaises(bootstrap.BootstrapError):
            self.verify(git(self.repo, "rev-parse", "HEAD"))

    def test_rejects_missing_allowlisted_file(self) -> None:
        relative = bootstrap.IMPORT_PATHS[2]
        (self.repo / relative).unlink()
        git(self.repo, "add", "-u", relative)
        git(self.repo, "commit", "-qm", "remove import")
        with self.assertRaises(bootstrap.BootstrapError):
            self.verify(git(self.repo, "rev-parse", "HEAD"))

    def test_rejects_symlink_even_when_path_is_allowlisted(self) -> None:
        relative = bootstrap.IMPORT_PATHS[0]
        (self.repo / relative).unlink()
        (self.repo / relative).symlink_to("README.md")
        git(self.repo, "add", relative)
        git(self.repo, "commit", "-qm", "replace import with symlink")
        with self.assertRaises(bootstrap.BootstrapError):
            self.verify(git(self.repo, "rev-parse", "HEAD"))

    def test_rejects_manifest_that_expands_import_allowlist(self) -> None:
        manifest = json.loads((self.repo / "bootstrap-manifest.json").read_text())
        manifest["imports"]["scenarios/escape"] = {"mode": "100644", "sha256": "0" * 64}
        (self.repo / "bootstrap-manifest.json").write_text(json.dumps(manifest))
        git(self.repo, "add", "bootstrap-manifest.json")
        git(self.repo, "commit", "-qm", "expand manifest")
        with self.assertRaises(bootstrap.BootstrapError):
            self.verify(git(self.repo, "rev-parse", "HEAD"))

    def test_rejects_old_source_wrong_manifest_baseline_and_wrong_git_base(self) -> None:
        manifest = json.loads((self.repo / "bootstrap-manifest.json").read_text())
        manifest["source_commit"] = "219d50f920ba9fbcd107e202d5661185d11e5676"
        (self.repo / "bootstrap-manifest.json").write_text(json.dumps(manifest))
        git(self.repo, "add", "bootstrap-manifest.json")
        git(self.repo, "commit", "-qm", "use old source pin")
        with self.assertRaises(bootstrap.BootstrapError):
            self.verify(git(self.repo, "rev-parse", "HEAD"))

        manifest = json.loads((self.repo / "bootstrap-manifest.json").read_text())
        manifest["source_commit"] = self.source
        manifest["initial_main"] = "c5d985cbb5adff2983325bc3feeb4c90856d2b3a"
        (self.repo / "bootstrap-manifest.json").write_text(json.dumps(manifest))
        git(self.repo, "add", "bootstrap-manifest.json")
        git(self.repo, "commit", "-qm", "use old base pin")
        bad_head = git(self.repo, "rev-parse", "HEAD")
        with self.assertRaises(bootstrap.BootstrapError):
            self.verify(bad_head)

        with self.assertRaises(bootstrap.BootstrapError):
            self.verify(bad_head, base=self.source)

    def test_rejects_test_merge_with_extra_path(self) -> None:
        extra = self.repo / "scenarios" / "unexpected" / "app.py"
        extra.parent.mkdir(parents=True)
        extra.write_text("not allowed in test merge\n", encoding="utf-8")
        git(self.repo, "add", "scenarios/unexpected/app.py")
        merge_tree = git(self.repo, "write-tree")
        bad_merge = self.commit_tree(merge_tree, self.initial, self.head)
        git(self.repo, "switch", "-q", "--detach", bad_merge)
        event = {
            "pull_request": {
                "base": {"ref": "integration/pentest-bootstrap", "sha": self.initial,
                         "repo": {"full_name": "owner/project"}},
                "head": {"ref": "fix/pentest-c1-build-context", "sha": self.head,
                         "repo": {"full_name": "owner/project"}},
            }
        }
        env = {
            "GITHUB_ACTIONS": "true", "GITHUB_EVENT_NAME": "pull_request",
            "GITHUB_REPOSITORY": "owner/project", "GITHUB_SHA": bad_merge,
        }
        with self.assertRaises(bootstrap.BootstrapError):
            bootstrap.verify_repository(
                self.repo, self.initial, self.head, event=event, environment=env
            )

    def test_rejects_pull_request_from_fork_and_wrong_refs(self) -> None:
        event = {
            "pull_request": {
                "base": {"ref": "integration/pentest-bootstrap", "sha": self.initial,
                         "repo": {"full_name": "owner/project"}},
                "head": {"ref": "fix/pentest-c1-build-context", "sha": self.head,
                         "repo": {"full_name": "fork/project"}},
            }
        }
        env = {
            "GITHUB_ACTIONS": "true",
            "GITHUB_EVENT_NAME": "pull_request",
            "GITHUB_REPOSITORY": "owner/project",
        }
        with self.assertRaises(bootstrap.BootstrapError):
            bootstrap._validate_event(self.repo, self.initial, self.head, event, env)

        event["pull_request"]["head"]["repo"]["full_name"] = "owner/project"
        event["pull_request"]["base"]["ref"] = "dev"
        with self.assertRaises(bootstrap.BootstrapError):
            bootstrap._validate_event(self.repo, self.initial, self.head, event, env)

    def test_push_uses_event_before_and_rejects_branch_creation(self) -> None:
        zero = "0" * 40
        env = {
            "GITHUB_ACTIONS": "true",
            "GITHUB_EVENT_NAME": "push",
            "GITHUB_REPOSITORY": "owner/project",
            "GITHUB_REF": "refs/heads/integration/pentest-bootstrap",
            "GITHUB_SHA": self.head,
        }
        event = {"before": self.initial}
        self.assertEqual(
            bootstrap._validate_event(self.repo, self.initial, self.head, event, env),
            (None, self.initial),
        )
        event["before"] = zero
        with self.assertRaises(bootstrap.BootstrapError):
            bootstrap._validate_event(self.repo, zero, self.head, event, env)

    def test_accepts_task_promotion_and_push_commit_graphs(self) -> None:
        tree = git(self.repo, "rev-parse", f"{self.head}^{{tree}}")
        task_merge = self.commit_tree(tree, self.initial, self.head)
        git(self.repo, "switch", "-q", "--detach", task_merge)

        pr_event = {
            "pull_request": {
                "base": {"ref": "integration/pentest-bootstrap", "sha": self.initial,
                         "repo": {"full_name": "owner/project"}},
                "head": {"ref": "fix/pentest-c1-build-context", "sha": self.head,
                         "repo": {"full_name": "owner/project"}},
            }
        }
        pr_env = {
            "GITHUB_ACTIONS": "true", "GITHUB_EVENT_NAME": "pull_request",
            "GITHUB_REPOSITORY": "owner/project", "GITHUB_SHA": task_merge,
        }
        bootstrap.verify_repository(
            self.repo, self.initial, self.head, event=pr_event, environment=pr_env
        )

        push_event = {"before": self.initial}
        push_env = {
            "GITHUB_ACTIONS": "true", "GITHUB_EVENT_NAME": "push",
            "GITHUB_REPOSITORY": "owner/project",
            "GITHUB_REF": "refs/heads/integration/pentest-bootstrap",
            "GITHUB_SHA": task_merge,
        }
        bootstrap.verify_repository(
            self.repo, self.initial, task_merge, event=push_event, environment=push_env
        )

        promotion_merge = self.commit_tree(tree, self.initial, task_merge)
        git(self.repo, "switch", "-q", "--detach", promotion_merge)
        promotion_event = {
            "pull_request": {
                "base": {"ref": "main", "sha": self.initial,
                         "repo": {"full_name": "owner/project"}},
                "head": {"ref": "integration/pentest-bootstrap", "sha": task_merge,
                         "repo": {"full_name": "owner/project"}},
            }
        }
        promotion_env = dict(pr_env, GITHUB_SHA=promotion_merge)
        bootstrap.verify_repository(
            self.repo, self.initial, task_merge,
            event=promotion_event, environment=promotion_env,
        )


class AuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "benchmark" / "pentest").mkdir(parents=True)
        (self.root / "benchmark" / "pentest" / "package-lock.json").write_text(
            json.dumps({"lockfileVersion": 3, "packages": {
                "": {"name": "fixture", "version": "1.0.0"},
                "node_modules/a": {"name": "a", "version": "1.2.3"},
                "node_modules/optional": {"name": "optional", "version": "4.5.6", "optional": True},
            }}),
            encoding="utf-8",
        )
        (self.root / "benchmark" / "pentest" / "runner.Dockerfile").write_text(
            "RUN pip install --no-cache-dir pypdf==6.21.4\n", encoding="utf-8"
        )
        self.bin_dir = self.root / ".private" / "tools"
        self.bin_dir.mkdir(parents=True)
        self.scanner = self.bin_dir / "osv-scanner"
        self.scanner.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        self.scanner.chmod(0o755)
        bootstrap.ROOT = self.root
        bootstrap.OSV_SCANNER_SHA256 = hashlib.sha256(self.scanner.read_bytes()).hexdigest()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def scanner_with(self, outputs: list[dict], codes: list[int] | None = None) -> Path:
        codes = codes or [0] * len(outputs)
        body = "import json, pathlib, sys, tomllib\nargs = sys.argv\nlock = next(args[i+1] for i,x in enumerate(args[:-1]) if x == '--lockfile')\n"
        body += "required = ['scan', 'source', '--format', 'json', '--all-packages', '--all-vulns', '--verbosity', 'error', '--config']\n"
        body += "assert all(x in args for x in required)\nassert pathlib.Path(lock).parent == pathlib.Path.cwd()\n"
        body += "config = pathlib.Path(args[args.index('--config')+1])\nassert config.suffix == '.toml'\n"
        body += "assert tomllib.loads(config.read_text()) == {}\n"
        body += "items = " + repr(outputs) + "\n"
        body += "codes = " + repr(codes) + "\n"
        body += "index = 0 if lock.endswith('package-lock.json') else 1\n"
        body += "for result in items[index]['results']:\n source = result['source']\n if source.get('path') == '__LOCKFILE__': source['path'] = lock\n elif source.get('path') == '__OTHER__': source['path'] = lock + '.other'\n"
        body += "print(json.dumps(items[index]))\nsys.exit(codes[index])\n"
        script = "#!/usr/bin/env python3\n" + body
        self.scanner.write_text(script, encoding="utf-8")
        self.scanner.chmod(0o755)
        bootstrap.OSV_SCANNER_SHA256 = hashlib.sha256(self.scanner.read_bytes()).hexdigest()
        return self.scanner

    @staticmethod
    def clean_result(*packages, source_type="lockfile", source_path="__LOCKFILE__"):
        return {"results": [{"source": {"type": source_type, "path": source_path}, "packages": [
            {"package": {"name": name, "version": version, "ecosystem": ecosystem}}
            for name, version, ecosystem in packages
        ]}]}

    def run_audit(self, report: Path, codes: list[int] | None = None, npm_output=None, pypi_output=None) -> int:
        npm = npm_output or self.clean_result(("a", "1.2.3", "npm"), ("optional", "4.5.6", "npm"))
        pypi = pypi_output or {
            "results": (
                self.clean_result(("pypdf", "6.21.4", "PyPI"))["results"]
                + self.clean_result(("typing-extensions", "4.9.0", "PyPI"), source_type="unknown")["results"]
            )
        }
        self.scanner_with([npm, pypi], codes)
        return bootstrap.run_audit(self.scanner, report, timeout_seconds=2)

    def test_includes_optional_npm_packages_and_extracted_pdf_constraint(self) -> None:
        report = self.root / "report.json"
        code = self.run_audit(report)
        self.assertEqual(code, 0)
        data = json.loads(report.read_text(encoding="utf-8"))
        self.assertEqual(data["status"], "pass")
        self.assertEqual({item["source"] for item in data["sources"]}, {"npm", "pypi"})
        self.assertEqual(data["sources"][0]["observed_package_count"], 2)
        self.assertNotIn(str(self.root), report.read_text(encoding="utf-8"))

    def test_findings_fail_closed_even_when_scanner_returns_zero(self) -> None:
        report = self.root / "report.json"
        npm = self.clean_result(("a", "1.2.3", "npm"), ("optional", "4.5.6", "npm"))
        npm["results"][0]["packages"][0]["vulnerabilities"] = [{"id": "GHSA-private"}]
        code = self.run_audit(report, npm_output=npm)
        self.assertNotEqual(code, 0)
        self.assertEqual(json.loads(report.read_text())["status"], "fail")
        self.assertNotIn("GHSA-private", report.read_text())

    def test_scanner_nonzero_fails_without_leaking_output(self) -> None:
        report = self.root / "report.json"
        code = self.run_audit(report, codes=[1, 0])
        self.assertNotEqual(code, 0)
        self.assertEqual(json.loads(report.read_text())["status"], "fail")

    def test_invalid_json_and_incomplete_coverage_fail_closed(self) -> None:
        report = self.root / "report.json"
        self.scanner.write_text("#!/bin/sh\nprintf 'not-json\\n'\n", encoding="utf-8")
        self.scanner.chmod(0o755)
        bootstrap.OSV_SCANNER_SHA256 = hashlib.sha256(self.scanner.read_bytes()).hexdigest()
        self.assertNotEqual(bootstrap.run_audit(self.scanner, report, timeout_seconds=2), 0)
        self.assertEqual(json.loads(report.read_text())["status"], "fail")

        incomplete = self.clean_result(("a", "1.2.3", "npm"))
        self.scanner_with([incomplete, self.clean_result(("pypdf", "6.21.4", "PyPI"))])
        self.assertNotEqual(bootstrap.run_audit(self.scanner, report, timeout_seconds=2), 0)

    def test_pypi_unknown_supplement_is_narrow_and_fail_closed(self) -> None:
        report = self.root / "report.json"
        unknown_npm = self.clean_result(("typing-extensions", "4.9.0", "npm"), source_type="unknown")
        self.assertNotEqual(self.run_audit(report, npm_output={"results": unknown_npm["results"]}), 0)

        other_path = self.clean_result(("typing-extensions", "4.9.0", "PyPI"), source_type="unknown", source_path="__OTHER__")
        self.assertNotEqual(self.run_audit(report, pypi_output={"results": [
            self.clean_result(("pypdf", "6.21.4", "PyPI"))["results"][0],
            other_path["results"][0],
        ]}), 0)

        missing_primary = {"results": self.clean_result(("pypdf", "6.21.4", "PyPI"), source_type="unknown")["results"]}
        self.assertNotEqual(self.run_audit(report, pypi_output=missing_primary), 0)

        advisory_supplement = self.clean_result(("typing-extensions", "4.9.0", "PyPI"), source_type="unknown")
        advisory_supplement["results"][0]["packages"][0]["vulnerabilities"] = [{"id": "GHSA-supplement"}]
        with_advisory = {"results": [
            self.clean_result(("pypdf", "6.21.4", "PyPI"))["results"][0],
            advisory_supplement["results"][0],
        ]}
        self.assertNotEqual(self.run_audit(report, pypi_output=with_advisory), 0)

        wrong_ecosystem = self.clean_result(("typing-extensions", "4.9.0", "npm"), source_type="unknown")
        mismatch = {"results": [
            self.clean_result(("pypdf", "6.21.4", "PyPI"))["results"][0],
            wrong_ecosystem["results"][0],
        ]}
        self.assertNotEqual(self.run_audit(report, pypi_output=mismatch), 0)

    def test_scanner_must_be_under_private_tools_and_checksum_pinned(self) -> None:
        outside = self.root / "outside"
        outside.write_text("#!/bin/sh\nexit 0\n")
        outside.chmod(0o755)
        with self.assertRaises(bootstrap.BootstrapError):
            bootstrap.run_audit(outside, self.root / "report.json", timeout_seconds=1)

    def test_early_audit_failure_still_writes_per_source_sanitized_report(self) -> None:
        outside = self.root / "outside"
        outside.write_text("#!/bin/sh\nexit 0\n")
        outside.chmod(0o755)
        report = self.root / "report.json"
        with redirect_stderr(StringIO()):
            code = bootstrap.main(["audit", "--scanner", str(outside), "--report", str(report)])
        self.assertEqual(code, 1)
        data = json.loads(report.read_text(encoding="utf-8"))
        self.assertEqual({source["source"] for source in data["sources"]}, {"npm", "pypi"})
        self.assertTrue(all(source["status"] == "fail" for source in data["sources"]))
        self.assertNotIn(str(self.root), report.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
