#!/usr/bin/env python3
"""Build Figarium from the approved root Paper Index and canonical paper READMEs.

Python standard library only. Fenced examples are copied as inert text, never
executed. Unindexed folders, PDFs, materials, and temporary QA files are not
published. Existing unrelated output files are deliberately left untouched.
"""

from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import html
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
from urllib.parse import quote, unquote, urlsplit


DEFAULT_SITE = {
    "name": "Figarium",
    "chineseName": "图圃",
    "tagline": "Curate the figure. Keep the recipe.",
    "description": "Human-curated research figures with reusable reconstruction recipes.",
    "repositoryUrl": "https://github.com/lyc61c/PaperFigureAssets",
    "featuredPaperIds": [
        "2026_arxiv_WeVisDoc", "2026_arxiv_Qwen-AgentWorld",
        "2026_arxiv_AutoEnvScaling", "2026_arxiv_ODE",
    ],
}
TYPE_FOLDERS = {"method": "method_figures", "result": "result_figures", "table": "tables"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}
CODE_LANGUAGES = {"python": "python", "py": "python", "latex": "latex", "tex": "latex", "svg": "svg", "tikz": "tikz"}
NOT_DOCUMENTED = "Not documented in the paper README."
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^\s)]+)(?:\s+\"[^\"]*\")?\)")
GENERATED_MANIFEST = ".figarium-generated.json"
MANIFEST_SCHEMA = "figarium-generated-files"
FRONTEND_FILES = ("index.html", "styles.css", "app.js")
CATALOG_FILES = ("catalog.json", "catalog.js")
GUIDE_FILES = ("GETTING_STARTED.md", "CUSTOMIZATION.md")
# Deliberately enumerate the bundled fonts and their provenance. Never publish
# a complete source directory: a nearby working font or private file is not an
# approved website asset merely because it lives in website/fonts/.
FONT_FILES = (
    "fonts/manrope-latin.woff2",
    "fonts/instrument-serif-latin.woff2",
    "fonts/figarium-editorial-sc.woff2",
    "fonts/Manrope-OFL.txt",
    "fonts/Instrument-Serif-OFL.txt",
    "fonts/Noto-Serif-SC-OFL.txt",
    "fonts/README.md",
)


class BuildError(ValueError):
    """An input would make the published catalog invalid or unsafe."""


def plain_text(value: str) -> str:
    """Keep content, not README HTML or Markdown presentation instructions."""
    value = LINK_RE.sub(lambda match: match.group(1), value)
    value = re.sub(r"<[^>]*>", "", value)
    value = value.replace("`", "").replace("\\|", "|")
    return html.unescape(value).strip()


def table_cells(line: str) -> list[str]:
    if not line.strip().startswith("|"):
        return []
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", line.strip().strip("|"))]


