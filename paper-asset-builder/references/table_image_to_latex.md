# Table Image to LaTeX Reconstruction Reference

You are an expert LaTeX table reconstruction engineer. You are highly proficient in recreating scientific paper tables from images using LaTeX.

I have a table image extracted from a research paper, but I do not have the corresponding LaTeX source code. Your task is to generate LaTeX code that reproduces the table image as faithfully as possible.

For this skill, the generated LaTeX should be inserted directly into the paper-level `README.md` under:

```markdown
### LaTeX Source
```

The goal is not merely to extract the table content, but to recreate the full visual appearance of the table, including its structure, data, typography, colors, rules, spacing, alignment, and layout.

---

## 1. Content Extraction

Carefully extract all visible:

- text;
- numbers;
- symbols;
- mathematical expressions;
- citations;
- arrows;
- checkmarks;
- crosses;
- percentages;
- bold values;
- underlined values;
- special markers.

If some small text is unclear, infer the closest visually consistent text based on the surrounding context.

If content cannot be confidently recovered, add this sentence before the LaTeX block:

```markdown
Note: The following LaTeX code is a structural reconstruction and should be verified against the original table.
```

---

## 2. Table Structure Reconstruction

Reconstruct the table structure as accurately as possible, including:

- number of rows and columns;
- header hierarchy;
- row groups and column groups;
- multirow and multicolumn cells;
- merged headers;
- empty cells;
- separator rows;
- category labels;
- method or model names;
- metric names;
- dataset names;
- grouped evaluation settings.

Use appropriate LaTeX constructs when necessary:

```latex
\multicolumn
\multirow
\makecell
p{}
m{}
>{\centering\arraybackslash}
\cline
\cmidrule
```

Do not flatten complex table structures into plain rows and columns when the image contains clear grouping or merged headers.

---

## 3. Visual Style Reproduction

Generate LaTeX code that matches the visual style of the table as closely as possible, including:

- table width and aspect ratio;
- column widths;
- row heights;
- cell padding;
- text alignment;
- font size;
- bold, italic, underline, superscript, subscript, and math formatting;
- horizontal rules and vertical rules;
- rule thickness;
- double rules or partial rules;
- booktabs-style lines such as `\toprule`, `\midrule`, and `\bottomrule`;
- `\cline` or `\cmidrule` ranges;
- background colors for header rows, highlighted rows, or highlighted cells;
- text colors;
- symbols such as `\checkmark`, `\times`, `\uparrow`, `\downarrow`, `\dagger`, and stars;
- caption and table notes, if visible.

Prioritize visual similarity to the provided image.

---

## 4. LaTeX Code Requirements

Generate a table environment suitable for insertion into a research paper.

Use this structure by default:

```latex
\begin{table}[t]
\centering
\caption{...}
\label{tab:...}
\begin{tabular}{...}
\toprule
...
\midrule
...
\bottomrule
\end{tabular}
\end{table}
```

Use `adjustbox`, `resizebox`, or carefully controlled column widths if necessary to match the reference image size and layout.

Include only the LaTeX packages that are necessary for the final generated code.

Common packages include:

```latex
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{xcolor}
\usepackage{graphicx}
\usepackage{array}
\usepackage{makecell}
\usepackage{siunitx}
\usepackage{pifont}
\usepackage{ulem}
\usepackage{adjustbox}
```

---

## 5. README Output Format

Use this block format inside the paper README:

````markdown
## Table {index}: {table_title}

<p align="center">
  <img src="tables/{image_filename}" alt="{table_title}" width="720">
</p>

| Asset | Link |
|---|---|
| Preview Image | [{image_filename}](tables/{image_filename}) |

### LaTeX Source

```latex
...
```

### Required Packages

```latex
\usepackage{booktabs}
```
````

---

## 6. Paper Asset Builder Integration

When used by `paper-asset-builder`, infer `{table_title}` from both the image content and filename. Prefer concise scientific table names such as `Main Results`, `Benchmark Comparison`, `Ablation Results`, `Dataset Statistics`, or a more specific title visible in the table.

Write only the README block content. Do not create separate `.tex` files unless the user explicitly asks for them.
