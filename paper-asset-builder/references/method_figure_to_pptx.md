# Method Figure → Editable PowerPoint

This is the bundled PPT reconstruction subworkflow of `paper-asset-builder`. No second third-party skill installation is required. Execute it for **every approved Method Figure** unless the user explicitly sets `method_pptx=off`. Never run it while extracted images are awaiting human selection. On resume, rescan current images and their hashes; removed or replaced figures are not restored from the PDF.

## Contract: full visual content, honest editability

The target is a faithful reconstruction of the entire approved figure, not a redesigned explanation, simplified flowchart, or generic presentation. Preserve aspect ratio, layout, all panels, text, mathematical symbols, modules, grouping, arrows, legends, color, line styles, layering, and illustrative content. Do not add a title/footer/cover absent from the figure.

Use native editable PowerPoint text for readable labels and native shapes/freeform paths/lines for vector diagram elements. Prefer native connectors where endpoint semantics can be recovered. A native freeform arrow is editable geometry but is **not** a bound connector; disclose that distinction. Charts recovered as paths are not data-bound charts. Equations may be native text/runs, editable equation objects when supported, or clearly declared editable vector outlines when font recovery is impossible.

Photos, screenshots, and genuinely complex raster illustrations may remain **independent local cropped image objects** with correct footprint and transparency. They must be separately movable/resizable; their internal pixels are not editable. Do not redraw scientific example images with generative AI or invent hidden text. Do not use a full-slide screenshot, whole-figure SVG, giant raster fragment, transparent native overlay, or a tiled full-image mosaic to simulate editability. Native object counts alone do not prove useful editability.

“Complete visual reconstruction” and “all pixels are native objects” are different claims. Report the former only after visual verification, and report the actual native/raster boundary. Never promise pixel-identical rendering across Office versions or recovered author source.

## Authoring and source inventory

1. Read the host's presentation skill, if available, and follow its required authoring backend, markers, finalization, and output rules. In the Codex bundled presentation environment use its JavaScript artifact runtime; do not substitute an obsolete API. If no host backend exists, use an available native-PPTX authoring library permitted by that host and name it in the QA receipt. Missing tooling is a reported limitation, not permission to embed the whole PNG.
2. Create an isolated build/QA directory outside `papers/`. Record source SHA-256, dimensions, paper URL, and any matching PDF page/crop. Inspect the source at full resolution. Inventory every panel, text span, module, edge, local illustration, and clipping/layer dependency. Mark unreadable labels as unresolved instead of guessing.
3. Prefer original PDF text and vector geometry when they match the approved image. Verify page/crop registration visually; a title or caption match alone is insufficient. Do not replace user-edited pixels with a different PDF version. Extract local raster assets without external uploads. If only a PNG exists, manually or locally-assisted reconstruct its structure; OCR is a draft to be checked against the image, not ground truth.
4. Use a canvas proportional to the source. Preserve exact positions, sizes, colors, stroke widths, dashes, arrowheads, rounded corners, and z-order. Group semantically useful elements where supported. Name objects meaningfully. Recover readable text as text rather than hundreds of letter outlines when possible. Inspect installed fonts and disclose substitutions; do not claim a reference font merely because it has a similar name.
5. Save the authoring source/scene and component inventory in the private job directory so changes are repeatable. Keep this source separate from supplemental README SVG/TikZ code. No network-loaded image/font, macro, OLE payload, script, active content, or external media dependency belongs in the delivered PPTX. Ordinary citation hyperlinks are allowed.

PDF recovery is not automatically faithful. A font's ToUnicode can return a **valid but wrong** character (for example a Greek variable or operator); verify every equation visually, not merely the absence of replacement characters. Recover unsupported mathematical glyphs as source-matched native vector outlines when necessary and disclose that they are not typeable equation text. Image xref/occurrence reuse can recover the wrong logo or photo; check the actual pixels against the approved crop. Preserve clipping paths, soft masks, inherited group opacity, rotated-text baselines, dash geometry, and nested fill winding. Large raster panel shadows should be rebuilt as native effects, not used as screenshot-like backgrounds. These are visual acceptance checks, not assumptions justified by a successful PDF parser.

## Two independent acceptance gates

### A. Native-object/package gate

Inspect **the exported final PPTX ZIP/OOXML**, not just the authoring source. Verify slide count, source aspect/layout, required editable text, native vector objects, connectors where required, independently positioned raster exceptions, no full-background disguise, no macros/OLE/external media, and no missing package relationships. Use the host finalizer/integrity/layout checks too when available.

The bundled stdlib helper is an additional safety and inventory check:

