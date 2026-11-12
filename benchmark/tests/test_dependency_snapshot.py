import datetime as dt
import hashlib
import importlib.util
import json
import marshal
import struct
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts/ci/dependency_snapshot.py"
SPEC = importlib.util.spec_from_file_location("dependency_snapshot", MODULE_PATH)
snapshot = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = snapshot
SPEC.loader.exec_module(snapshot)


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip()


def new_repo(path):
    path.mkdir(parents=True)
    subprocess.run(["git", "init", "--quiet", str(path)], check=True)
    git(path, "config", "user.name", "fixture")
    git(path, "config", "user.email", "fixture@example.invalid")
    return path


def add_and_commit(root):
    git(root, "add", "--all")
    git(root, "commit", "--quiet", "-m", "fixture")
    return git(root, "rev-parse", "HEAD")


class DependencySnapshotTests(unittest.TestCase):
    def setUp(self):
        fixed = dt.datetime(2026, 11, 12, 12, tzinfo=dt.timezone.utc)

        class FixtureDateTime(dt.datetime):
            @classmethod
            def now(cls, tz=None):
                return fixed.replace(tzinfo=None) if tz is None else fixed.astimezone(tz)

        clock = patch.object(snapshot, "dt", SimpleNamespace(
            datetime=FixtureDateTime, timezone=dt.timezone, timedelta=dt.timedelta))
        clock.start()
        self.addCleanup(clock.stop)
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.source = new_repo(self.base / "source")
        self.trusted = new_repo(self.base / "trusted")
        for root in (self.source, self.trusted):
            self._write_snapshot_files(root)
        self.source_sha = add_and_commit(self.source)
        self.trusted_sha = add_and_commit(self.trusted)

    def tearDown(self):
        self.tmp.cleanup()

    @staticmethod
    def _write_snapshot_files(root):
        paths = [
            "scenarios/c1-specialists-economy/backend/pom.xml",
            "experiment/configs.yaml", "experiment/amendments/A-002.json",
            "benchmark/scripts/run_system_evaluation.py", "scripts/pentest/preflight.py",
            "benchmark/pentest/policy.json", ".github/workflows/ci.yml",
            ".github/workflows/pentest.yml", "scripts/ci/dependency-audit.py",
            "scripts/ci/dependency_snapshot.py", "benchmark/scripts/install_tools.py",
        ]
        for relative in paths:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("fixture\n", encoding="utf-8")

    @staticmethod
    def tree_node(name, version, children=None):
        value = {"groupId": "org.example", "artifactId": name, "version": version,
                 "type": "jar", "scope": "compile", "classifier": "", "optional": "false"}
        if children is not None:
            value["children"] = children
        return value

    def test_canonical_maven_graph_sorts_children_recursively_and_omits_empty(self):
        left = self.tree_node("b", "1", [self.tree_node("z", "1"), self.tree_node("a", "1", [])])
        right = self.tree_node("a", "1")
        first = self.tree_node("root", "1", [left, right])
        second = self.tree_node("root", "1", [right, left])
        canonical, nodes, edges, spring = snapshot.canonical_maven_tree(first)
        canonical2, _, _, _ = snapshot.canonical_maven_tree(second)
        self.assertEqual(canonical, canonical2)
        self.assertEqual((nodes, edges, spring), (5, 4, []))
        self.assertNotIn(b'"children":[]', canonical)

    def test_maven_graph_rejects_extra_fields_wrong_types_and_malformed_children(self):
        valid = self.tree_node("root", "1")
        for invalid in ({**valid, "downloadUrl": "https://invalid"},
                        {**valid, "version": 1}, {**valid, "children": {}},
                        {key: value for key, value in valid.items() if key != "scope"}):
            with self.subTest(invalid=invalid):
                with self.assertRaises(snapshot.SnapshotError):
                    snapshot.canonical_maven_tree(invalid)

    def test_maven_graph_uses_only_copied_pom_and_ignores_candidate_mvn_config(self):
        backend = self.source / snapshot.SCENARIO_DIRS["C1"] / "backend"
        pom = backend / "pom.xml"
        pom.parent.mkdir(parents=True, exist_ok=True)
        pom.write_text("<project>fixture</project>\n", encoding="utf-8")
        (backend / ".mvn").mkdir()
        (backend / ".mvn/extensions.xml").write_text("untrusted extension marker", encoding="utf-8")
        tree = {**self.tree_node("spring-webmvc", "6.2.19"), "groupId": "org.springframework"}
        calls = []

        def fake_run(args, **kwargs):
            calls.append((args, kwargs))
            isolated_project = kwargs["cwd"]
            output_arg = next(item for item in args if item.startswith("-DoutputFile="))
            Path(output_arg.split("=", 1)[1]).write_text(json.dumps(tree), encoding="utf-8")
            self.assertNotEqual(isolated_project, backend)
            self.assertEqual((Path(isolated_project) / "pom.xml").read_bytes(), pom.read_bytes())
            self.assertFalse((Path(isolated_project) / ".mvn").exists())
            self.assertEqual(kwargs["env"]["MAVEN_PROJECTBASEDIR"], str(isolated_project))
            self.assertEqual(kwargs["stdin"], subprocess.DEVNULL)
            return SimpleNamespace(returncode=0)

        with patch.object(snapshot.subprocess, "run", side_effect=fake_run):
            graph_sha, pom_sha = snapshot._maven_tree(self.source, "C1")
        canonical = snapshot.canonical_maven_tree(tree)[0]
        self.assertEqual(graph_sha, hashlib.sha256(canonical).hexdigest())
        self.assertEqual(pom_sha, hashlib.sha256(pom.read_bytes()).hexdigest())
        self.assertEqual(calls[0][0][0:3], ["mvn", "-B", "--no-transfer-progress"])
        self.assertFalse(any(str(backend / ".mvn") in arg for arg in calls[0][0]))

    def test_source_digest_covers_tracked_scope_and_rejects_dirty_or_untracked(self):
        original = snapshot.measure_source_sha256(self.source, "C1")
        target = self.source / "scenarios/c1-specialists-economy/backend/pom.xml"
        target.write_text("changed\n", encoding="utf-8")
        with self.assertRaises(snapshot.SnapshotError):
            snapshot.measure_source_sha256(self.source, "C1")
        target.write_text("fixture\n", encoding="utf-8")
        added = self.source / "scenarios/c1-specialists-economy/backend/new.txt"
        added.write_text("new tracked input\n", encoding="utf-8")
        with self.assertRaises(snapshot.SnapshotError):
            snapshot.measure_source_sha256(self.source, "C1")
        git(self.source, "add", "--all")
        git(self.source, "commit", "--quiet", "-m", "new tracked file")
        self.assertNotEqual(original, snapshot.measure_source_sha256(self.source, "C1"))

    def test_snapshot_rejects_symlink_even_when_tracked(self):
        path = self.source / "scenarios/c1-specialists-economy/backend/alias"
        path.symlink_to("pom.xml")
        git(self.source, "add", "--all")
        git(self.source, "commit", "--quiet", "-m", "symlink")
        with self.assertRaises(snapshot.SnapshotError):
            snapshot.measure_source_sha256(self.source, "C1")

    def test_path_traversal_absolute_and_windows_paths_are_rejected(self):
        for path in ("../outside", "/absolute/file", "a\\b", "a//b", ":(glob)*"):
            with self.subTest(path=path), self.assertRaises(snapshot.SnapshotError):
                snapshot._git_path(path)

    def test_trusted_checkout_requires_exact_sha_clean_code_and_separate_roots(self):
        evaluator = self.trusted / "scripts/ci/dependency-audit.py"
        helper = self.trusted / "scripts/ci/dependency_snapshot.py"
        result = snapshot.verify_trusted_checkout(self.trusted, self.trusted_sha,
                                                  self.source, evaluator, helper)
        self.assertEqual(result, (self.source.resolve(), self.trusted.resolve()))
        with self.assertRaises(snapshot.SnapshotError):
            snapshot.verify_trusted_checkout(self.trusted, "0" * 40, self.source, evaluator, helper)
        with self.assertRaises(snapshot.SnapshotError):
            snapshot.verify_trusted_checkout(self.trusted, self.trusted_sha, self.trusted, evaluator, helper)

    def test_trusted_code_modification_or_candidate_file_cannot_be_loaded(self):
        helper = self.trusted / "scripts/ci/dependency_snapshot.py"
        helper.write_text("candidate replacement\n", encoding="utf-8")
        with self.assertRaises(snapshot.SnapshotError):
            snapshot.verify_trusted_checkout(self.trusted, self.trusted_sha, self.source,
                                             self.trusted / "scripts/ci/dependency-audit.py", helper)
        outside = self.source / "scripts/ci/dependency-audit.py"
        outside.parent.mkdir(parents=True, exist_ok=True)
        outside.write_text("candidate evaluator", encoding="utf-8")
        with self.assertRaises(snapshot.SnapshotError):
            snapshot.verify_trusted_checkout(self.trusted, self.trusted_sha, self.source,
                                             outside, self.trusted / "scripts/ci/dependency_snapshot.py")

    def test_scanner_binary_is_measured_and_changed_bytes_block(self):
        scanner_path = self.trusted / ".private/tools/osv-scanner"
        scanner_path.parent.mkdir(parents=True)
        scanner_path.write_bytes(b"trusted scanner fixture")
        measured = hashlib.sha256(scanner_path.read_bytes()).hexdigest()
        with patch.object(snapshot, "SCANNER_SHA256", measured):
            self.assertEqual(snapshot.measure_scanner_binary(self.trusted, scanner_path), measured)
            scanner_path.write_bytes(b"modified scanner fixture")
            with self.assertRaisesRegex(snapshot.SnapshotError, "digest real"):
                snapshot.measure_scanner_binary(self.trusted, scanner_path)
            scanner_path.unlink()
            scanner_path.symlink_to(self.source / "candidate-bin")
            with self.assertRaises(snapshot.SnapshotError):
                snapshot.measure_scanner_binary(self.trusted, scanner_path)

    def test_candidate_policy_is_ignored_and_only_trusted_policy_is_read(self):
        trusted_policy = self.trusted / snapshot.POLICY_PATH
        source_policy = self.source / snapshot.POLICY_PATH
        trusted_policy.parent.mkdir(parents=True, exist_ok=True)
        source_policy.parent.mkdir(parents=True, exist_ok=True)
        trusted_policy.write_text('{"status":"proposed"}\n', encoding="utf-8")
        source_policy.write_text('{"status":"active","records":["candidate"]}\n', encoding="utf-8")
        self.trusted_sha = add_and_commit(self.trusted)
        policy, _ = snapshot.read_trusted_policy(self.trusted, self.trusted_sha)
        self.assertEqual(policy["status"], "proposed")
        self.assertEqual(len(policy), 1)

    def test_advisory_digest_uses_only_canonical_security_fields(self):
        vuln = {"id": "GHSA-j9f9-w8pj-32f8", "modified": "2026-11-01T00:00:00Z",
                "affected": [{"ranges": [{"events": [{"introduced": "0"}]}]}],
                "severity": [{"type": "CVSS_V3", "score": "9.8"}],
                "database_specific": {"severity": "CRITICAL"}, "summary": "ignored text",
                "references": [{"url": "https://invalid"}]}
        digest = snapshot.advisory_sha256(vuln)
        vuln["summary"] = "changed text"
        vuln["references"] = []
        self.assertEqual(snapshot.advisory_sha256(vuln), digest)
        vuln["severity"][0]["score"] = "7.5"
        self.assertNotEqual(snapshot.advisory_sha256(vuln), digest)
        with self.assertRaises(snapshot.SnapshotError):
            snapshot.advisory_sha256({"id": "GHSA-incomplete"})

    def test_policy_requires_exact_eight_records_and_measured_bindings(self):
        evidence = self.trusted / "experiment/evaluation/evidence.md"
        evidence.parent.mkdir(parents=True, exist_ok=True)
        evidence.write_text("neo evidence\n", encoding="utf-8")
        self.trusted_sha = add_and_commit(self.trusted)
        evidence_sha = hashlib.sha256(evidence.read_bytes()).hexdigest()
        source_hashes = {scenario: hashlib.sha256(scenario.encode()).hexdigest() for scenario in snapshot.SCENARIO_DIRS}
        graph_hashes = {scenario: hashlib.sha256((scenario + "-graph").encode()).hexdigest() for scenario in snapshot.SCENARIO_DIRS}
        installer_sha = hashlib.sha256((self.trusted / snapshot.INSTALLER_PATH).read_bytes()).hexdigest()
        scanner_sha = snapshot.SCANNER_SHA256
        policy = self._policy(source_hashes, graph_hashes, installer_sha, evidence_sha)
        now = dt.datetime(2026, 11, 12, 12, tzinfo=dt.timezone.utc)
        with patch.object(snapshot, "SCANNER_SHA256", scanner_sha):
            digest, records = snapshot._validate_policy(policy, scanner_sha, installer_sha, source_hashes,
                                                       graph_hashes, self.trusted, self.trusted_sha, now)
        self.assertEqual(len(records), 8)
        self.assertEqual(len(digest), 64)
        identity = ("C1", "Maven", snapshot.EXPECTED_PACKAGE[1], snapshot.EXPECTED_PACKAGE[2],
                    "GHSA-j9f9-w8pj-32f8")
        matched = records[identity]
        authorization = snapshot.SnapshotAuthorization(
            self.trusted_sha, digest, scanner_sha, installer_sha, source_hashes, graph_hashes, records,
            "2026-11-20T00:00:00Z", self.source, self.trusted, self.trusted / ".private/tools/osv-scanner",
            self.trusted / "scripts/ci/dependency-audit.py", self.trusted / "scripts/ci/dependency_snapshot.py")
        finding = {"id": identity[-1], "ecosystem": "Maven", "package": identity[2],
                   "version": identity[3], "severity": "CRITICAL",
                   "advisory_sha256": matched["advisory_sha256"]}
        decision = snapshot.decision_for(authorization, "C1", finding)
        self.assertEqual(decision["decision"], "not_reachable_in_reviewed_snapshot")
        self.assertEqual(decision["risk_residual"], matched["risk_residual"])
        for change in ({"severity": "UNKNOWN"}, {"severity": "HIGH"},
                       {"package": "different"}, {"version": "6.2.20"},
                       {"advisory_sha256": "0" * 64}):
            candidate = {**finding, **change}
            with self.subTest(change=change):
                self.assertIsNone(snapshot.decision_for(authorization, "C1", candidate))
        self.assertIsNone(snapshot.decision_for(authorization, "C5", finding))
        authorization_expired = snapshot.SnapshotAuthorization(
            self.trusted_sha, digest, scanner_sha, installer_sha, source_hashes, graph_hashes, records,
            "2026-11-12T11:59:59Z", self.source, self.trusted, self.trusted / ".private/tools/osv-scanner",
            self.trusted / "scripts/ci/dependency-audit.py", self.trusted / "scripts/ci/dependency_snapshot.py")
        self.assertIsNone(snapshot.decision_for(authorization_expired, "C1", finding))
        for mutate in (lambda value: value["records"].pop(),
                       lambda value: value["records"].append(dict(value["records"][0])),
                       lambda value: value.update(status="revoked"),
                       lambda value: value.update(status="proposed"),
                       lambda value: value.update(expires_at="2026-12-20T00:00:00Z"),
                       lambda value: value["records"][0].update(source_sha256="0" * 64),
                       lambda value: value["records"][0].update(graph_sha256="0" * 64),
                       lambda value: value["records"][0].update(reviewer="other"),
                       lambda value: value["records"][0].update(status="revoked")):
            candidate = json.loads(json.dumps(policy))
            mutate(candidate)
            with self.subTest(mutate=mutate), self.assertRaises(snapshot.SnapshotError):
                snapshot._validate_policy(candidate, scanner_sha, installer_sha, source_hashes,
                                          graph_hashes, self.trusted, self.trusted_sha, now)

    def test_policy_evidence_absent_or_digest_mismatch_cannot_authorize(self):
        source_hashes = {scenario: hashlib.sha256(scenario.encode()).hexdigest() for scenario in snapshot.SCENARIO_DIRS}
        graph_hashes = {scenario: hashlib.sha256((scenario + "-graph").encode()).hexdigest() for scenario in snapshot.SCENARIO_DIRS}
        evidence = self.trusted / "experiment/evaluation/evidence.md"
        evidence.parent.mkdir(parents=True, exist_ok=True)
        evidence.write_text("evidence\n", encoding="utf-8")
        self.trusted_sha = add_and_commit(self.trusted)
        installer_sha = hashlib.sha256((self.trusted / snapshot.INSTALLER_PATH).read_bytes()).hexdigest()
        policy = self._policy(source_hashes, graph_hashes, installer_sha, "0" * 64)
        now = dt.datetime(2026, 11, 12, 12, tzinfo=dt.timezone.utc)
        with self.assertRaises(snapshot.SnapshotError):
            snapshot._validate_policy(policy, snapshot.SCANNER_SHA256, installer_sha, source_hashes,
                                      graph_hashes, self.trusted, self.trusted_sha, now)

    def _complete_fixture(self):
        for root in (self.source, self.trusted):
            for directory in snapshot.SCENARIO_DIRS.values():
                for relative in ("backend/pom.xml", "frontend/package-lock.json"):
                    file = root / directory / relative
                    file.parent.mkdir(parents=True, exist_ok=True)
                    file.write_text("fixture\n", encoding="utf-8")
            (root / "benchmark/requirements.txt").write_text("fixture==1\n")
            (root / "experiment/dependency-triage.json").write_text("[]\n")
            (root / ".gitignore").write_text(".private/\n__pycache__/\n")
            add_and_commit(root)
        scanner = self.trusted / ".private/tools/osv-scanner"
        scanner.parent.mkdir(parents=True)
        scanner.write_bytes(b"scanner fixture\n")
        evidence = self.trusted / "experiment/evaluation/evidence.md"
        evidence.parent.mkdir(parents=True, exist_ok=True)
        evidence.write_text("Independent fixture evidence\n")
        leaf = {**self.tree_node("spring-webmvc", "6.2.19"), "groupId": "org.springframework"}
        tree = self.tree_node("application", "1", [leaf])
        graph_digest = hashlib.sha256(json.dumps(
            tree, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        graph_records = []
        for scenario, directory in snapshot.SCENARIO_DIRS.items():
            relative = f"experiment/evaluation/dependency-graphs/{scenario.lower()}.json"
            file = self.trusted / relative
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(json.dumps(tree))
            graph_records.append({
                "scenario": scenario, "source_directory": directory + "/backend",
                "scenario_git_tree": git(self.trusted, "rev-parse", f"HEAD:{directory}"),
                "source_pom_sha256": hashlib.sha256((self.source / directory / "backend/pom.xml").read_bytes()).hexdigest(),
                "tree_file": relative, "canonical_tree_sha256": graph_digest,
                "reported_nodes": 2, "reported_edges": 1, "spring_webmvc_versions": ["6.2.19"],
            })
        graph_manifest = {"tool": snapshot.TREE_TOOL, "format": "json",
                          "canonicalization": "Recursively sort child nodes by canonical JSON; preserve string fields; JSON sort_keys=true, separators comma/colon, UTF-8. Optional children omitted when empty.",
                          "records": graph_records}
        (self.trusted / snapshot.GRAPH_MANIFEST_PATH).write_text(json.dumps(graph_manifest))
        advisory_records = []
        advisory_hashes = {}
        for advisory in sorted(snapshot.ADVISORIES):
            data = {"id": advisory, "modified": "2026-11-01T00:00:00Z",
                    "affected": [{"package": {"ecosystem": "Maven", "name": snapshot.EXPECTED_PACKAGE[1]},
                                  "versions": ["6.2.19"]}],
                    "severity": [], "database_specific": {"severity": "CRITICAL"}}
            digest = hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            advisory_hashes[advisory] = digest
            file = self.trusted / f"experiment/evaluation/dependency-advisories/{advisory}.json"
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(json.dumps(data))
            advisory_records.append({"advisory": advisory, "modified": data["modified"],
                                     "security_fields_sha256": digest})
        advisory_manifest = self.trusted / snapshot.ADVISORY_MANIFEST_PATH
        advisory_manifest.write_text(json.dumps({"records": advisory_records}))
        sources = {scenario: snapshot.measure_source_sha256(self.source, scenario)
                   for scenario in snapshot.SCENARIO_DIRS}
        graphs = {scenario: graph_digest for scenario in snapshot.SCENARIO_DIRS}
        installer_sha = hashlib.sha256((self.trusted / snapshot.INSTALLER_PATH).read_bytes()).hexdigest()
        policy = self._policy(sources, graphs, installer_sha, hashlib.sha256(evidence.read_bytes()).hexdigest())
        scanner_sha = hashlib.sha256(scanner.read_bytes()).hexdigest()
        policy["scanner"]["binary_sha256"] = scanner_sha
        for record in policy["records"]:
            record["advisory_sha256"] = advisory_hashes[record["advisory"]]
        (self.trusted / snapshot.POLICY_PATH).write_text(json.dumps(policy))
        trusted_sha = add_and_commit(self.trusted)
        def maven_runner(source, scenario):
            return graph_digest, hashlib.sha256((source / snapshot.SCENARIO_DIRS[scenario] / "backend/pom.xml").read_bytes()).hexdigest()
        return SimpleNamespace(scanner=scanner, scanner_sha=scanner_sha, trusted_sha=trusted_sha,
                               maven_runner=maven_runner, advisory_hashes=advisory_hashes)

    def _prepare_complete(self, fixture):
        return snapshot.prepare_snapshot(
            self.source, self.trusted, fixture.trusted_sha,
            self.trusted / "scripts/ci/dependency-audit.py",
            self.trusted / "scripts/ci/dependency_snapshot.py", fixture.scanner,
            maven_runner=fixture.maven_runner)

    def test_full_prepare_and_final_revalidation_preserve_exact_decision(self):
        fixture = self._complete_fixture()
        with patch.object(snapshot, "SCANNER_SHA256", fixture.scanner_sha):
            authorization = self._prepare_complete(fixture)
            snapshot.assert_authorization_current(authorization)
            self.assertEqual(len(authorization.records), 8)
            advisory = sorted(snapshot.ADVISORIES)[0]
            finding = {"id": advisory, "ecosystem": "Maven", "package": snapshot.EXPECTED_PACKAGE[1],
                       "version": "6.2.19", "severity": "CRITICAL",
                       "advisory_sha256": fixture.advisory_hashes[advisory]}
            self.assertEqual(snapshot.decision_for(authorization, "C1", finding)["decision"],
                             "not_reachable_in_reviewed_snapshot")

    def test_prepare_rejects_missing_primary_advisories_even_with_valid_policy(self):
        fixture = self._complete_fixture()
        for file in (self.trusted / "experiment/evaluation/dependency-advisories").glob("GHSA-*.json"):
            file.unlink()
        (self.trusted / snapshot.ADVISORY_MANIFEST_PATH).write_text('{"records":[]}')
        fixture.trusted_sha = add_and_commit(self.trusted)
        with patch.object(snapshot, "SCANNER_SHA256", fixture.scanner_sha):
            with self.assertRaises(snapshot.SnapshotError):
                self._prepare_complete(fixture)

    def test_prepare_rejects_policy_hash_not_bound_to_primary_advisory(self):
        fixture = self._complete_fixture()
        file = self.trusted / snapshot.POLICY_PATH
        policy = json.loads(file.read_text())
        policy["records"][0]["advisory_sha256"] = "0" * 64
        file.write_text(json.dumps(policy))
        fixture.trusted_sha = add_and_commit(self.trusted)
        with patch.object(snapshot, "SCANNER_SHA256", fixture.scanner_sha):
            with self.assertRaises(snapshot.SnapshotError):
                self._prepare_complete(fixture)

    def test_final_revalidation_rejects_changed_primary_advisory(self):
        fixture = self._complete_fixture()
        with patch.object(snapshot, "SCANNER_SHA256", fixture.scanner_sha):
            authorization = self._prepare_complete(fixture)
            file = self.trusted / f"experiment/evaluation/dependency-advisories/{sorted(snapshot.ADVISORIES)[0]}.json"
            data = json.loads(file.read_text())
            data["modified"] = "2026-11-02T00:00:00Z"
            file.write_text(json.dumps(data))
            with self.assertRaises(snapshot.SnapshotError):
                snapshot.assert_authorization_current(authorization)

    def test_trusted_loader_executes_measured_source_instead_of_forged_pyc(self):
        spec = importlib.util.spec_from_file_location("snapshot_loader_regression", MODULE_PATH.with_name("dependency-audit.py"))
        audit = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(audit)
        evaluator = self.trusted / "scripts/ci/dependency-audit.py"
        evaluator.write_bytes(MODULE_PATH.with_name("dependency-audit.py").read_bytes())
        helper = self.trusted / "scripts/ci/dependency_snapshot.py"
        helper.write_text('TRUSTED_MARKER = "source"\n')
        (self.trusted / ".gitignore").write_text("__pycache__/\n")
        trusted_sha = add_and_commit(self.trusted)
        canary = self.base / "bytecode-canary"
        cache = Path(importlib.util.cache_from_source(str(helper)))
        cache.parent.mkdir(exist_ok=True)
        code = compile(f'from pathlib import Path\nPath({str(canary)!r}).write_text("unexpected")\nTRUSTED_MARKER = "bytecode"\n', str(helper), "exec")
        header = importlib.util.MAGIC_NUMBER + struct.pack("<III", 0, int(helper.stat().st_mtime), helper.stat().st_size)
        cache.write_bytes(header + marshal.dumps(code))
        with patch.object(audit, "__file__", str(evaluator)):
            module = audit._load_trusted_snapshot_module(self.source, self.trusted, trusted_sha)
        self.assertFalse(canary.exists(), "ignored bytecode must never execute")
        self.assertEqual(module.TRUSTED_MARKER, "source")

    def test_optional_advisory_fields_are_canonical_null_without_weakening_identity(self):
        data = {"id": "GHSA-fixture", "modified": "2026-11-01T00:00:00Z", "affected": []}
        explicit = {**data, "severity": None, "database_specific": None}
        self.assertEqual(snapshot.advisory_sha256(data),
                         hashlib.sha256(json.dumps(explicit, sort_keys=True, separators=(",", ":")).encode()).hexdigest())

    def _policy(self, source_hashes, graph_hashes, installer_sha, evidence_sha):
        issued = "2026-11-12T00:00:00Z"
        expires = "2026-11-20T00:00:00Z"
        records = []
        for scenario in snapshot.SCENARIO_DIRS:
            for advisory in sorted(snapshot.ADVISORIES):
                records.append({
                    "scenario": scenario, "ecosystem": "Maven", "package": snapshot.EXPECTED_PACKAGE[1],
                    "version": snapshot.EXPECTED_PACKAGE[2], "advisory": advisory, "severity": "CRITICAL",
                    "decision": "not_reachable_in_reviewed_snapshot", "risk_residual": "componente vulnerável permanece",
                    "reviewer": "neo", "status": "active", "issued_at": issued, "expires_at": expires,
                    "source_sha256": source_hashes[scenario], "graph_sha256": graph_hashes[scenario],
                    "advisory_sha256": hashlib.sha256(advisory.encode()).hexdigest(),
                    "evidence": [{"path": "experiment/evaluation/evidence.md", "sha256": evidence_sha}],
                })
        return {"schema_version": 1, "status": "active", "issued_at": issued, "expires_at": expires,
                "scanner": {"name": "OSV-Scanner", "version": snapshot.SCANNER_VERSION,
                            "binary_sha256": snapshot.SCANNER_SHA256, "installer_sha256": installer_sha},
                "records": records}


if __name__ == "__main__":
    unittest.main()
