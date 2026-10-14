# Method Figure Reconstruction Reference

Use this reference when processing images in:

```text
method_figures/
```

## Goal

For each method figure image, generate a README-ready block containing:

1. figure title;
2. centered image preview;
3. asset table;
4. PPT source link if a same-basename `.pptx` exists;
5. extracted or estimated color palette table;
6. self-contained editable SVG or TikZ reconstruction where feasible, with an honest scope/fidelity note.

Current scope:

```text
method figure image -> semantic palette + editable diagram reconstruction
```

Keep supplied same-basename PPT sources, but do not label reconstructed SVG/TikZ as the authors' original source. Automatic PPT reconstruction is not required. Existing palette-only library entries remain valid legacy entries; this capability does not mean every existing diagram already has editable code.

---

## Output Block Format

Use this block format inside the paper README:

```markdown
## Figure {index}: {figure_title}

<p align="center">
  <img src="method_figures/{image_filename}" alt="{figure_title}" width="760">
</p>

| Asset | Link |
|---|---|
| Preview Image | [{image_filename}](method_figures/{image_filename}) |
| PPT Source | [{pptx_filename}](method_figures/{pptx_filename}) |

### Color Palette

| Role | Swatch | Color | Hex |
|---|---|---|---|
| Input / context | ![#6B7280](https://placehold.co/20x20/6B7280/6B7280.svg) | Gray | `#6B7280` |
| Vision encoder | ![#2563EB](https://placehold.co/20x20/2563EB/2563EB.svg) | Blue | `#2563EB` |
| Projector / adapter | ![#16A34A](https://placehold.co/20x20/16A34A/16A34A.svg) | Green | `#16A34A` |
| LLM / reasoning | ![#F97316](https://placehold.co/20x20/F97316/F97316.svg) | Orange | `#F97316` |
| Supervision signal | ![#DC2626](https://placehold.co/20x20/DC2626/DC2626.svg) | Red | `#DC2626` |
```

After the palette, add `### Editable Reconstruction` without changing the canonical paper template itself. Introduce the block with a scope note such as:

> Reconstructed schematic (not author-provided source). Preserves the module hierarchy, labels, and connections; illustrations are simplified.

Use a fenced `svg` block containing a complete `<svg xmlns="http://www.w3.org/2000/svg" ...>` document, or a fenced `latex` block containing a complete standalone TikZ document with its packages/libraries. Prefer SVG for portable, directly editable scientific diagrams. Distinguish a TikZ block from table `### LaTeX Source` blocks so table testing does not process it as a table.

## Editable Diagram Procedure

1. Inspect all panels, modules, arrows, grouping containers, legends, labels, and equations; derive a small scene graph before drawing.
2. Recreate the meaningful layout and semantics, not an unrelated generic flowchart. Use named groups/classes or TikZ styles and a small palette so users can change colors/text/spacing easily.
3. Embed all required vector shapes and text in the code. Do not depend on private file paths, remote images, raster screenshots, or external fonts to pretend the diagram is self-contained. SVG must not contain scripts, event handlers, `foreignObject`, or network-loaded resources.
4. Preserve readable module names, arrow direction, panel ordering, and key mathematical notation. Keep a sensible viewBox/canvas size and avoid clipped text or overlapping connectors.
5. Render the actual code locally with an available SVG renderer/browser or TeX compiler, inspect it against the approved figure, and repair meaningful structural defects. Keep QA outputs outside `papers/`; report if rendering could not be verified.
6. State fidelity honestly: full vector diagram reconstruction, simplified schematic, or unsupported original imagery. If photos, screenshots, complex artwork, tiny unreadable details, or licensing constraints prevent faithful reconstruction, preserve the preview/palette and explain exactly which elements cannot be supplied as editable code. Do not promise pixel-identical or author-source recovery.

The result should be useful as an editable starting point without disguising estimated artwork as original research evidence. Reconstruction does not transfer rights to an author's original illustration.

If no matching PPT file exists, use:

```markdown
| PPT Source | Not available |
```

---

## Palette Extraction Procedure

For each method figure:

1. inspect the image visually;
2. identify representative non-background colors;
3. prefer colors used by major modules, arrows, highlights, and supervision signals;
4. avoid near-white background colors unless visually meaningful;
5. avoid near-duplicate colors;
6. use uppercase HEX values;
7. assign colors to semantic roles when possible.

---

## Default Palette Roles

Use these roles by default:

```text
Input / context
Vision encoder
Projector / adapter
LLM / reasoning
Supervision signal
```

If the figure clearly uses more specific semantics, use better role names while keeping the same table format.

Examples:

```text
Feature tokens
Fusion block
Reasoning block
Loss head
Frozen branch
```

---

## Swatch Format

Use this exact Markdown image format:

```markdown
![#HEX](https://placehold.co/20x20/HEX_NO_HASH/HEX_NO_HASH.svg)
```

Example:

```markdown
![#2563EB](https://placehold.co/20x20/2563EB/2563EB.svg)
```

---

## Color Name Rule

Use coarse color names:

```text
Gray
Blue
Green
Orange
Red
Purple
Yellow
Cyan
Black
White
Brown
Pink
Teal
Indigo
```

Choose the nearest simple color family when uncertain.

---

## Output

Write the palette directly into the paper README under `### Color Palette`, followed by `### Editable Reconstruction` containing the labeled code or a concrete reconstruction limitation. Keep source provenance and PPT availability distinct from reconstructed code.