def http_url(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme.lower() not in {"https", "http"} or not parsed.netloc:
        return ""
    if parsed.username or parsed.password:
        return ""
    return value


def first_url(value: str) -> str:
    for match in LINK_RE.finditer(value):
        if url := http_url(html.unescape(match.group(2))):
            return url
    stripped = value.strip().strip("<>")
    return http_url(stripped)


def inside(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def local_reference(base: Path, reference: str, boundary: Path) -> Path:
    """Resolve a local README reference, including symlinks, without escaping."""
    decoded = html.unescape(unquote(reference)).replace("\\", "/")
    parsed = urlsplit(decoded)
    if parsed.scheme or parsed.netloc or parsed.query or decoded.startswith("/"):
        raise BuildError(f"Expected a plain local file reference: {reference}")
    # A drive-letter path also has a scheme and is rejected above.
    path = (base / parsed.path).resolve()
    if not inside(path, boundary.resolve()):
        raise BuildError(f"Reference escapes its approved directory: {reference}")
    return path


def headings(markdown: str) -> list[tuple[int, int, int, str]]:
    """Return heading offsets, ignoring code comments inside fenced examples."""
    result = []
    offset = 0
    fence = None
    for line in markdown.splitlines(keepends=True):
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
        elif fence is None and (match := re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)):
            result.append((offset, offset + len(line), len(match.group(1)), match.group(2)))
        offset += len(line)
    return result


def read_metadata(markdown: str) -> dict[str, str]:
    marks = headings(markdown)
    metadata = {}
    for position, (_, end, level, title) in enumerate(marks):
        if level != 2 or title.casefold() != "paper information":
            continue
        stop = next((start for start, _, lev, _ in marks[position + 1:] if lev <= level), len(markdown))
        for line in markdown[end:stop].splitlines():
            cells = table_cells(line)
            if len(cells) >= 2 and cells[0].strip("-:"):
                metadata[plain_text(cells[0]).casefold()] = cells[1]
        break
    return metadata


def approved_papers(repo_root: Path) -> list[dict[str, str | Path]]:
    text = (repo_root / "README.md").read_text(encoding="utf-8-sig")
    start_marker, end_marker = "<!-- PAPER_INDEX_START -->", "<!-- PAPER_INDEX_END -->"
    if text.count(start_marker) != 1 or text.count(end_marker) != 1:
        raise BuildError("Root README must contain exactly one marked Paper Index.")
    start, end = text.index(start_marker) + len(start_marker), text.index(end_marker)
    if end < start:
        raise BuildError("Paper Index markers are out of order.")
    result, seen = [], set()
    for line in text[start:end].splitlines():
        cells = table_cells(line)
        if not cells or not (match := LINK_RE.search(cells[0])):
            continue
        reference = match.group(2)
        path = local_reference(repo_root, reference, repo_root)
        relative = path.relative_to(repo_root)
        if len(relative.parts) != 3 or relative.parts[0] != "papers" or relative.name != "README.md":
            raise BuildError(f"Paper Index entry must reference papers/<id>/README.md: {reference}")
        paper_id = relative.parts[1]
        if paper_id in seen:
            raise BuildError(f"Duplicate Paper Index entry: {paper_id}")
        if not path.is_file():
            raise BuildError(f"Indexed paper README does not exist: {reference}")
        seen.add(paper_id)
        result.append({
            "id": paper_id, "path": path, "title": plain_text(match.group(1)),
            "venue": plain_text(cells[1]) if len(cells) > 1 else "",
            "year": plain_text(cells[2]) if len(cells) > 2 else "",
            "topic": plain_text(cells[3]) if len(cells) > 3 else "",
        })
    if not result:
        raise BuildError("The Paper Index has no approved paper entries.")
    return result


class ImageReferences(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.sources = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "img":
            source = dict(attrs).get("src")
            if source:
                self.sources.append(source)


def without_fences(markdown: str) -> str:
    lines, fence = [], None
    for line in markdown.splitlines(keepends=True):
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if match:
            token = match.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is None:
            lines.append(line)
    return "".join(lines)


def code_examples(block: str) -> list[dict[str, str]]:
    examples, active, buffer, language, label, section_label = [], None, [], "", "", "Source"
    for line in block.splitlines(keepends=True):
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})([^\r\n]*)", line)
        if marker:
            token, info = marker.groups()
            if active is None:
                active, buffer = token, []
                language = CODE_LANGUAGES.get(info.strip().split(" ", 1)[0].casefold(), "")
                label = section_label
            elif token[0] == active[0] and len(token) >= len(active) and not info.strip():
                if language:
                    examples.append({"language": language, "label": label, "code": "".join(buffer).rstrip("\r\n") + "\n"})
                active = None
            else:
                buffer.append(line)
        elif active is not None:
            buffer.append(line)
        elif match := re.match(r"^###\s+(.+?)\s*$", line):
            section_label = plain_text(match.group(1))
    if active is not None:
        raise BuildError("An asset has an unclosed fenced code block.")
    return examples


def palette_colors(block: str) -> list[dict[str, str]]:
    colors = []
    for line in block.splitlines():
        cells = table_cells(line)
        if len(cells) == 4 and (match := re.fullmatch(r"`?(#[0-9A-Fa-f]{6})`?", cells[3])):
            colors.append({"role": plain_text(cells[0]), "color": plain_text(cells[2]), "hex": match.group(1).upper()})
    return colors


def section_type(title: str) -> str | None:
    title = re.sub(r"^\d+\.\s*", "", title).casefold()
    return {"method figures": "method", "result analysis figures": "result", "result figures": "result", "paper tables": "table", "tables": "table"}.get(title)


def github_readme(repository_url: str, paper_id: str, anchor: str = "") -> str:
    url = f"{repository_url.rstrip('/')}/blob/main/papers/{quote(paper_id, safe='')}/README.md"
    return url + ("#" + anchor if anchor else "")


def heading_anchor(title: str) -> str:
    return re.sub(r"[^\w\- ]", "", plain_text(title).casefold()).replace(" ", "-")


