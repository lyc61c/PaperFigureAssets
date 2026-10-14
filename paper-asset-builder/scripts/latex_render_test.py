#!/usr/bin/env python3
"""Prepare or explicitly upload README table snippets for isolated render tests.

Only table LaTeX and its listed, permitted packages are submitted. The static
screening is defense in depth, not a general-purpose TeX sandbox. Use a trusted
compiler service with its own OS-level isolation. HTTPS is required except for
an explicitly selected localhost/loopback self-hosted service.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

DEFAULT_ENDPOINT = "https://latex.ytotech.com/builds/sync"
MAX_README_BYTES = 2 * 1024 * 1024
MAX_RESPONSE_BYTES = 20 * 1024 * 1024
MAX_SOURCE_BYTES = 256 * 1024
ALLOWED_PACKAGES = frozenset({
    "booktabs", "multirow", "xcolor", "graphicx", "array", "makecell",
    "siunitx", "pifont", "ulem", "adjustbox", "amssymb", "amsmath",
    "arydshln", "tabularx", "longtable", "threeparttable", "caption",
    "colortbl", "boldline", "rotating", "float", "hhline", "diagbox",
})
PACKAGE_RE = re.compile(
    r"\\usepackage\s*(?:\[([A-Za-z0-9 ,=.!+_-]*)\])?\s*"
    r"\{([A-Za-z0-9, -]+)\}")
FORBIDDEN_COMMANDS = frozenset({
    "input", "include", "includeonly", "includegraphics", "graphicspath",
    "bibliography", "bibliographystyle", "addbibresource", "import", "subimport",
    "openin", "closein", "read", "readline", "openout", "closeout", "write",
    "immediate", "write18", "directlua", "latelua", "luafunction", "luaexec",
    "special", "pdffiledump", "pdfmdfivesum", "pdffilesize", "pdfximage",
    "pdfobj", "pdfcatalog", "pdfextension", "pdfprimitive", "pdfmapfile",
    "pdfmapline", "pdfannot", "pdfstartlink", "pdfendlink", "pdfoutline",
    "csname", "endcsname", "catcode", "scantokens", "expandafter",
    "def", "edef", "gdef", "xdef", "let", "futurelet", "newcommand",
    "providecommand", "newenvironment", "renewenvironment", "newif",
    "explsyntaxon", "newdocumentcommand", "renewdocumentcommand", "providedocumentcommand",
    "makeatletter", "makeatother", "everyjob", "everyeof", "everypar",
    "everymath", "everydisplay", "everyhbox", "everyvbox", "everycr",
    "documentclass", "documentstyle", "usepackage", "requirepackage",
    "inputencoding", "inputminted", "lstinputlisting", "verbatiminput",
    "url", "href", "hyperref", "shellescape", "execute", "jobname",
    "endinput", "loop", "repeat", "shipout", "font", "newfont",
    "sisetup", "pgfplotstableread", "pgfplotsset", "tikzset",
    "usefont", "fontspec", "setmainfont", "setsansfont", "setmonofont",
})


@dataclass(frozen=True)
class TableSnippet:
    title: str
    source: str
    packages: str


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract_tables(markdown: str) -> list[TableSnippet]:
    """Extract canonical table sections, ignoring headings inside code fences."""
    section = False
    current = None
    subsection = None
    fence = None
    fence_lines = []
    parsed = []

    def finish():
        if current is not None:
            if len(current["source"]) != 1 or len(current["packages"]) != 1:
                raise ValueError(f"{current['title']}: expected one source and one packages block")
            source, packages = current["source"][0], current["packages"][0]
            if not source.strip():
                raise ValueError(f"{current['title']}: empty table source")
            parsed.append(TableSnippet(current["title"], source, packages))

    for line in markdown.splitlines():
        if fence is not None:
            if re.fullmatch(r"\s*" + re.escape(fence) + r"\s*", line):
                if section and current is not None and subsection in ("source", "packages"):
                    if fence_language != "latex":
                        raise ValueError("Table source and packages must use latex fences")
                    current[subsection].append("\n".join(fence_lines).strip())
                fence = None
                fence_lines = []
            else:
                fence_lines.append(line)
            continue
        opening = re.fullmatch(r"\s*(`{3,}|~{3,})([\w+-]*)\s*", line)
        if opening:
            fence, fence_language = opening.groups()
            continue
        if re.match(r"^#\s+", line):
            finish()
            current, subsection = None, None
            section = bool(re.fullmatch(r"#\s+3\.\s+Paper Tables\s*", line))
        elif section and re.match(r"^##\s+", line):
            finish()
            current, subsection = None, None
            title = re.fullmatch(r"##\s+(Table\s+\d+\s*:.*)", line)
            if title:
                current = {"title": title.group(1).strip(), "source": [], "packages": []}
        elif section and current is not None and re.match(r"^###\s+", line):
            subsection = {"### LaTeX Source": "source", "### Required Packages": "packages"}.get(line.strip())
    if fence is not None:
        raise ValueError("Unclosed Markdown code fence")
    finish()
    return parsed


def uncomment(text: str) -> str:
    # A percent is escaped only after an odd run of backslashes.
    return re.sub(r"(?<!\\)(?:\\\\)*%[^\n]*", "", text)


def validate_source(source: str, packages: str) -> None:
    if len((source + packages).encode("utf-8")) > MAX_SOURCE_BYTES:
        raise ValueError("Table source exceeds size limit")
    text = uncomment(source)
    if "^^" in text or any(ord(char) < 32 and char not in "\n\r\t" for char in text):
        raise ValueError("Encoded/control TeX input is not permitted")
    for command in re.findall(r"\\([A-Za-z]+[0-9]*)", text):
        if command.lower() in FORBIDDEN_COMMANDS or command.lower().startswith(("pdf", "lua", "xe")):
            raise ValueError(f"Unsafe or external-resource command: \\{command}")
    # Only the table-specific arraystretch adjustment may redefine a command.
    remainder = re.sub(r"\\renewcommand\s*\{\\arraystretch\}\s*\{[0-9.]+\}", "", text)
    if re.search(r"\\renewcommand\b", remainder):
        raise ValueError("Only numeric arraystretch renewal is permitted")
    if re.search(r"\\(?:begin|end)\s*\{(?:document|filecontents\*?|luacode\*?|minted|verbatimwrite)\}", text, re.I):
        raise ValueError("Document or executable/file environment is not permitted")
    package_text = uncomment(packages)
    position = 0
    for match in PACKAGE_RE.finditer(package_text):
        if package_text[position:match.start()].strip():
            raise ValueError("Packages block may contain only literal usepackage declarations")
        for name in match.group(2).split(","):
            if name.strip() not in ALLOWED_PACKAGES:
                raise ValueError(f"Package not permitted for isolated tables: {name.strip()}")
        position = match.end()
    if package_text[position:].strip():
        raise ValueError("Packages block may contain only literal usepackage declarations")


def wrap_table(table: TableSnippet) -> str:
    validate_source(table.source, table.packages)
    # article supports floating table/table*; standalone's default mode does not.
    return ("\\documentclass[10pt]{article}\n"
            "\\usepackage[paperwidth=320mm,paperheight=420mm,margin=12mm]{geometry}\n"
            + table.packages + "\n\\pagestyle{empty}\n"
            "\\begin{document}\n" + table.source
            + "\n\\clearpage\n\\end{document}\n")


def validate_endpoint(endpoint: str) -> str:
    parsed = urllib.parse.urlsplit(endpoint)
    if parsed.username or parsed.password or not parsed.hostname:
        raise ValueError("Endpoint must have a host and no embedded credentials")
    loopback = parsed.hostname.lower() in {"localhost", "127.0.0.1", "::1"}
    if parsed.scheme != "https" and not (parsed.scheme == "http" and loopback):
        raise ValueError("Endpoint requires HTTPS (HTTP allowed only for localhost/loopback)")
    if parsed.fragment:
        raise ValueError("Endpoint must not contain a fragment")
    return endpoint


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, "Redirect refused", headers, fp)


def compile_remote(document: str, *, allow_upload: bool, endpoint: str,
                   compiler: str, timeout: float, opener=None) -> dict:
    if not allow_upload:
        raise PermissionError("Online upload requires explicit --allow-upload")
    validate_endpoint(endpoint)
    payload = {"compiler": compiler, "resources": [{"main": True, "path": "main.tex", "content": document}],
               "options": {"compiler": {"halt_on_error": True, "force": False, "bibliography": False},
                           "response": {"log_files_on_failure": True}}}
    request = urllib.request.Request(endpoint, data=json.dumps(payload).encode("utf-8"),
                                     headers={"Content-Type": "application/json", "Accept": "application/pdf"}, method="POST")
    opener = opener or urllib.request.build_opener(NoRedirect())
    for attempt in range(2):
        try:
            with opener.open(request, timeout=timeout) as response:
                data = response.read(MAX_RESPONSE_BYTES + 1)
                if len(data) > MAX_RESPONSE_BYTES:
                    return {"status": "response_too_large", "attempts": attempt + 1}
                if plausible_pdf(data):
                    return {"status": "compiled", "pdf": data, "attempts": attempt + 1}
                return {"status": "non_pdf_response", "response": decode_response(data), "attempts": attempt + 1}
        except urllib.error.HTTPError as error:
            data = error.read(MAX_RESPONSE_BYTES + 1)
            return {"status": "http_error", "http_status": error.code,
                    "response": decode_response(data[:MAX_RESPONSE_BYTES]), "attempts": attempt + 1}
        except (urllib.error.URLError, TimeoutError, socket.timeout, ConnectionError, OSError) as error:
            if attempt == 1:
                return {"status": "network_error", "error": str(error), "attempts": 2}
            time.sleep(0.5)
    raise AssertionError("unreachable")


def plausible_pdf(data: bytes) -> bool:
    """Reject error bodies and trivial signature-only fakes before saving a PDF.

    Full parsing and page validation happen with PyMuPDF when available.
    """
    if not data.startswith(b"%PDF-") or b"%%EOF" not in data[-2048:]:
        return False
    crossrefs = re.findall(rb"startxref\s+(\d+)\s+%%EOF", data[-2048:])
    return bool(crossrefs and 0 < int(crossrefs[-1]) < len(data) and b"/Root" in data)


def decode_response(data: bytes):
    text = data.decode("utf-8", errors="replace")
    try:
        return json.loads(text)
    except ValueError:
        return {"body": text}


def safe_child(directory: Path, basename: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", basename) or basename in {".", ".."}:
        raise ValueError("Unsafe output basename")
    target = directory / basename
    if target.resolve().parent != directory.resolve():
        raise ValueError("Output escapes the selected directory")
    return target


def render_pdf(pdf_path: Path, output: Path, basename: str) -> dict:
    try:
        import fitz
    except ImportError:
        return {"status": "unavailable", "reason": "PyMuPDF is not installed"}
    try:
        with fitz.open(pdf_path) as document:
            if not document.is_pdf or document.page_count < 1:
                raise ValueError("PDF has no pages")
            images = []
            for number, page in enumerate(document, 1):
                path = safe_child(output, f"{basename}-page-{number:02d}.png")
                page.get_pixmap(dpi=300, alpha=False).save(path)
                images.append(str(path))
            return {"status": "rendered", "page_count": document.page_count, "png_paths": images, "dpi": 300}
    except Exception as error:
        return {"status": "failed", "error": str(error)}


def run(args) -> dict:
    validate_endpoint(args.endpoint)
    if args.timeout <= 0:
        raise ValueError("Timeout must be positive")
    output = Path(args.out).resolve()
    output.mkdir(parents=True, exist_ok=True)
    report = {"allow_upload": args.allow_upload, "endpoint": args.endpoint, "compiler": args.compiler,
              "upload_scope": "Each table source, its listed packages, and a minimal article wrapper only.", "tables": []}
    for readme_arg in args.readme:
        readme = Path(readme_arg).resolve()
        if readme.stat().st_size > MAX_README_BYTES:
            raise ValueError(f"README exceeds size limit: {readme}")
        tables = extract_tables(readme.read_text(encoding="utf-8-sig"))
        if not tables:
            raise ValueError(f"No canonical tables found in {readme}")
        folder = re.sub(r"[^A-Za-z0-9_-]+", "-", readme.parent.name).strip("-_")[:64] or "paper"
        for number, table in enumerate(tables, 1):
            basename = f"{folder}-{sha256(str(readme))[:8]}-table-{number:02d}"
            item = {"readme": str(readme), "table": table.title,
                    "source_sha256": sha256(table.source), "packages_sha256": sha256(table.packages)}
            report["tables"].append(item)
            try:
                document = wrap_table(table)
                item["document_sha256"] = sha256(document)
            except ValueError as error:
                item.update(status="rejected", error=str(error))
                continue
            tex_path = safe_child(output, basename + ".tex")
            tex_path.write_text(document, encoding="utf-8")
            item["tex_path"] = str(tex_path)
            if not args.allow_upload:
                item.update(status="prepared", render={"status": "not_requested"})
                continue
            result = compile_remote(document, allow_upload=args.allow_upload, endpoint=args.endpoint,
                                    compiler=args.compiler, timeout=args.timeout)
            pdf_data = result.pop("pdf", None)
            item.update(result)
            if pdf_data is not None:
                pdf_path = safe_child(output, basename + ".pdf")
                pdf_path.write_bytes(pdf_data)
                item["pdf_path"] = str(pdf_path)
                item["render"] = render_pdf(pdf_path, output, basename)
                if item["render"].get("status") == "failed":
                    item["status"] = "invalid_pdf"
                if "page_count" in item["render"]:
                    item["page_count"] = item["render"]["page_count"]
            else:
                log_path = safe_child(output, basename + ".error.json")
                log_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
                item["log_path"] = str(log_path)
                item["render"] = {"status": "not_compiled"}
    report_path = safe_child(output, "report.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    report["report_path"] = str(report_path)
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readme", action="append", required=True, help="Explicit paper README; repeat for several papers")
    parser.add_argument("--out", required=True, help="Temporary QA output directory")
    parser.add_argument("--compiler", choices=("pdflatex", "xelatex", "lualatex"), default="pdflatex")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--timeout", type=float, default=60)
    parser.add_argument("--allow-upload", action="store_true", help="Explicitly permit sending table-only source to this endpoint")
    args = parser.parse_args(argv)
    try:
        report = run(args)
    except (OSError, ValueError) as error:
        parser.exit(2, f"error: {error}\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return int(any(table["status"] not in {"compiled", "prepared"} for table in report["tables"]))


if __name__ == "__main__":
    raise SystemExit(main())