```text
python <skill>/scripts/method_pptx_qa.py inspect --pptx <final.pptx> --inventory <inventory.json> --report <qa.json>
```

Suggested inventory (one item per slide):

```json
{
  "schema_version": 1,
  "slides": [{
    "slide": 1,
    "required_text": ["Encoder", "Decoder"],
    "required_native_objects": {"shapes": 4, "text_shapes": 2, "connectors": 1},
    "important_objects": [{"label": "Encoder", "kind": "text_shape", "text": "Encoder"}],
    "allowed_images": []
  }]
}
```

Counts are minima and text checks normalize whitespace. They cannot certify semantic grouping, arrow binding, complete coverage, or visual fidelity. Add source component positions and raster-exception explanations to the private inventory/receipt; manually verify them. Package validation without an inventory proves only a readable/safe package, not native editability or fidelity. The website builder performs package validation, **not** scientific reconstruction acceptance.

### B. Actual-final-file visual gate

Render the **delivered PPTX itself**, after finalization, with an available local renderer. Prefer actual PowerPoint/LibreOffice when available. A roundtrip import of the exported PPTX into the host presentation renderer is acceptable evidence if clearly identified; do not call it a PowerPoint application test. Rendering the source scene, a temporary SVG, or a prior candidate is not enough.

Compare every final slide to its approved PNG at the same aspect ratio and inspect at full resolution: all panel boundaries, labels (including tiny annotations), equations, arrow directions, dashed/curved paths, icons/photos, overlaps, clipping, and image transparency. Use side-by-side, overlay, and difference images:

```text
python <skill>/scripts/method_pptx_qa.py compare --reference <approved.png> --rendered <final-slide.png> --out-dir <qa-dir>
```

Pixel metrics are diagnostics only: white backgrounds can make a poor reconstruction score well. Do not locally warp or crop away differences to manufacture a match. Record a component-by-component visual review, repair defects, re-export, and rerender affected final files. Bind the acceptance receipt to both reference and final PPTX SHA-256; edits invalidate the receipt. If rendering/fonts/clipping cannot be verified, keep the artifact **unverified/incomplete**, preserve work, and explain the remaining issue. Do not publish it as a completed full reconstruction.

## Delivery and integration

- Individual deck: `method_figures/<image-stem>.pptx`, one slide, no extra cover. Each slide retains the image's aspect ratio.
- Per-paper deck: `method_figures/method_figures_editable.pptx`, one slide per selected Method Figure, natural figure order. Use a common canvas with uniform scaling and letterboxing for differing ratios; never stretch. Validate this deck's package **and each actual final slide** too.
- If any selected figure is incomplete, the paper deck is not an all-selected completed deliverable. Either repair it or explicitly name/label the combined deck as partial and enumerate omitted or unverified slides; never silently present a verified subset as the complete paper.
- Before publishing, check target collisions. Preserve user/author PPTs. Use versioned private candidates and an explicitly safe final name when existing files cannot be replaced. The asset `PPT Source` row links the actual chosen file; the combined metadata row uses exactly `Method Figures PPT`.
- README scope note: “Reconstructed editable PPTX, not author-provided source. Text and vector geometry are native PowerPoint objects; [specific photos/screenshots] remain independent raster images. [Renderer] final-file visual QA [status]; PowerPoint application compatibility [tested/not tested].” State any font substitution/unbound arrows/vectorized text explicitly.
- Keep palette and existing SVG/TikZ scope notes. Supplemental simplified code is not upgraded to “full” merely because a PPT exists. The canonical template and root image counts do not change.
- Publish only selected images, validated PPTX files, README links, and requested source. Keep source PDFs, authoring dependencies, extracted embedded fonts, QA screenshots, private manifests, and credentials out of Git unless separately authorized. Existing license/attribution obligations still apply; reconstruction does not transfer rights.
- The gallery copies explicitly linked safe local PPTX files and offers direct downloads. It does not execute authoring code. Running this subworkflow is not authorization to commit, push, or deploy; obtain that authority from the user.
- Report selected/completed/skipped/incomplete figure counts, individual and combined deck paths, native/raster boundaries, renderer evidence, and any application-compatibility limits. Do not silently downgrade a batch to one example.

## Research provenance

This workflow was independently authored after consulting the native-object/hybrid reconstruction approach in [paper-figure-pptx-skill](https://github.com/fengting124/paper-figure-pptx-skill). Other approaches, such as [img2pptx](https://github.com/Lancelot-Xie/img2pptx), embed a whole SVG and require later Office “Convert to Shape”; that is **not** the default native-editable delivery promised here. No third-party skill code, hard-coded environment, external OCR/upload policy, or automatic fidelity claim is imported by this reference.