@lru_cache(maxsize=1)
def pptx_qa_module():
    """Load the repository's trusted standard-library package validator lazily."""
    helper = Path(__file__).resolve().parent.parent / "paper-asset-builder" / "scripts" / "method_pptx_qa.py"
    if not helper.is_file():
        raise BuildError("Local PPTX publishing requires paper-asset-builder/scripts/method_pptx_qa.py.")
    name = "_figarium_method_pptx_qa"
    spec = importlib.util.spec_from_file_location(name, helper)
    if spec is None or spec.loader is None:
        raise BuildError("The PPTX package validator could not be loaded.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(name, None)
        raise
    return module


def pptx_downloads(value: str, paper_dir: Path, paper_id: str, *, combined: bool = False) -> tuple[list[dict], list[tuple[Path, str]]]:
    """Publish only explicitly linked method decks, not every nearby PPTX."""
    paper_dir = paper_dir.resolve()
    downloads, copies = [], []
    for link in LINK_RE.finditer(value):
        target = html.unescape(link.group(2))
        external = http_url(target)
        label = "Method figures PPTX (combined)" if combined else "PPTX"
        if external:
            downloads.append({
                "label": label + " (external)", "url": external, "format": "pptx",
                "filename": unquote(PurePosixPath(urlsplit(external).path).name), "local": False,
                "validation": "External source link; package and editability have not been checked by the static builder.",
            })
            continue
        decoded = html.unescape(unquote(target)).replace("\\", "/")
        parsed = urlsplit(decoded)
        if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment:
            raise BuildError(f"{paper_id}: expected a plain local method PPTX reference: {target}")
        # Reject traversal and all symlink/junction components, even aliases
        # that happen to resolve to another file inside the paper directory.
        local = output_target(paper_dir, parsed.path)
        relative = local.relative_to(paper_dir)
        if len(relative.parts) < 2 or relative.parts[0] != "method_figures" or local.suffix.lower() != ".pptx":
            raise BuildError(f"{paper_id}: local PPTX must be inside method_figures/: {target}")
        if not local.is_file():
            raise BuildError(f"{paper_id}: linked PPTX does not exist: {target}")
        qa = pptx_qa_module()
        try:
            qa.validate_pptx_package(local)
        except qa.PptxQAError as error:
            raise BuildError(f"{paper_id}: invalid PPTX package {relative.as_posix()}: {error}") from error
        destination = f"assets/papers/{paper_id}/{relative.as_posix()}"
        downloads.append({
            "label": label, "url": quote(destination, safe="/"), "format": "pptx",
            "filename": local.name, "local": True,
            "validation": "OOXML package checked. The static builder does not verify visual fidelity or native object editability.",
        })
        copies.append((local, destination))
    return downloads, copies


def has_local_pptx(asset: dict) -> bool:
    return any(download.get("format") == "pptx" and download.get("local") is True for download in asset.get("downloads", []))


def has_source(asset: dict) -> bool:
    return bool(asset.get("codes")) or has_local_pptx(asset)


def parse_paper(entry: dict, site: dict) -> tuple[dict, list[dict], list[tuple[Path, str]]]:
    paper_dir = entry["path"].parent
    markdown = entry["path"].read_text(encoding="utf-8-sig")
    metadata = read_metadata(markdown)
    paper_id = entry["id"]
    paper = {
        "id": paper_id,
        "title": plain_text(metadata.get("title", entry["title"])),
        "topic": plain_text(metadata.get("topic", entry["topic"])),
        "venue": plain_text(metadata.get("venue", entry["venue"])),
        "year": plain_text(metadata.get("year", entry["year"])),
        "paperUrl": first_url(metadata.get("paper link", metadata.get("paper", ""))),
        "readmeUrl": github_readme(site["repositoryUrl"], paper_id),
        "authors": plain_text(metadata.get("authors", NOT_DOCUMENTED)),
        "license": plain_text(metadata.get("original asset license", metadata.get("license", NOT_DOCUMENTED))),
    }
    assets, copies, seen = [], [], set()
    paper["downloads"], combined_copies = pptx_downloads(metadata.get("method figures ppt", ""), paper_dir, paper_id, combined=True)
    copies.extend(combined_copies)
    marks = headings(markdown)
    kind = None
    for position, (start, end, level, title) in enumerate(marks):
        if level == 1:
            kind = section_type(title)
            continue
        if level != 2 or kind is None or not re.match(r"^(?:Figure|Table)\s+[^:]+:\s*.+", title, re.I):
            continue
        stop = next((offset for offset, _, lev, _ in marks[position + 1:] if lev <= 2), len(markdown))
        block = markdown[end:stop]
        prose = without_fences(block)
        parser = ImageReferences()
        parser.feed(prose)
        references = parser.sources + re.findall(r"!\[[^\]]*\]\(([^\s)]+)\)", prose)
        image = None
        for reference in references:
            if urlsplit(reference).scheme or reference.startswith("//"):
                continue
            candidate = local_reference(paper_dir, reference, paper_dir)
            relative = candidate.relative_to(paper_dir)
            if not relative.parts or relative.parts[0] != TYPE_FOLDERS[kind]:
                raise BuildError(f"{paper_id}: {title}: image is outside {TYPE_FOLDERS[kind]}/")
            if candidate.suffix.lower() not in IMAGE_SUFFIXES or not candidate.is_file():
                raise BuildError(f"{paper_id}: missing or unsupported image: {reference}")
            image = candidate
            break
        if image is None:
            raise BuildError(f"{paper_id}: {title}: no local approved preview image.")
        if image in seen:
            continue
        seen.add(image)
        relative = image.relative_to(paper_dir).as_posix()
        destination = f"assets/papers/{paper_id}/{relative}"
        fields = {}
        for line in prose.splitlines():
            cells = table_cells(line)
            if len(cells) == 2:
                fields[plain_text(cells[0]).casefold()] = cells[1]
        source = plain_text(fields.get("source", ""))
        source_match = re.search(r"\b((?:Figure|Fig\.?|Table)\s+[A-Za-z]?\d+(?:[A-Za-z]|\.\d+)?)", source, re.I)
        page_match = re.search(r"\b(?:PDF\s+)?page\s+(\d+)\b", source, re.I)
        label_match = re.match(r"^((?:Figure|Table)\s+[^:]+):\s*(.+)", title, re.I)
        downloads = [{"label": "Image", "url": quote(destination, safe="/")}]
        ppt_value = fields.get("ppt source", "")
        if LINK_RE.search(ppt_value) and kind != "method":
            raise BuildError(f"{paper_id}: PPT Source belongs to a method figure, not {kind}: {title}")
        presentations, presentation_copies = pptx_downloads(ppt_value, paper_dir, paper_id)
        downloads.extend(presentations)
        copies.extend(presentation_copies)
        asset = {
            "id": f"{paper_id}--{kind}--{image.stem}", "paperId": paper_id,
            "title": plain_text(label_match.group(2)), "type": kind,
            "src": quote(destination, safe="/"), "filename": image.name,
            "sourceLabel": source_match.group(1) if source_match else label_match.group(1),
            "page": int(page_match.group(1)) if page_match else None,
            "approximate": bool(re.search(r"\bapproximate(?:ly)?\b|\bestimat(?:ed|ion|ing)\b|\b(?:structural|schematic) reconstruction\b|\bsimplif(?:ied|ication)\b|近似|估读|简化", prose, re.I)),
            "validation": plain_text(metadata.get("latex validation", NOT_DOCUMENTED)) if kind == "table" else NOT_DOCUMENTED,
            "codes": code_examples(block), "palette": palette_colors(prose),
            "downloads": downloads,
            "readmeUrl": github_readme(site["repositoryUrl"], paper_id, heading_anchor(title)),
            "paperUrl": paper["paperUrl"],
        }
        assets.append(asset)
        copies.append((image, destination))
    return paper, assets, copies


def load_site(repo_root: Path) -> dict:
    site = dict(DEFAULT_SITE)
    config = repo_root / "website" / "figarium.config.json"
    if config.is_file():
        values = json.loads(config.read_text(encoding="utf-8-sig"))
        if not isinstance(values, dict):
            raise BuildError("figarium.config.json must contain an object.")
        for key in DEFAULT_SITE:
            if key in values:
                expected = list if key == "featuredPaperIds" else str
                if not isinstance(values[key], expected):
                    raise BuildError(f"Invalid configuration value for {key}.")
                site[key] = values[key]
    if not http_url(site["repositoryUrl"]):
        raise BuildError("repositoryUrl must be an HTTP(S) repository URL.")
    if not all(isinstance(paper_id, str) for paper_id in site["featuredPaperIds"]):
        raise BuildError("featuredPaperIds must contain only strings.")
    return site


def make_catalog(repo_root: Path) -> tuple[dict, list[tuple[Path, str]]]:
    repo_root = repo_root.resolve()
    site = load_site(repo_root)
    papers, assets, copies = [], [], []
    for entry in approved_papers(repo_root):
        paper, figures, files = parse_paper(entry, site)
        papers.append(paper)
        assets.extend(figures)
        copies.extend(files)
    unique_copies = {}
    for source, destination in copies:
        if destination in unique_copies and source != unique_copies[destination]:
            raise BuildError(f"Conflicting generated files: {destination}")
        unique_copies[destination] = source
    copies = [(source, destination) for destination, source in unique_copies.items()]
    ids = [asset["id"] for asset in assets]
    if len(ids) != len(set(ids)):
        raise BuildError("Asset IDs must be unique; avoid duplicate image stems within an asset type.")
    site["featuredPaperIds"] = [paper_id for paper_id in site["featuredPaperIds"] if any(paper["id"] == paper_id for paper in papers)]
    counts = {kind: sum(asset["type"] == kind for asset in assets) for kind in TYPE_FOLDERS}
    catalog = {
        "site": site,
        "stats": {"paperCount": len(papers), "assetCount": len(assets), "sourceCount": sum(has_source(asset) for asset in assets), "pptxCount": sum(has_local_pptx(asset) for asset in assets), "counts": counts},
        "papers": papers, "assets": assets,
    }
    return catalog, copies


def javascript_payload(catalog: dict) -> str:
    # Also safe when a future host chooses to embed this assignment in <script>.
    payload = json.dumps(catalog, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    return "window.FIGARIUM_CATALOG = " + payload + ";\n"


def output_target(out: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative or ":" in relative:
        raise BuildError(f"Invalid generated relative path: {relative}")
    path = PurePosixPath(relative)
    if path.is_absolute() or path.as_posix() != relative or any(part in {".", ".."} for part in path.parts):
        raise BuildError(f"Invalid generated relative path: {relative}")
    target = out
    for part in path.parts:
        target = target / part
        if target.is_symlink() or getattr(target, "is_junction", lambda: False)():
            raise BuildError(f"Generated output cannot traverse a symlink or junction: {relative}")
    target = target.resolve()
    if not inside(target, out.resolve()):
        raise BuildError(f"Output target escapes the output directory: {relative}")
    return target


def generated_kind(relative: str) -> str | None:
    """The only namespaces whose previous generation records are trusted."""
    if not isinstance(relative, str) or "\\" in relative or ":" in relative:
        return None
    path = PurePosixPath(relative)
    if path.is_absolute() or path.as_posix() != relative or any(part in {".", ".."} for part in path.parts):
        return None
    if relative in FRONTEND_FILES + CATALOG_FILES:
        return "site"
    if relative in FONT_FILES:
        return "font"
    if relative in tuple(f"guides/{name}" for name in GUIDE_FILES):
        return "guide"
    parts = path.parts
    if (len(parts) >= 5 and parts[:2] == ("assets", "papers")
            and parts[3] in TYPE_FOLDERS.values() and path.suffix.lower() in IMAGE_SUFFIXES):
        return "image"
    if (len(parts) >= 5 and parts[:2] == ("assets", "papers")
            and parts[3] == "method_figures" and path.suffix.lower() == ".pptx"):
        return "presentation"
    return None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def previous_generated_files(out: Path) -> dict[str, str]:
    manifest = output_target(out, GENERATED_MANIFEST)
    if not manifest.exists():
        # A first build must not guess which preexisting files belong to it.
        return {}
    if not manifest.is_file():
        raise BuildError("The generated-file manifest is not a regular file.")
    try:
        data = json.loads(manifest.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as error:
        raise BuildError("Cannot read the previous generated-file manifest; no files were removed.") from error
    if (not isinstance(data, dict) or data.get("schema") != MANIFEST_SCHEMA
            or type(data.get("version")) is not int or data["version"] != 1
            or not isinstance(data.get("files"), list)):
        raise BuildError("Unsupported or invalid generated-file manifest; no files were removed.")
    previous = {}
    for record in data["files"]:
        if not isinstance(record, dict):
            raise BuildError("Invalid file record in the generated-file manifest.")
        relative, digest = record.get("path"), record.get("sha256")
        if (generated_kind(relative) is None or not isinstance(digest, str)
                or re.fullmatch(r"[0-9a-f]{64}", digest) is None or relative in previous):
            raise BuildError("Unsafe, duplicate or invalid path/hash in the generated-file manifest.")
        # Validate even retained records before any output writes or cleanup.
        output_target(out, relative)
        previous[relative] = digest
    return previous


def stale_generated_files(out: Path, previous: dict[str, str], current: set[str]) -> list[tuple[str, str]]:
    stale = []
    for relative, digest in previous.items():
        if relative in current or generated_kind(relative) not in {"image", "guide", "presentation", "font"}:
            continue
        target = output_target(out, relative)
        if not target.exists():
            continue
        if not target.is_file() or sha256_file(target) != digest:
            raise BuildError(
                f"Stale generated file was modified and has been preserved: {relative}. "
                "Move or remove it explicitly before rebuilding for publication."
            )
        stale.append((relative, digest))
    return stale


def build(repo_root: Path, out: Path) -> dict:
    repo_root, out = repo_root.resolve(), out.resolve()
    if out == repo_root or inside(repo_root, out):
        raise BuildError("Output directory cannot be the repository root or its parent.")
    catalog, copies = make_catalog(repo_root)
    frontend = repo_root / "website"
    for name in FRONTEND_FILES:
        if not (frontend / name).is_file():
            raise BuildError(f"Website source is missing: website/{name}")
    planned_copies = copies + [(frontend / name, name) for name in FRONTEND_FILES]
    for relative in FONT_FILES:
        # Reuse the same component-by-component symlink/junction and traversal
        # check as generated outputs, now bounded to the frontend source root.
        source = output_target(frontend, relative)
        if not source.is_file():
            raise BuildError(f"Website font source is missing: website/{relative}")
        planned_copies.append((source, relative))
    # Publish only these explicit guides as inert Markdown text, not arbitrary
    # docs/ content or generated HTML. Links remain usable before a Git push.
    for name in GUIDE_FILES:
        source = repo_root / "docs" / name
        if source.is_file():
            if not inside(source.resolve(), (repo_root / "docs").resolve()) or not inside(source.resolve(), repo_root):
                raise BuildError(f"Guide source escapes docs/: {name}")
            planned_copies.append((source, f"guides/{name}"))
    planned_text = {
        "catalog.json": json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        "catalog.js": javascript_payload(catalog),
    }
    current = {relative for _, relative in planned_copies} | set(planned_text)
    for relative in current:
        if generated_kind(relative) is None:
            raise BuildError(f"File is outside the generated namespaces: {relative}")
        output_target(out, relative)
    previous = previous_generated_files(out)
    # Preflight all stale files before touching any output. One user-modified
    # file blocks publication without deleting any of the other stale files.
    stale = stale_generated_files(out, previous, current)
    out.mkdir(parents=True, exist_ok=True)
    for source, relative in planned_copies:
        target = output_target(out, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.resolve() != target:
            shutil.copy2(source, target)
    for relative, text in planned_text.items():
        output_target(out, relative).write_text(text, encoding="utf-8")
    for relative, digest in stale:
        # Revalidate immediately before unlinking, including link components,
        # so an intervening local edit is preserved rather than overwritten.
        target = output_target(out, relative)
        if not target.is_file() or sha256_file(target) != digest:
            raise BuildError(f"Stale generated file changed during build and was preserved: {relative}")
        target.unlink()
    manifest = {
        "schema": MANIFEST_SCHEMA, "version": 1,
        "files": [{"path": relative, "sha256": sha256_file(output_target(out, relative))} for relative in sorted(current)],
    }
    output_target(out, GENERATED_MANIFEST).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if stale:
        print(f"Figarium removed {len(stale)} unchanged stale generated image/guide/PPTX/font file(s); unknown files were preserved.")
    return catalog


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--out", type=Path, help="Output directory (default: <repo-root>/website/dist)")
    arguments = parser.parse_args(argv)
    out = arguments.out or arguments.repo_root / "website" / "dist"
    try:
        catalog = build(arguments.repo_root, out)
    except (BuildError, OSError, json.JSONDecodeError) as error:
        print(f"Figarium build failed: {error}", file=sys.stderr)
        return 1
    stats = catalog["stats"]
    print(f"Figarium: {stats['paperCount']} papers, {stats['assetCount']} figures, {stats['sourceCount']} with reconstruction source -> {out.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
