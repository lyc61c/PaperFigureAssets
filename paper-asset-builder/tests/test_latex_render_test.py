"""Offline tests; no test submits source to a remote service."""
import argparse
import importlib.util
import io
import json
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "latex_render_test.py"
SPEC = importlib.util.spec_from_file_location("latex_render_test", SCRIPT)
helper = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = helper
SPEC.loader.exec_module(helper)

SOURCE = r"\begin{table}[t]\centering\begin{tabular}{cc} A & B \\\end{tabular}\end{table}"
PACKAGES = r"\usepackage{booktabs}"
README = """# Title
# 2. Result Analysis Figures
```python
# 3. Paper Tables
## Table 8: Not a table
```
# 3. Paper Tables
## Table 1: Test
### LaTeX Source
```latex
%s
```
### Required Packages
```latex
%s
```
---
""" % (SOURCE, PACKAGES)


def minimal_pdf():
    chunks = [b"%PDF-1.4\n"]
    positions = []
    for number, body in enumerate([
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 100 100] /Resources << >> /Contents 4 0 R >>",
        b"<< /Length 0 >>\nstream\n\nendstream",
    ], 1):
        positions.append(sum(map(len, chunks)))
        chunks.append(str(number).encode() + b" 0 obj\n" + body + b"\nendobj\n")
    crossref = sum(map(len, chunks))
    chunks.append(b"xref\n0 5\n0000000000 65535 f \n")
    chunks.extend(f"{position:010d} 00000 n \n".encode() for position in positions)
    chunks.append(f"trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n{crossref}\n%%EOF\n".encode())
    return b"".join(chunks)


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class FakeOpener:
    def __init__(self, response=None, error=None):
        self.response, self.error, self.calls, self.request = response, error, 0, None

    def open(self, request, timeout):
        self.calls += 1
        self.request = request
        if self.error:
            raise self.error
        return FakeResponse(self.response)


