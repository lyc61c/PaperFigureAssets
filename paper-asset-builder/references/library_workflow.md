# Personal Figarium Library Workflow

Read this reference when helping a new user install the skill, create a personal paper-figure library, or connect existing entries to the static gallery. Routine single-paper updates can follow `SKILL.md` directly.

## Product boundaries

Figarium · 图圃 (Figure + Herbarium) has three separate layers:

- The local agent uses `paper-asset-builder` to inspect PDFs, extract/classify assets, pause for human review, and reconstruct editable examples.
- `papers/<paper_id>/README.md` and its approved images are the canonical library. Python, SVG/TikZ, and table LaTeX live in README blocks; reconstruction notes and original provenance travel with the asset.
- `website/build.py`, when present, generates a static browsing/export surface. It does not run the agent, execute copied Python, or accept arbitrary online compilation jobs.

Customization means each user owns the paper selection, final local images, branding, and site, rather than merely viewing someone else's gallery. Reproducibility means explicit source/data assumptions and editable examples; it is not a promise that every figure can be recovered exactly.

## Setup guidance

Use the repository's `docs/GETTING_STARTED.md` and `docs/CUSTOMIZATION.md` when available. Forking and remote changes must follow the user's explicit intent; do not create a GitHub fork, rename a remote, publish a site, or push just because setup was requested.

For Codex, current official local discovery locations include repository `.agents/skills/` and user `~/.agents/skills/`. Copy the complete `paper-asset-builder/` directory, not only `SKILL.md`, into one appropriate scope. See [official skills documentation](https://developers.openai.com/codex/skills) for current host behavior. If this user already has a working install in a host-specific legacy directory, update that installation in place rather than creating duplicate same-name installations. Do not hard-code another user's home directory.

For Claude Code, use project `.claude/skills/paper-asset-builder/` or user `~/.claude/skills/paper-asset-builder/`. Keep the invocation name compatible: Codex `$paper-asset-builder`/natural language, Claude Code `/paper-asset-builder`.

Explain dependencies by stage rather than making users install a large global environment blindly: the page/crop helper uses PyMuPDF; chart examples commonly use NumPy/Matplotlib; the static builder uses its documented Python requirements; local LaTeX is optional if authorized online testing is chosen. Prefer an existing compatible environment or a project-local virtual environment. Do not make normal users run extraction scripts to invoke the skill.

## First paper

An example user prompt is:

```text
$paper-asset-builder paper="Exact paper title or URL" repo_root="/path/to/my-library" selection=all
```

Resolve metadata and an accessible PDF. Inventory all numbered figures/tables including appendices, extract verified regions into at most the three optional type folders, and maintain coverage/provenance. Report the absolute local path and stop. Do not immediately convert every extracted asset into a published library entry.

The human may delete, replace, reclassify, rename, or add images. On `检查好了，继续`, rescan the current directory and use it as truth. Never rerun extraction to restore deleted files. Reconstruct only the retained assets, generate the canonical paper README, update the root index, and rebuild the available local static website. Rebuilding does not authorize external publishing.

## Ongoing library maintenance

- Reuse existing paper IDs for the same paper and preserve unrelated user edits.
- Treat a change of paper PDF version as provenance-sensitive; record it and request review for changed/re-extracted assets.
- Prefer explicit, reproducible corrections over silently rewriting old data or claiming an approximate curve is exact.
- Existing code coverage is asset-specific. Preserve old entries and report where editable method code is not yet available instead of promising a migration that has not occurred.
- Updating extracted images requires a new image review checkpoint; text-only metadata fixes do not automatically require re-extracting the PDF.
- For already published entries, identify stale generated files before removing them. Synchronize only files known to belong to this entry and covered by the requested update; never delete unrelated user material.

## Privacy and publication

Online LaTeX testing needs scoped consent for the selected service and minimal table source upload, as described in `latex_render_testing.md`. Do not carry consent from one private paper to every future upload.

Local extraction does not grant redistribution rights. Before public publication, check figure/table licenses or permission and keep source/license notes with each entry. A paper's public availability or arXiv distribution permission is not blanket reuse permission. Reconstruction code does not imply rights to embedded third-party art or exact scientific raw data.

Keep full PDFs, material manifests with private absolute paths, credentials, temporary QA files, and hosting identity files out of public exports unless separately intended and authorized. Check the actual build output before deployment. Use the user's own repository URL/hosting identity for a fork rather than inheriting an unrelated deployment project ID.
