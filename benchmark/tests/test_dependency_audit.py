import importlib.util
import json
import math
import tempfile
import unittest
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

    def test_scanner_quebrado_reprova_mesmo_com_saida_json(self):
        completed = type("Completed", (), {"returncode": 2, "stdout": '{"results": []}'})()
        with patch.object(audit_module.subprocess, "run", return_value=completed):
            with self.assertRaises(audit_module.AuditError):
                audit_module._run(self.scanner, self.root / "manifest", "lockfile")

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
        payload = {"results": [{"packages": [{"package": {"name": "pkg", "version": "1"},
                                                "groups": [{"ids": ["GHSA-a"], "max_severity": "7.5"}],
                                                "vulnerabilities": [{"id": "GHSA-a", "aliases": [],
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