class RenderHelperTests(unittest.TestCase):
    def compile(self, opener, **kwargs):
        return helper.compile_remote("document", allow_upload=True,
                                     endpoint=helper.DEFAULT_ENDPOINT, compiler="pdflatex",
                                     timeout=1, opener=opener, **kwargs)

    def test_parse_only_canonical_tables(self):
        tables = helper.extract_tables(README)
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0].source, SOURCE)
        self.assertEqual(tables[0].packages, PACKAGES)
        self.assertEqual(tables[0].title, "Table 1: Test")

    def test_missing_or_duplicate_block_rejected(self):
        with self.assertRaises(ValueError):
            helper.extract_tables(README.replace("### Required Packages", "### Other"))
        with self.assertRaises(ValueError):
            helper.extract_tables(README + "### Required Packages\n```latex\n\\usepackage{array}\n```\n")

    def test_unclosed_fence_rejected(self):
        with self.assertRaises(ValueError):
            helper.extract_tables(README + "```latex\n")

    def test_article_wrapper_keeps_float_and_only_listed_packages(self):
        document = helper.wrap_table(helper.extract_tables(README)[0])
        self.assertIn(r"\documentclass[10pt]{article}", document)
        self.assertNotIn("standalone", document)
        self.assertIn(SOURCE, document)
        self.assertIn(PACKAGES, document)
        self.assertEqual(document.count(r"\begin{document}"), 1)

    def test_unsafe_commands_and_dynamic_input_rejected(self):
        for unsafe in [r"\input{secret}", r"\includegraphics{x.png}", r"\write18{curl x}",
                       r"\directlua{os.execute('x')}", r"\csname input\endcsname{x}",
                       r"\catcode`\%=12", r"\^^69nput{x}", r"\end{document}",
                       r"\newcommand{\xx}{x}", r"\renewcommand{\input}{x}",
                       r"\begin{filecontents}{x}hi\end{filecontents}", r"\pdfximage{x}"]:
            with self.subTest(unsafe=unsafe), self.assertRaises(ValueError):
                helper.validate_source(unsafe, PACKAGES)
        helper.validate_source(SOURCE + r"\renewcommand{\arraystretch}{1.12}", PACKAGES)

    def test_packages_are_literal_and_permitted(self):
        for unsafe in [r"\usepackage{../../secret}", r"\usepackage{shellesc}",
                       r"\usepackage{luacode}", r"\usepackage{booktabs}\input{x}",
                       r"\usepackage[foo=\input{x}]{booktabs}"]:
            with self.subTest(unsafe=unsafe), self.assertRaises(ValueError):
                helper.validate_source(SOURCE, unsafe)
        helper.validate_source(SOURCE, "\\usepackage[table]{xcolor}\n\\usepackage{amsmath,amssymb}")

    def test_no_upload_without_explicit_gate(self):
        opener = FakeOpener(b"anything")
        with self.assertRaises(PermissionError):
            helper.compile_remote("document", allow_upload=False, endpoint=helper.DEFAULT_ENDPOINT,
                                  compiler="pdflatex", timeout=1, opener=opener)
        self.assertEqual(opener.calls, 0)

    def test_endpoint_policy(self):
        for accepted in [helper.DEFAULT_ENDPOINT, "http://localhost:8080/builds/sync", "http://127.0.0.1:8080", "http://[::1]:8080"]:
            self.assertEqual(helper.validate_endpoint(accepted), accepted)
        for denied in ["http://example.com/build", "file:///tmp/test", "https://user:pass@example.com", "https://example.com/#frag"]:
            with self.subTest(endpoint=denied), self.assertRaises(ValueError):
                helper.validate_endpoint(denied)

    def test_non_pdf_and_signature_only_fake_rejected(self):
        for data in [b"<html>Error</html>", b'{"error":"TeX failed"}', b"%PDF-1.4\nfake\n%%EOF"]:
            result = self.compile(FakeOpener(data))
            self.assertEqual(result["status"], "non_pdf_response")
            self.assertNotIn("pdf", result)

    def test_pdf_success_and_actual_page_validation(self):
        data = minimal_pdf()
        result = self.compile(FakeOpener(data))
        self.assertEqual(result["status"], "compiled")
        self.assertEqual(result["pdf"], data)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            pdf = output / "test.pdf"
            pdf.write_bytes(data)
            rendered = helper.render_pdf(pdf, output, "test")
            if rendered["status"] == "unavailable":
                self.assertIn("PyMuPDF", rendered["reason"])
            else:
                self.assertEqual(rendered["status"], "rendered")
                self.assertEqual(rendered["page_count"], 1)
                self.assertTrue(Path(rendered["png_paths"][0]).is_file())

    def test_options_nesting_and_no_files(self):
        opener = FakeOpener(b'{"error":"TeX failed"}')
        self.compile(opener)
        payload = json.loads(opener.request.data)
        self.assertEqual(payload["options"]["compiler"], {"halt_on_error": True, "force": False, "bibliography": False})
        self.assertEqual(payload["resources"], [{"main": True, "path": "main.tex", "content": "document"}])

    def test_http_failure_keeps_log_and_does_not_retry(self):
        error = urllib.error.HTTPError(helper.DEFAULT_ENDPOINT, 400, "Bad TeX", {}, io.BytesIO(b'{"logs":["Undefined control sequence"]}'))
        opener = FakeOpener(error=error)
        result = self.compile(opener)
        self.assertEqual(result["status"], "http_error")
        self.assertEqual(result["response"]["logs"], ["Undefined control sequence"])
        self.assertEqual(opener.calls, 1)

    def test_network_failure_retries_only_once(self):
        opener = FakeOpener(error=urllib.error.URLError("offline"))
        with patch.object(helper.time, "sleep"):
            result = self.compile(opener)
        self.assertEqual(result["status"], "network_error")
        self.assertEqual(opener.calls, 2)

    def test_response_limit(self):
        with patch.object(helper, "MAX_RESPONSE_BYTES", 10):
            result = self.compile(FakeOpener(b"x" * 11))
        self.assertEqual(result["status"], "response_too_large")

    def test_output_path_and_symlink_safety(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary).resolve()
            self.assertEqual(helper.safe_child(directory, "paper-01.tex"), directory / "paper-01.tex")
            for name in ["../escape.tex", "..", "/escape.tex", "x/y.tex", r"x\y.tex", "C:escape.tex"]:
                with self.subTest(name=name), self.assertRaises(ValueError):
                    helper.safe_child(directory, name)

    def test_run_dry_run_never_uses_network(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            readme = root / "README.md"
            readme.write_text(README, encoding="utf-8")
            args = argparse.Namespace(readme=[str(readme)], out=str(root / "qa"),
                                      endpoint=helper.DEFAULT_ENDPOINT, compiler="pdflatex", timeout=60, allow_upload=False)
            with patch.object(helper, "compile_remote", side_effect=AssertionError("network called")):
                report = helper.run(args)
            self.assertEqual(report["tables"][0]["status"], "prepared")
            self.assertTrue(Path(report["tables"][0]["tex_path"]).is_file())
            self.assertEqual(report["tables"][0]["source_sha256"], helper.sha256(SOURCE))


if __name__ == "__main__":
    unittest.main()
