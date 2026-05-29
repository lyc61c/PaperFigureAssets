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
5. extracted or estimated color palette table.

Current scope:

```text
method figure image -> color palette table
```

PPT reconstruction is not included in this version.

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

Write the palette directly into the paper README under `### Color Palette`.