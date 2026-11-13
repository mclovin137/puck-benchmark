import importlib.util
import json
import math
import hashlib
import shutil
import subprocess
import tempfile
import unittest
import tomllib
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts/ci/dependency-audit.py"
SPEC = importlib.util.spec_from_file_location("dependency_audit", MODULE_PATH)
audit_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit_module)


class DependencyAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for _, _, target, mode in audit_module.TARGETS:
            path = self.root / target
            path.parent.mkdir(parents=True, exist_ok=True)
            if mode == "directory":
                path.mkdir(parents=True, exist_ok=True)
                (path / "manifest").touch()
            else:
                path.touch()
        self.scanner = self.root / "scanner"
        self.scanner.touch()
        self.triage = self.root / "triage.json"
        self.triage.write_text("[]")
        self.report = self.root / "report.json"

    def tearDown(self):
        self.tmp.cleanup()

    @staticmethod
    def clean_result():
        return {"packages": 4, "findings": []}

    @staticmethod
    def critical_result():
        return {"packages": 4, "findings": [{
            "package": "org.example:sample", "version": "1.2.3", "id": "GHSA-test-1234",
            "aliases": ["CVE-2026-1234"], "severity": "CRITICAL",
            "ecosystem": "Maven", "advisory_sha256": "a" * 64,
        }]}

    def run_audit(self, result):
        with patch.object(audit_module, "_run", return_value=result):
            return audit_module.audit(self.root, self.scanner, self.triage, self.report)

    def test_audita_nove_fontes_obrigatorias_e_escreve_relatorio_sanitizado(self):
        report, code = self.run_audit(self.clean_result())
        self.assertEqual(code, 0)
        self.assertEqual(len(report["sources"]), 9)
        self.assertEqual(report["status"], "passed")
        contents = self.report.read_text()
        self.assertNotIn(str(self.root), contents)
        self.assertNotIn("details", contents)

    def test_critica_sem_triagem_reprova(self):
        report, code = self.run_audit(self.critical_result())
        self.assertEqual(code, 1)
        self.assertEqual(report["status"], "failed")
        self.assertEqual(len(report["untriaged_high_critical"]), 9)

    def test_triagem_informativa_nao_desbloqueia_sem_binding(self):
        record = {
            "scenario": "C1", "ecosystem": "Maven", "package": "org.example:sample",
            "version": "1.2.3", "advisory": "CVE-2026-1234", "decision": "descartado",
            "reviewer": "neo", "evidence": "revisão independente registrada", "expires": "2026-12-12",
        }
        self.triage.write_text(json.dumps([record]))
        with self.assertRaisesRegex(audit_module.AuditError, "sem binding"):
            self.run_audit(self.critical_result())

    def test_triagem_nao_pode_ser_global_por_advisory(self):
        record = {
            "scenario": "*", "ecosystem": "*", "package": "*", "version": "*",
            "advisory": "GHSA-test-1234", "decision": "descartado", "reviewer": "neo",
            "evidence": "evidência", "expires": "2026-12-12",
        }
        self.triage.write_text(json.dumps([record]))
        with self.assertRaisesRegex(audit_module.AuditError, "sem binding"):
            self.run_audit(self.critical_result())

    def test_triagem_expirada_ou_com_campo_extra_falha_fechado(self):
        record = {
            "scenario": "C1", "ecosystem": "Maven", "package": "org.example:sample",
            "version": "1.2.3", "advisory": "GHSA-test-1234", "decision": "descartado",
            "reviewer": "neo", "evidence": "evidência", "expires": "2026-11-11", "global": True,
        }
        self.triage.write_text(json.dumps([record]))
        with self.assertRaises(audit_module.AuditError):
            self.run_audit(self.critical_result())

    def test_manifest_ausente_bloqueia_cobertura_incompleta(self):
        missing = self.root / audit_module.TARGETS[0][2]
        (missing / "manifest").unlink()
        missing.rmdir()
        with self.assertRaises(audit_module.AuditError):
            self.run_audit(self.clean_result())

    def test_scanner_com_json_invalido_falha_fechado(self):
        completed = type("Completed", (), {"returncode": 0, "stdout": "not json"})()
        with patch.object(audit_module.subprocess, "run", return_value=completed):
            with self.assertRaises(audit_module.AuditError):
                audit_module._run(self.scanner, self.root / "manifest", "lockfile")

    def test_scanner_recebe_configuracao_neutra_fora_do_candidato(self):
        payload = {"results": [{"packages": [{"package": {"name": "safe", "version": "1"},
                                                "groups": [], "vulnerabilities": []}]}]}
        def run(args, **kwargs):
            self.assertIn("--config", args)
            config = Path(args[args.index("--config") + 1])
            self.assertTrue(config.is_absolute())
            self.assertFalse(config.resolve().is_relative_to(self.root))
            self.assertFalse(config.is_symlink())
            self.assertEqual(tomllib.loads(config.read_text()), {})
            return subprocess.CompletedProcess(args, 0, stdout=json.dumps(payload))
        with patch.object(audit_module.subprocess, "run", side_effect=run):
            result = audit_module._run(self.scanner, self.root / "benchmark/requirements.txt", "lockfile")
        self.assertEqual(result["packages"], 1)
        self.assertEqual(result["findings"], [])

    def test_advisory_opcional_nao_oculta_finding_critico(self):
        advisory = {"id": "PYSEC-fixture", "modified": "2026-11-01T00:00:00Z", "affected": [], "severity": []}
        payload = {"results": [{"packages": [{"package": {"name": "pkg", "version": "1", "ecosystem": "PyPI"},
                                                "groups": [{"ids": [advisory["id"]], "max_severity": "9.8"}],
                                                "vulnerabilities": [advisory]}]}]}
        completed = subprocess.CompletedProcess([], 1, stdout=json.dumps(payload))
        with patch.object(audit_module.subprocess, "run", return_value=completed):
            result = audit_module._run(self.scanner, self.root / "benchmark/requirements.txt", "lockfile")
        self.assertEqual(result["findings"][0]["severity"], "CRITICAL")
        self.assertEqual(len(result["findings"][0]["advisory_sha256"]), 64)

    def test_scanner_quebrado_reprova_mesmo_com_saida_json(self):
        completed = type("Completed", (), {"returncode": 2, "stdout": '{"results": []}'})()
        with patch.object(audit_module.subprocess, "run", return_value=completed):
            with self.assertRaises(audit_module.AuditError):
                audit_module._run(self.scanner, self.root / "manifest", "lockfile")

    def test_optin_carrega_helper_trustado_e_ignora_policy_do_source(self):
        trusted = self.root / "trusted"
        source = self.root / "source"
        trusted.mkdir()
        source.mkdir()
        for repo in (trusted, source):
            subprocess.run(["git", "init", "--quiet", str(repo)], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "fixture"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "fixture@example.invalid"], check=True)
        audit_file = trusted / "scripts/ci/dependency-audit.py"
        helper_file = trusted / "scripts/ci/dependency_snapshot.py"
        installer = trusted / "benchmark/scripts/install_tools.py"
        for path in (audit_file, helper_file, installer):
            path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(MODULE_PATH, audit_file)
        helper_bytes = (MODULE_PATH.parents[0] / "dependency_snapshot.py").read_bytes()
        scanner_path = trusted / ".private/tools/osv-scanner"
        scanner_path.parent.mkdir(parents=True)
        scanner_bytes = b"scanner fixture"
        scanner_path.write_bytes(scanner_bytes)
        scanner_digest = hashlib.sha256(scanner_bytes).hexdigest()
        helper_file.write_bytes(helper_bytes.replace(
            b'SCANNER_SHA256 = "160c6253e2922e9e0a6a9771c5c4c40a4b3c6090b34a3cdd5e80c96cc2e4218b"',
            f'SCANNER_SHA256 = "{scanner_digest}"'.encode("ascii")))
        installer.write_text("trusted installer fixture\n", encoding="utf-8")
        candidate_policy = source / "experiment/dependency-snapshot-policy.json"
        candidate_policy.parent.mkdir(parents=True)
        candidate_policy.write_text('{"status":"active","marker":"CANDIDATE_POLICY"}\n', encoding="utf-8")
        for repo in (trusted, source):
            subprocess.run(["git", "-C", str(repo), "add", "--all"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "--quiet", "-m", "fixture"], check=True)
        trusted_sha = subprocess.run(["git", "-C", str(trusted), "rev-parse", "HEAD"], check=True,
                                    stdout=subprocess.PIPE, text=True).stdout.strip()
        result = subprocess.run([
            "python3", "-I", str(audit_file), "--root", str(source), "--scanner", ".private/tools/osv-scanner",
            "--trusted-root", str(trusted), "--trusted-sha", trusted_sha,
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("arquivo confiável ausente", result.stderr)
        self.assertNotIn("CANDIDATE_POLICY", result.stdout + result.stderr)

    def test_codigo_1_sem_achados_falha_fechado(self):
        payload = {"results": [{"packages": [{"package": {"name": "pkg", "version": "1"},
                                                "groups": [], "vulnerabilities": []}]}]}
        completed = type("Completed", (), {"returncode": 1, "stdout": json.dumps(payload)})()
        with patch.object(audit_module.subprocess, "run", return_value=completed):
            with self.assertRaisesRegex(audit_module.AuditError, "sem achados"):
                audit_module._run(self.scanner, self.root / "manifest", "lockfile")

    def test_severidade_nao_finita_ou_fora_da_escala_e_desconhecida(self):
        for value in ("NaN", "Infinity", "-1", "10.1", "not-a-number"):
            with self.subTest(value=value):
                self.assertEqual(audit_module._severity({}, {"max_severity": value}), "UNKNOWN")

    def test_conflito_de_severidade_usa_a_maior_ou_bloqueia_com_unknown(self):
        vuln = {"database_specific": {"severity": "LOW"}}
        self.assertEqual(audit_module._severity(vuln, {"max_severity": "9.8"}), "CRITICAL")
        vuln["database_specific"]["severity"] = "UNRECOGNIZED"
        self.assertEqual(audit_module._severity(vuln, {"max_severity": "2"}), "UNKNOWN")
        vuln["database_specific"]["severity"] = "LOW"
        self.assertEqual(audit_module._severity(vuln, {"max_severity": "NaN"}), "UNKNOWN")

    def test_codigo_0_com_achados_falha_fechado(self):
        payload = {"results": [{"packages": [{"package": {"name": "pkg", "version": "1", "ecosystem": "Maven"},
                                                "groups": [{"ids": ["GHSA-a"], "max_severity": "7.5"}],
                                                "vulnerabilities": [{"id": "GHSA-a", "aliases": [],
                                                                     "modified": "2026-11-01T00:00:00Z",
                                                                     "affected": [], "severity": [],
                                                                     "database_specific": {"severity": "HIGH"}}]}]}]}
        completed = type("Completed", (), {"returncode": 0, "stdout": json.dumps(payload)})()
        with patch.object(audit_module.subprocess, "run", return_value=completed):
            with self.assertRaisesRegex(audit_module.AuditError, "código 0 com achados"):
                audit_module._run(self.scanner, self.root / "manifest", "lockfile")

    def test_triagem_ausente_falha_fechado(self):
        self.triage.unlink()
        with self.assertRaises(audit_module.AuditError):
            self.run_audit(self.clean_result())


if __name__ == "__main__":
    unittest.main()
