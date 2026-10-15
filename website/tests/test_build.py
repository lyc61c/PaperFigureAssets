"""Offline tests for Figarium's README-to-catalog boundary."""

import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile


BUILDER = Path(__file__).resolve().parents[1] / "build.py"
SPEC = importlib.util.spec_from_file_location("figarium_build", BUILDER)
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


ROOT_README = """# Collection
<!-- PAPER_INDEX_START -->
| Paper | Venue | Year | Topic | Assets |
|---|---|---|---|---|
| [Approved paper](papers/approved/README.md) | arXiv | 2026 | Test research | 3 |
<!-- PAPER_INDEX_END -->
"""

PAPER_README = '''<h1>Approved paper</h1>
## Paper Information
| Field | Value |
|---|---|
| Title | Approved <em>paper</em> |
| Venue | arXiv |
| Year | 2026 |
| Topic | Test research |
| Authors | Ada Example |
| Paper Link | [paper](https://example.com/paper) |
| Original Asset License | Rights reserved; permission not documented |
| LaTeX Validation | One table compiled and visually checked. |
## Asset Preview Gallery
<img src="method_figures/method.png">
<img src="result_figures/result.png">
<img src="tables/table.png">
# 1. Method Figures
## Figure 1: Reviewed framework
<img src="method_figures/method.png" alt="Framework">
| Asset | Link |
|---|---|
| Preview Image | [preview](method_figures/method.png) |
| PPT Source | Not available |
| Source | Figure 2, PDF page 3 of [paper](https://example.com/paper) |
### Color Palette
| Role | Swatch | Color | Hex |
|---|---|---|---|
| Main path | irrelevant | Teal | `#0F766E` |
# 2. Result Analysis Figures
## Figure 2: Measured result
<img src="result_figures/result.png">
### Plotting Code
Note: This is an approximate visual reconstruction.
```python
# 1. Method Figures
raise RuntimeError("This code must never run.")
unsafe = "</script><script>alert(1)</script>\u2028\u2029"
```
# 3. Paper Tables
## Table 1: Evaluation
<img src="tables/table.png">
### LaTeX Source
```latex
\\begin{tabular}{lr} Model & 1 \\\\ \\end{tabular}
```
### Required Packages
```latex
\\usepackage{booktabs}
```
'''


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="figarium-build-test-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / "README.md").write_text(ROOT_README, encoding="utf-8")
        self.paper = self.root / "papers" / "approved"
        self.paper.mkdir(parents=True)
        (self.paper / "README.md").write_text(PAPER_README, encoding="utf-8")
        for folder, name in (("method_figures", "method.png"), ("result_figures", "result.png"), ("tables", "table.png")):
            (self.paper / folder).mkdir()
            (self.paper / folder / name).write_bytes(b"fixture-image-not-rendered")
        website = self.root / "website"
        website.mkdir()
        for name in ("index.html", "styles.css", "app.js"):
            (website / name).write_text("fixture", encoding="utf-8")
        for relative in builder.FONT_FILES:
            target = website / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"fixture-font-or-license-not-rendered")

    def replace_paper(self, old, new):
        path = self.paper / "README.md"
        path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")

    def make_pptx(self, name="method.pptx"):
        """A minimal OOXML format fixture, not a visual-fidelity test deck."""
        path = self.paper / "method_figures" / name
        parts = {
            "[Content_Types].xml": '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/><Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/></Types>',
            "_rels/.rels": '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/></Relationships>',
            "ppt/presentation.xml": '<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><p:sldIdLst><p:sldId id="256" r:id="rId1"/></p:sldIdLst><p:sldSz cx="9144000" cy="5143500"/></p:presentation>',
            "ppt/_rels/presentation.xml.rels": '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/></Relationships>',
            "ppt/slides/slide1.xml": '<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><p:cSld><p:spTree><p:sp><p:nvSpPr><p:cNvPr id="2" name="Editable text"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:t>Editable fixture</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld></p:sld>',
        }
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as package:
            for member, content in parts.items():
                package.writestr(member, content)
        return path

    def link_pptx(self, name="method.pptx", *, combined=False):
        path = self.make_pptx(name)
        if combined:
            self.replace_paper("| Authors | Ada Example |", f"| Authors | Ada Example |\n| Method Figures PPT | [Combined editable deck](method_figures/{name}) |")
        else:
            self.replace_paper("| PPT Source | Not available |", f"| PPT Source | [Deck](method_figures/{name}) |")
        return path

    def remove_asset_type(self, kind):
        path = self.paper / "README.md"
        text = path.read_text(encoding="utf-8")
        marks = builder.headings(text)
        start, end, _, title = next(mark for mark in marks if mark[2] == 1 and builder.section_type(mark[3]) == kind)
        stop = next((offset for offset, _, level, _ in marks if offset > start and level == 1), len(text))
        path.write_text(text[:start] + "# " + title + "\n\nNo approved assets of this type.\n\n" + text[stop:], encoding="utf-8")
        for image in (self.paper / builder.TYPE_FOLDERS[kind]).iterdir():
            image.unlink()

    def test_index_is_only_publish_allowlist(self):
        for folder in ("papers/新建文件夹", "materials/unreviewed", "tmp/private"):
            path = self.root / folder
            path.mkdir(parents=True)
            (path / "README.md").write_text("Broken unapproved README", encoding="utf-8")
            (path / "secret.pdf").write_bytes(b"not public")
        catalog, copies = builder.make_catalog(self.root)
        self.assertEqual([paper["id"] for paper in catalog["papers"]], ["approved"])
        self.assertEqual(len(copies), 3)
        self.assertNotIn("secret.pdf", json.dumps(catalog))

    def test_standalone_index_works_without_a_root_readme_and_preserves_catalog(self):
        expected, expected_copies = builder.make_catalog(self.root)
        (self.root / "PAPER_INDEX.md").write_text(ROOT_README, encoding="utf-8")
        (self.root / "README.md").unlink()
        catalog, copies = builder.make_catalog(self.root)
        self.assertEqual(catalog, expected)
        self.assertEqual(copies, expected_copies)

    def test_standalone_index_takes_precedence_without_publishing_stale_root_entries(self):
        (self.root / "PAPER_INDEX.md").write_text(ROOT_README, encoding="utf-8")
        private = self.root / "papers" / "private"
        shutil.copytree(self.paper, private)
        stale_row = "| [Private draft](papers/private/README.md) | Internal | 2026 | Private | 3 |\n"
        (self.root / "README.md").write_text(ROOT_README.replace("<!-- PAPER_INDEX_END -->", stale_row + "<!-- PAPER_INDEX_END -->"), encoding="utf-8")
        out = self.root / "website" / "dist"
        catalog = builder.build(self.root, out)
        self.assertEqual([paper["id"] for paper in catalog["papers"]], ["approved"])
        self.assertFalse((out / "assets/papers/private").exists())
        self.assertTrue((private / "README.md").is_file())
        # A landing page need not contain a table at all after migration.
        (self.root / "README.md").write_text("# A concise landing page\n", encoding="utf-8")
        self.assertEqual(builder.make_catalog(self.root)[0], catalog)

    def test_standalone_index_uses_root_relative_paths_and_preserves_order_and_metadata(self):
        other = self.root / "papers" / "Other Paper"
        shutil.copytree(self.paper, other)
        row = "| [Other title](papers/Other%20Paper/README.md) | Example venue | 2027 | Another topic | 3 |\n"
        original = "| [Approved paper](papers/approved/README.md) | arXiv | 2026 | Test research | 3 |"
        (self.root / "PAPER_INDEX.md").write_text(ROOT_README.replace(original, row + original), encoding="utf-8")
        entries = builder.approved_papers(self.root)
        self.assertEqual([entry["id"] for entry in entries], ["Other Paper", "approved"])
        self.assertEqual(entries[0], {"id": "Other Paper", "path": (other / "README.md").resolve(), "title": "Other title", "venue": "Example venue", "year": "2027", "topic": "Another topic"})
        self.assertEqual([paper["id"] for paper in builder.make_catalog(self.root)[0]["papers"]], ["Other Paper", "approved"])

    def test_invalid_standalone_index_never_falls_back_to_valid_legacy_readme(self):
        row = "| [Approved paper](papers/approved/README.md) | arXiv | 2026 | Test research | 3 |"
        invalid = (
            "", "# Index with no markers\n", ROOT_README.replace("<!-- PAPER_INDEX_END -->", ""),
            ROOT_README + "<!-- PAPER_INDEX_START -->",
            "<!-- PAPER_INDEX_END -->\n<!-- PAPER_INDEX_START -->",
            ROOT_README.replace(row, ""),
            ROOT_README.replace(row, row + "\n| Broken entry | arXiv | 2026 | Test | 3 |"),
            ROOT_README.replace(row, row + "\n" + row),
            ROOT_README.replace("papers/approved/README.md", "../secret/README.md"),
            ROOT_README.replace("papers/approved/README.md", "materials/approved/README.md"),
            ROOT_README.replace("papers/approved/README.md", "papers/missing/README.md"),
        )
        for content in invalid:
            (self.root / "PAPER_INDEX.md").write_text(content, encoding="utf-8")
            with self.subTest(content=content), self.assertRaises(builder.BuildError):
                builder.make_catalog(self.root)

    def test_non_utf8_standalone_index_fails_closed(self):
        (self.root / "PAPER_INDEX.md").write_bytes(b"\xff\xfe\x00")
        with self.assertRaisesRegex(builder.BuildError, "Cannot read PAPER_INDEX.md"):
            builder.make_catalog(self.root)

    def test_standalone_index_directory_fails_closed(self):
        (self.root / "PAPER_INDEX.md").mkdir()
        with self.assertRaisesRegex(builder.BuildError, "regular file"):
            builder.make_catalog(self.root)

    def test_standalone_index_symlinks_fail_closed_when_supported(self):
        index = self.root / "PAPER_INDEX.md"
        targets = (self.root / "README.md", self.root / "missing-index.md", self.root.parent / "outside-index.md")
        for target in targets:
            try:
                index.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("File symlinks are unavailable on this system.")
            try:
                with self.subTest(target=target), self.assertRaisesRegex(builder.BuildError, "regular file"):
                    builder.make_catalog(self.root)
            finally:
                index.unlink()

    def test_legacy_index_still_works_only_when_standalone_is_absent(self):
        self.assertFalse((self.root / "PAPER_INDEX.md").exists())
        self.assertEqual([entry["id"] for entry in builder.approved_papers(self.root)], ["approved"])
        (self.root / "README.md").write_text("# No approvals\n", encoding="utf-8")
        with self.assertRaisesRegex(builder.BuildError, "exactly one marked Paper Index"):
            builder.make_catalog(self.root)

    def test_removing_standalone_entry_prunes_export_without_using_stale_root_index(self):
        other = self.root / "papers" / "other"
        shutil.copytree(self.paper, other)
        row = "| [Other paper](papers/other/README.md) | arXiv | 2026 | Another topic | 3 |\n"
        content = ROOT_README.replace("<!-- PAPER_INDEX_END -->", row + "<!-- PAPER_INDEX_END -->")
        index = self.root / "PAPER_INDEX.md"
        index.write_text(content, encoding="utf-8")
        (self.root / "README.md").write_text(content, encoding="utf-8")
        out = self.root / "website" / "dist"
        builder.build(self.root, out)
        index.write_text(ROOT_README, encoding="utf-8")
        catalog = builder.build(self.root, out)
        self.assertEqual([paper["id"] for paper in catalog["papers"]], ["approved"])
        self.assertEqual(list((out / "assets/papers/other").rglob("*.png")), [])
        self.assertTrue((other / "README.md").is_file())

    def test_gallery_duplicates_are_not_catalog_assets(self):
        catalog, _ = builder.make_catalog(self.root)
        self.assertEqual(catalog["stats"], {"paperCount": 1, "assetCount": 3, "sourceCount": 2, "pptxCount": 0, "counts": {"method": 1, "result": 1, "table": 1}})
        self.assertEqual(len({asset["src"] for asset in catalog["assets"]}), 3)

    def test_metadata_palette_provenance_and_license_are_truthful(self):
        catalog, _ = builder.make_catalog(self.root)
        paper = catalog["papers"][0]
        self.assertEqual(paper["title"], "Approved paper")
        self.assertEqual(paper["authors"], "Ada Example")
        self.assertIn("permission not documented", paper["license"])
        method = catalog["assets"][0]
        self.assertEqual(method["sourceLabel"], "Figure 2")
        self.assertEqual(method["page"], 3)
        self.assertEqual(method["palette"], [{"role": "Main path", "color": "Teal", "hex": "#0F766E"}])
        self.assertEqual(method["paletteSource"], "readme")
        self.assertEqual(len(method["downloads"]), 1)
        self.assertTrue(catalog["assets"][1]["approximate"])
        self.assertFalse(method["approximate"])
        self.assertIn("visually checked", catalog["assets"][2]["validation"])

    def test_sampled_palette_has_provenance_without_claiming_estimated_data(self):
        palette = "\n### Color Palette\n\n" + builder.SAMPLED_PALETTE_NOTE + "\n\n| Role | Swatch | Color | Hex |\n|---|---|---|---|\n| Representative color 1 | square | Blue | `#237ABC` |\n"
        self.replace_paper("Note: This is an approximate visual reconstruction.", "Values transcribed from published annotations.")
        self.replace_paper("### Plotting Code", palette + "\n### Plotting Code")
        catalog, _ = builder.make_catalog(self.root)
        result = next(asset for asset in catalog["assets"] if asset["type"] == "result")
        self.assertEqual(result["paletteSource"], "image-sample")
        self.assertEqual(result["palette"][0]["hex"], "#237ABC")
        self.assertFalse(result["approximate"])
        self.replace_paper("Values transcribed from published annotations.", "Values are estimated.")
        catalog, _ = builder.make_catalog(self.root)
        self.assertTrue(next(asset for asset in catalog["assets"] if asset["type"] == "result")["approximate"])

    def test_real_approximation_note_inside_palette_section_is_preserved(self):
        self.replace_paper("Note: This is an approximate visual reconstruction.", "")
        palette = "### Color Palette\n\n" + builder.SAMPLED_PALETTE_NOTE + "\n\nData values in the reconstruction were estimated from the chart.\n\n"
        self.replace_paper("### Plotting Code", palette + "### Plotting Code")
        catalog, _ = builder.make_catalog(self.root)
        self.assertTrue(next(asset for asset in catalog["assets"] if asset["type"] == "result")["approximate"])

    def test_tables_never_publish_palette_metadata(self):
        self.replace_paper("### LaTeX Source", "### Color Palette\n| Role | Swatch | Color | Hex |\n|---|---|---|---|\n| Header | square | Blue | `#237ABC` |\n\n### LaTeX Source")
        catalog, _ = builder.make_catalog(self.root)
        table = next(asset for asset in catalog["assets"] if asset["type"] == "table")
        self.assertEqual(table["palette"], [])
        self.assertEqual(table["paletteSource"], "")

    def test_examples_are_inert_text_and_packages_are_separate(self):
        catalog, _ = builder.make_catalog(self.root)
        code = catalog["assets"][1]["codes"][0]
        self.assertIn("RuntimeError", code["code"])
        self.assertIn("</script>", code["code"])
        self.assertEqual(code["language"], "python")
        table = catalog["assets"][2]
        self.assertEqual([code["label"] for code in table["codes"]], ["LaTeX Source", "Required Packages"])
        self.assertEqual(catalog["stats"]["sourceCount"], sum(bool(asset["codes"]) for asset in catalog["assets"]))

    def test_javascript_payload_cannot_close_script_or_split_lines(self):
        catalog, _ = builder.make_catalog(self.root)
        payload = builder.javascript_payload(catalog)
        self.assertNotIn("<", payload)
        self.assertNotIn("\u2028", payload)
        self.assertNotIn("\u2029", payload)
        decoded = json.loads(payload.removeprefix("window.FIGARIUM_CATALOG = ").removesuffix(";\n"))
        self.assertEqual(decoded, catalog)

    def test_image_path_traversal_is_rejected(self):
        self.replace_paper('src="method_figures/method.png" alt=', 'src="../../secret.png" alt=')
        with self.assertRaisesRegex(builder.BuildError, "escapes"):
            builder.make_catalog(self.root)

    def test_percent_encoded_and_windows_traversal_are_rejected(self):
        for reference in ("%2e%2e/%2e%2e/secret.png", "..\\..\\secret.png", "C:/private/image.png"):
            with self.subTest(reference=reference), self.assertRaises(builder.BuildError):
                builder.local_reference(self.paper, reference, self.paper)

    def test_index_path_traversal_and_noncanonical_paths_are_rejected(self):
        for reference in ("../secret/README.md", "materials/approved/README.md", "https://example.com/paper.md"):
            (self.root / "README.md").write_text(ROOT_README.replace("papers/approved/README.md", reference), encoding="utf-8")
            with self.subTest(reference=reference), self.assertRaises(builder.BuildError):
                builder.make_catalog(self.root)

    def test_missing_image_fails_instead_of_silent_publication(self):
        (self.paper / "method_figures" / "method.png").unlink()
        with self.assertRaisesRegex(builder.BuildError, "missing or unsupported"):
            builder.make_catalog(self.root)

    def test_build_preserves_unknown_output_files_and_copies_only_approved_images(self):
        out = self.root / "website" / "dist"
        out.mkdir()
        (out / "keep-me.txt").write_text("user-owned", encoding="utf-8")
        (self.paper / "paper.pdf").write_bytes(b"not published")
        builder.build(self.root, out)
        self.assertEqual((out / "keep-me.txt").read_text(encoding="utf-8"), "user-owned")
        copied = list((out / "assets").rglob("*.*"))
        self.assertEqual(len(copied), 3)
        self.assertTrue(all(path.suffix == ".png" for path in copied))
        self.assertEqual(json.loads((out / "catalog.json").read_text(encoding="utf-8"))["stats"]["assetCount"], 3)
        self.assertFalse((out / ".openai").exists())

    def test_generated_manifest_contains_only_relative_paths_and_matching_hashes(self):
        out = self.root / "website" / "dist"
        builder.build(self.root, out)
        text = (out / builder.GENERATED_MANIFEST).read_text(encoding="utf-8")
        manifest = json.loads(text)
        self.assertEqual(manifest["schema"], builder.MANIFEST_SCHEMA)
        self.assertEqual(manifest["version"], 1)
        self.assertNotIn(str(self.root), text)
        self.assertEqual(len(manifest["files"]), 3 + len(builder.FRONTEND_FILES) + len(builder.CATALOG_FILES) + len(builder.FONT_FILES))
        for record in manifest["files"]:
            self.assertIsNotNone(builder.generated_kind(record["path"]))
            self.assertEqual(record["sha256"], builder.sha256_file(out / record["path"]))

    def test_removed_approved_figure_is_pruned_without_removing_unknown_files_or_directories(self):
        out = self.root / "website" / "dist"
        builder.build(self.root, out)
        stale = out / "assets/papers/approved/result_figures/result.png"
        unknown = stale.parent / "my-notes.png"
        unknown.write_bytes(b"user-owned, never generated")
        self.remove_asset_type("result")
        catalog = builder.build(self.root, out)
        self.assertEqual(catalog["stats"]["assetCount"], 2)
        self.assertFalse(stale.exists())
        self.assertEqual(unknown.read_bytes(), b"user-owned, never generated")
        self.assertTrue(stale.parent.is_dir())
        self.assertNotIn("result_figures/result.png", (out / builder.GENERATED_MANIFEST).read_text(encoding="utf-8"))

    def test_only_explicit_fonts_and_licenses_are_published_and_recorded(self):
        frontend = self.root / "website"
        (frontend / "fonts/private-draft.woff2").write_bytes(b"Unapproved working font")
        (frontend / "fonts/private-notes.txt").write_text("Private", encoding="utf-8")
        out = frontend / "dist"
        (out / "fonts").mkdir(parents=True)
        (out / "fonts/user-owned.woff2").write_bytes(b"User-owned output")
        builder.build(self.root, out)
        manifest = json.loads((out / builder.GENERATED_MANIFEST).read_text(encoding="utf-8"))
        recorded = {record["path"] for record in manifest["files"] if record["path"].startswith("fonts/")}
        self.assertEqual(recorded, set(builder.FONT_FILES))
        for relative in builder.FONT_FILES:
            self.assertEqual((out / relative).read_bytes(), (frontend / relative).read_bytes())
        self.assertFalse((out / "fonts/private-draft.woff2").exists())
        self.assertFalse((out / "fonts/private-notes.txt").exists())
        self.assertEqual((out / "fonts/user-owned.woff2").read_bytes(), b"User-owned output")
        self.assertIsNone(builder.generated_kind("fonts/private-draft.woff2"))

    def test_missing_required_font_fails_before_output_writes(self):
        (self.root / "website" / builder.FONT_FILES[0]).unlink()
        out = self.root / "website" / "dist"
        with self.assertRaisesRegex(builder.BuildError, "font source is missing"):
            builder.build(self.root, out)
        self.assertFalse(out.exists())

    def test_font_source_symlink_is_rejected_when_supported(self):
        source = self.root / "website" / builder.FONT_FILES[0]
        source.unlink()
        external = self.root / "private-font.woff2"
        external.write_bytes(b"Private font")
        try:
            source.symlink_to(external)
        except (OSError, NotImplementedError):
            self.skipTest("File symlinks are unavailable on this system.")
        with self.assertRaisesRegex(builder.BuildError, "symlink or junction"):
            builder.build(self.root, self.root / "website" / "dist")

    def test_unindexed_paper_is_pruned_even_if_its_source_folder_still_exists(self):
        other = self.root / "papers" / "other"
        shutil.copytree(self.paper, other)
        other_row = "| [Other paper](papers/other/README.md) | arXiv | 2026 | Another topic | 3 |\n"
        (self.root / "README.md").write_text(ROOT_README.replace("<!-- PAPER_INDEX_END -->", other_row + "<!-- PAPER_INDEX_END -->"), encoding="utf-8")
        out = self.root / "website" / "dist"
        builder.build(self.root, out)
        original_row = "| [Approved paper](papers/approved/README.md) | arXiv | 2026 | Test research | 3 |\n"
        (self.root / "README.md").write_text((self.root / "README.md").read_text(encoding="utf-8").replace(original_row, ""), encoding="utf-8")
        catalog = builder.build(self.root, out)
        self.assertEqual([paper["id"] for paper in catalog["papers"]], ["other"])
        self.assertEqual(list((out / "assets/papers/approved").rglob("*.png")), [])
        self.assertEqual(len(list((out / "assets/papers/other").rglob("*.png"))), 3)
        self.assertTrue((self.paper / "README.md").is_file())

    def test_user_modified_stale_file_blocks_all_cleanup_and_output_publication(self):
        out = self.root / "website" / "dist"
        builder.build(self.root, out)
        stale = out / "assets/papers/approved/result_figures/result.png"
        other_stale = out / "assets/papers/approved/method_figures/method.png"
        original_manifest = (out / builder.GENERATED_MANIFEST).read_bytes()
        original_catalog = (out / "catalog.json").read_bytes()
        stale.write_bytes(b"User modified this file; preserve it.")
        self.remove_asset_type("method")
        self.remove_asset_type("result")
        with self.assertRaisesRegex(builder.BuildError, "modified and has been preserved"):
            builder.build(self.root, out)
        self.assertEqual(stale.read_bytes(), b"User modified this file; preserve it.")
        self.assertTrue(other_stale.is_file())
        self.assertEqual((out / builder.GENERATED_MANIFEST).read_bytes(), original_manifest)
        self.assertEqual((out / "catalog.json").read_bytes(), original_catalog)

    def test_first_build_does_not_guess_ownership_of_existing_image_files(self):
        out = self.root / "website" / "dist"
        old = out / "assets/papers/unindexed/result_figures/old.png"
        old.parent.mkdir(parents=True)
        old.write_bytes(b"No prior manifest means no deletion authority.")
        builder.build(self.root, out)
        self.assertTrue(old.is_file())
        manifest = json.loads((out / builder.GENERATED_MANIFEST).read_text(encoding="utf-8"))
        self.assertNotIn(old.relative_to(out).as_posix(), [record["path"] for record in manifest["files"]])

    def test_removed_explicit_guide_is_pruned_but_unknown_guide_is_kept(self):
        docs = self.root / "docs"
        docs.mkdir()
        source = docs / "GETTING_STARTED.md"
        source.write_text("Generated guide", encoding="utf-8")
        out = self.root / "website" / "dist"
        builder.build(self.root, out)
        unknown = out / "guides/PRIVATE.md"
        unknown.write_text("User-owned", encoding="utf-8")
        source.unlink()
        builder.build(self.root, out)
        self.assertFalse((out / "guides/GETTING_STARTED.md").exists())
        self.assertEqual(unknown.read_text(encoding="utf-8"), "User-owned")

    def test_manifest_traversal_and_unknown_namespaces_fail_without_deletion(self):
        out = self.root / "website" / "dist"
        builder.build(self.root, out)
        protected = self.root / "owned.png"
        protected.write_bytes(b"Protected")
        for relative in ("../owned.png", "assets/papers/approved/result_figures/../../../../owned.png", "private.txt", "guides/PRIVATE.md"):
            manifest = {"schema": builder.MANIFEST_SCHEMA, "version": 1, "files": [{"path": relative, "sha256": builder.sha256_file(protected)}]}
            (out / builder.GENERATED_MANIFEST).write_text(json.dumps(manifest), encoding="utf-8")
            with self.subTest(relative=relative), self.assertRaises(builder.BuildError):
                builder.build(self.root, out)
            self.assertEqual(protected.read_bytes(), b"Protected")

    def test_stale_symlink_cannot_remove_another_file_when_supported(self):
        out = self.root / "website" / "dist"
        builder.build(self.root, out)
        stale = out / "assets/papers/approved/result_figures/result.png"
        protected = out / "user-owned.png"
        protected.write_bytes(stale.read_bytes())
        stale.unlink()
        try:
            stale.symlink_to(protected)
        except (OSError, NotImplementedError):
            self.skipTest("File symlinks are unavailable on this system.")
        self.remove_asset_type("result")
        with self.assertRaisesRegex(builder.BuildError, "symlink or junction"):
            builder.build(self.root, out)
        self.assertTrue(protected.is_file())
        self.assertTrue(stale.is_symlink())

    def test_custom_branding_without_code_change(self):
        config = {"name": "My Figure Garden", "chineseName": "我的图圃", "tagline": "My recipes", "description": "My library", "repositoryUrl": "https://github.com/example/library", "featuredPaperIds": ["approved", "unindexed"]}
        (self.root / "website" / "figarium.config.json").write_text(json.dumps(config), encoding="utf-8")
        catalog, _ = builder.make_catalog(self.root)
        self.assertEqual(catalog["site"]["name"], "My Figure Garden")
        self.assertEqual(catalog["site"]["featuredPaperIds"], ["approved"])
        self.assertEqual(catalog["papers"][0]["readmeUrl"], "https://github.com/example/library/blob/main/papers/approved/README.md")

    def test_only_explicit_guides_are_copied_as_plain_markdown(self):
        docs = self.root / "docs"
        docs.mkdir()
        content = "# Setup\n```python\nraise RuntimeError('never execute')\n```\n<script>alert(1)</script>\n"
        for name in ("GETTING_STARTED.md", "CUSTOMIZATION.md", "PRIVATE.md", "secret.pdf"):
            (docs / name).write_text(content, encoding="utf-8")
        nested = docs / "nested"
        nested.mkdir()
        (nested / "GETTING_STARTED.md").write_text("Do not publish", encoding="utf-8")
        out = self.root / "website" / "dist"
        builder.build(self.root, out)
        self.assertEqual({path.name for path in (out / "guides").iterdir()}, {"GETTING_STARTED.md", "CUSTOMIZATION.md"})
        for name in ("GETTING_STARTED.md", "CUSTOMIZATION.md"):
            self.assertEqual((out / "guides" / name).read_text(encoding="utf-8"), content)
        self.assertFalse((out / "guides" / "GETTING_STARTED.html").exists())

    def test_external_ppt_source_is_included_only_when_linked(self):
        self.replace_paper("| PPT Source | Not available |", "| PPT Source | [Slides](https://example.com/source.pptx) |")
        catalog, copies = builder.make_catalog(self.root)
        download = catalog["assets"][0]["downloads"][-1]
        self.assertEqual(download["url"], "https://example.com/source.pptx")
        self.assertEqual(download["format"], "pptx")
        self.assertFalse(download["local"])
        self.assertIn("not been checked", download["validation"])
        self.assertEqual(catalog["stats"]["sourceCount"], 2)
        self.assertEqual(catalog["stats"]["pptxCount"], 0)
        self.assertEqual(len(copies), 3)

    def test_explicit_local_pptx_is_copied_as_a_download_not_an_image(self):
        source = self.link_pptx()
        self.make_pptx("unlinked.pptx")
        out = self.root / "website" / "dist"
        catalog = builder.build(self.root, out)
        asset = catalog["assets"][0]
        deck = asset["downloads"][-1]
        self.assertEqual(deck["url"], "assets/papers/approved/method_figures/method.pptx")
        self.assertEqual((deck["format"], deck["filename"], deck["local"]), ("pptx", "method.pptx", True))
        self.assertIn("does not verify", deck["validation"])
        self.assertEqual((out / deck["url"]).read_bytes(), source.read_bytes())
        self.assertFalse((out / "assets/papers/approved/method_figures/unlinked.pptx").exists())
        self.assertEqual(catalog["stats"]["assetCount"], 3)
        self.assertEqual(catalog["stats"]["sourceCount"], 3)
        self.assertEqual(catalog["stats"]["pptxCount"], 1)
        self.assertEqual(catalog["stats"]["counts"]["method"], 1)
        self.assertEqual(asset["codes"], [])
        self.assertNotIn(".pptx", builder.IMAGE_SUFFIXES)
        self.assertEqual(builder.generated_kind(deck["url"]), "presentation")

    def test_method_pptx_counts_as_source_without_exporting_legacy_diagram_code(self):
        self.link_pptx()
        self.replace_paper("### Color Palette", '### SVG Source\n```svg\n<svg xmlns="http://www.w3.org/2000/svg"/>\n```\n### Color Palette')
        catalog, _ = builder.make_catalog(self.root)
        self.assertEqual(catalog["stats"]["sourceCount"], 3)
        self.assertEqual(catalog["stats"]["pptxCount"], 1)
        self.assertEqual(catalog["assets"][0]["codes"], [])
        self.assertIn("<svg", (self.paper / "README.md").read_text(encoding="utf-8"))

    def test_combined_pptx_is_explicit_paper_download_not_implicit_asset_coverage(self):
        source = self.link_pptx("method_figures_editable.pptx", combined=True)
        out = self.root / "website" / "dist"
        catalog = builder.build(self.root, out)
        deck = catalog["papers"][0]["downloads"][0]
        self.assertIn("combined", deck["label"])
        self.assertTrue(deck["local"])
        self.assertEqual((out / deck["url"]).read_bytes(), source.read_bytes())
        self.assertEqual(catalog["stats"]["sourceCount"], 2)
        self.assertEqual(catalog["stats"]["pptxCount"], 0)
        self.assertFalse(builder.has_local_pptx(catalog["assets"][0]))

    def test_same_pptx_referenced_by_asset_and_paper_is_copied_once(self):
        self.link_pptx()
        self.replace_paper("| Authors | Ada Example |", "| Authors | Ada Example |\n| Method Figures PPT | [Combined editable deck](method_figures/method.pptx) |")
        catalog, copies = builder.make_catalog(self.root)
        self.assertEqual(sum(source.suffix == ".pptx" for source, _ in copies), 1)
        self.assertEqual(catalog["stats"]["pptxCount"], 1)

    def test_local_pptx_paths_are_restricted_to_method_directory(self):
        self.make_pptx()
        for target in ("../private.pptx", "%2e%2e/private.pptx", "result_figures/method.pptx", "method_figures/method.png", "C:/private/deck.pptx", "javascript:alert(1)", "method_figures/method.pptx?query=1"):
            with self.subTest(target=target), self.assertRaises(builder.BuildError):
                builder.pptx_downloads(f"[Deck]({target})", self.paper, "approved")
        self.assertIsNone(builder.generated_kind("assets/papers/approved/result_figures/method.pptx"))

    def test_missing_and_disguised_pptx_files_block_build(self):
        self.replace_paper("| PPT Source | Not available |", "| PPT Source | [Deck](method_figures/method.pptx) |")
        with self.assertRaisesRegex(builder.BuildError, "does not exist"):
            builder.make_catalog(self.root)
        (self.paper / "method_figures/method.pptx").write_bytes(b"This is not an OOXML package.")
        with self.assertRaisesRegex(builder.BuildError, "invalid PPTX package"):
            builder.make_catalog(self.root)

    def test_ppt_source_cannot_attach_a_method_deck_to_a_result_asset(self):
        self.make_pptx()
        self.replace_paper("### Plotting Code", "| PPT Source | [Deck](method_figures/method.pptx) |\n### Plotting Code")
        with self.assertRaisesRegex(builder.BuildError, "belongs to a method figure"):
            builder.make_catalog(self.root)

    def test_unlinked_local_pptx_is_cleaned_from_export_not_canonical_folder(self):
        source = self.link_pptx()
        out = self.root / "website" / "dist"
        builder.build(self.root, out)
        exported = out / "assets/papers/approved/method_figures/method.pptx"
        unknown = exported.parent / "user-owned.pptx"
        unknown.write_bytes(b"Unknown output is preserved.")
        self.replace_paper("| PPT Source | [Deck](method_figures/method.pptx) |", "| PPT Source | Not available |")
        catalog = builder.build(self.root, out)
        self.assertFalse(exported.exists())
        self.assertTrue(source.is_file())
        self.assertTrue(unknown.is_file())
        self.assertEqual(catalog["stats"]["pptxCount"], 0)

    def test_user_modified_stale_pptx_is_preserved_and_blocks_publication(self):
        self.link_pptx()
        out = self.root / "website" / "dist"
        builder.build(self.root, out)
        exported = out / "assets/papers/approved/method_figures/method.pptx"
        exported.write_bytes(exported.read_bytes() + b"User modification")
        original = exported.read_bytes()
        self.replace_paper("| PPT Source | [Deck](method_figures/method.pptx) |", "| PPT Source | Not available |")
        with self.assertRaisesRegex(builder.BuildError, "modified and has been preserved"):
            builder.build(self.root, out)
        self.assertEqual(exported.read_bytes(), original)

    def test_removed_combined_pptx_is_pruned(self):
        self.link_pptx("method_figures_editable.pptx", combined=True)
        out = self.root / "website" / "dist"
        builder.build(self.root, out)
        self.replace_paper("| Method Figures PPT | [Combined editable deck](method_figures/method_figures_editable.pptx) |\n", "")
        builder.build(self.root, out)
        self.assertFalse((out / "assets/papers/approved/method_figures/method_figures_editable.pptx").exists())

    def test_pptx_source_symlink_is_rejected_when_supported(self):
        source = self.make_pptx()
        alias = source.parent / "alias.pptx"
        try:
            alias.symlink_to(source)
        except (OSError, NotImplementedError):
            self.skipTest("File symlinks are unavailable on this system.")
        with self.assertRaisesRegex(builder.BuildError, "symlink or junction"):
            builder.pptx_downloads("[Deck](method_figures/alias.pptx)", self.paper, "approved")

    def test_legacy_method_code_is_not_published_or_counted_as_a_ppt_resource(self):
        self.replace_paper("### Color Palette", '''### SVG Source
```svg
<svg xmlns="http://www.w3.org/2000/svg"><text>Recipe</text></svg>
```
### TikZ Source
```tikz
\\begin{tikzpicture}\\node {Recipe};\\end{tikzpicture}
```
### Color Palette''')
        catalog, _ = builder.make_catalog(self.root)
        self.assertEqual(catalog["assets"][0]["codes"], [])
        self.assertEqual(catalog["stats"]["sourceCount"], 2)
        self.assertIn("<svg", (self.paper / "README.md").read_text(encoding="utf-8"))
        self.assertEqual(catalog["assets"][1]["codes"][0]["language"], "python")
        self.assertEqual(catalog["assets"][2]["codes"][0]["language"], "latex")
        self.assertNotIn("<svg", builder.javascript_payload(catalog))

    def test_duplicate_index_entry_is_rejected(self):
        row = "| [Approved paper](papers/approved/README.md) | arXiv | 2026 | Test research | 3 |"
        (self.root / "README.md").write_text(ROOT_README.replace(row, row + "\n" + row), encoding="utf-8")
        with self.assertRaisesRegex(builder.BuildError, "Duplicate Paper Index"):
            builder.make_catalog(self.root)

    def test_unknown_authors_and_license_do_not_inherit_repository_mit(self):
        self.replace_paper("| Authors | Ada Example |\n", "")
        self.replace_paper("| Original Asset License | Rights reserved; permission not documented |\n", "")
        catalog, _ = builder.make_catalog(self.root)
        self.assertEqual(catalog["papers"][0]["license"], builder.NOT_DOCUMENTED)
        self.assertEqual(catalog["papers"][0]["authors"], builder.NOT_DOCUMENTED)

    def test_symlink_escape_is_rejected_when_supported(self):
        external = self.root / "outside.png"
        external.write_bytes(b"private")
        link = self.paper / "method_figures" / "link.png"
        try:
            link.symlink_to(external)
        except (OSError, NotImplementedError):
            self.skipTest("File symlinks are unavailable on this system.")
        with self.assertRaises(builder.BuildError):
            builder.local_reference(self.paper, "method_figures/link.png", self.paper)


class RealCollectionTests(unittest.TestCase):
    def test_canonical_collection_consistency_without_hardcoded_catalog_counts(self):
        root = BUILDER.parent.parent
        if not (root / "papers" / "DDA" / "README.md").is_file():
            self.skipTest("Real collection is not available in this checkout.")
        entries = builder.approved_papers(root)
        catalog, copies = builder.make_catalog(root)
        self.assertEqual(catalog["stats"]["paperCount"], len(entries))
        image_copies = [(source, destination) for source, destination in copies if builder.generated_kind(destination) == "image"]
        self.assertEqual(catalog["stats"]["assetCount"], len(image_copies))
        self.assertEqual(sum(catalog["stats"]["counts"].values()), len(catalog["assets"]))
        self.assertEqual(catalog["stats"]["sourceCount"], sum(builder.has_source(asset) for asset in catalog["assets"]))
        self.assertEqual(catalog["stats"]["pptxCount"], sum(builder.has_local_pptx(asset) for asset in catalog["assets"]))
        self.assertEqual({paper["id"] for paper in catalog["papers"]}, {entry["id"] for entry in entries})
        self.assertFalse(any("新建文件夹" in asset["src"] for asset in catalog["assets"]))
        self.assertTrue(all(source.is_file() for source, _ in copies))
        # Compare approved README asset headings, not the duplicated preview grid.
        figure_headings = 0
        for entry in entries:
            text = entry["path"].read_text(encoding="utf-8-sig")
            figure_headings += sum(level == 2 and title.startswith(("Figure ", "Table ")) for _, _, level, title in builder.headings(text))
        self.assertEqual(len(catalog["assets"]), figure_headings)


if __name__ == "__main__":
    unittest.main()
