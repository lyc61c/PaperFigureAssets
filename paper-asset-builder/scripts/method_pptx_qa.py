#!/usr/bin/env python3
"""Read-only PPTX structure/editability QA and optional image comparison.

No Office process, author code, network request, or ZIP extraction is performed.
Package validation is intentionally not a complete ISO OOXML schema validator.
It does not prove fidelity, readability, or visual acceptance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import posixpath
import re
import sys
import unicodedata
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
import zipfile


NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
MAX_PACKAGE_BYTES = 120 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 200 * 1024 * 1024
MAX_ENTRY_BYTES = 32 * 1024 * 1024
MAX_ENTRIES = 2500
MAX_IMAGE_PIXELS = 25_000_000
MAX_SLIDE_OBJECTS = 10000
MAX_SLIDE_IMAGES = 1000


class PptxQAError(ValueError):
    """Unsafe, malformed, unsupported, or excessively large QA input."""


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _xml(data: bytes, part: str) -> ET.Element:
    try:
        text = data.decode("utf-16" if data.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig")
    except UnicodeDecodeError as exc:
        raise PptxQAError(f"Unsupported XML encoding in {part}") from exc
    if "\x00" in text or re.search(r"<!\s*(?:DOCTYPE|ENTITY)\b", text, re.I):
        raise PptxQAError(f"DTD/entities are not accepted: {part}")
    try:
        return ET.fromstring(data)
    except ET.ParseError as exc:
        raise PptxQAError(f"Malformed XML in {part}: {exc}") from exc


def _safe_name(name: str) -> None:
    decoded = unquote(name)
    if (not name or "\\" in decoded or "\x00" in decoded
            or decoded.startswith("/") or re.match(r"^[A-Za-z]:", decoded)
            or any(part in {".", ".."} for part in decoded.split("/"))):
        raise PptxQAError(f"Unsafe ZIP part name: {name!r}")


def _relationship_source(rel_part: str) -> str:
    if rel_part == "_rels/.rels":
        return ""
    path = PurePosixPath(rel_part)
    if path.parent.name != "_rels" or not path.name.endswith(".rels"):
        raise PptxQAError(f"Invalid relationship part name: {rel_part}")
    return str(path.parent.parent / path.name[:-5])


def _resolve_target(source: str, target: str) -> str:
    target = unquote(target)
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or "\\" in target or "\x00" in target:
        raise PptxQAError(f"Invalid internal relationship target: {target!r}")
    if parsed.query:
        raise PptxQAError(f"Queries are not valid internal part targets: {target!r}")
    joined = (parsed.path.lstrip("/") if parsed.path.startswith("/") else
              posixpath.join(posixpath.dirname(source), parsed.path or posixpath.basename(source)))
    normalized = posixpath.normpath(joined)
    if normalized in {"", ".", ".."} or normalized.startswith("../"):
        raise PptxQAError(f"Relationship escapes package: {target!r}")
    _safe_name(normalized)
    return normalized


def _warning(code: str, slide: int, detail: str) -> dict:
    return {"code": code, "slide": slide, "detail": detail}


def _shape_text(shape: ET.Element) -> str:
    return "\n".join("".join(t.text or "" for t in paragraph.findall(".//a:t", NS))
                     for paragraph in shape.findall(".//a:p", NS)).strip()


def _integer_pair(element: ET.Element | None, names: tuple[str, str], default: tuple[int, int]) -> tuple[int, int]:
    if element is None:
        return default
    try:
        return tuple(int(element.attrib.get(name, str(value))) for name, value in zip(names, default))
    except ValueError as exc:
        raise PptxQAError("Non-integer shape transform") from exc


def _object_bounds(node: ET.Element, transform: tuple[float, float, float, float]) -> dict | None:
    xfrm = node.find("p:spPr/a:xfrm", NS)
    if xfrm is None:
        xfrm = node.find("p:xfrm", NS)
    if xfrm is None:
        return None
    x, y = _integer_pair(xfrm.find("a:off", NS), ("x", "y"), (0, 0))
    width, height = _integer_pair(xfrm.find("a:ext", NS), ("cx", "cy"), (0, 0))
    if width < 0 or height < 0:
        raise PptxQAError("Negative shape extent")
    sx, sy, ox, oy = transform
    return {"x": sx*x+ox, "y": sy*y+oy, "width": sx*width, "height": sy*height}


def _group_transform(node: ET.Element, transform: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    xfrm = node.find("p:grpSpPr/a:xfrm", NS)
    if xfrm is None:
        return transform
    x, y = _integer_pair(xfrm.find("a:off", NS), ("x", "y"), (0, 0))
    width, height = _integer_pair(xfrm.find("a:ext", NS), ("cx", "cy"), (0, 0))
    child_x, child_y = _integer_pair(xfrm.find("a:chOff", NS), ("x", "y"), (0, 0))
    child_width, child_height = _integer_pair(xfrm.find("a:chExt", NS), ("cx", "cy"), (0, 0))
    if width < 0 or height < 0:
        raise PptxQAError("Negative group extent")
    if child_width <= 0 or child_height <= 0:
        return transform
    sx, sy, ox, oy = transform
    local_sx, local_sy = width/child_width, height/child_height
    return sx*local_sx, sy*local_sy, ox+sx*(x-child_x*local_sx), oy+sy*(y-child_y*local_sy)


def _invisible_paint(parent: ET.Element | None) -> bool:
    """Only flag explicit no-fill/zero alpha; missing theme styles are unknown."""
    if parent is None:
        return False
    if parent.find("a:noFill", NS) is not None:
        return True
    fill = next((child for child in parent if _local(child.tag) in {"solidFill", "gradFill", "pattFill"}), None)
    if fill is None:
        return False
    colors = [node for node in fill.iter() if _local(node.tag) in {"srgbClr", "schemeClr", "prstClr", "sysClr", "scrgbClr"}]
    return bool(colors) and all(any(_local(effect.tag) in {"alpha", "alphaMod"} and effect.attrib.get("val") == "0" for effect in color) for color in colors)


def _text_explicitly_invisible(shape: ET.Element) -> bool:
    runs = [node for node in shape.iter() if _local(node.tag) in {"r", "fld"} and node.find("a:t", NS) is not None]
    return bool(runs) and all(_invisible_paint(run.find("a:rPr", NS)) for run in runs)


def _rectangle_union_area(rectangles: list[tuple[float, float, float, float]]) -> float:
    # Bounded to at most MAX_SLIDE_OBJECTS rectangles. No pixel rasterization.
    edges = sorted({x for x0, unused_y0, x1, unused_y1 in rectangles for x in (x0, x1)})
    area = 0.0
    for left, right in zip(edges, edges[1:]):
        intervals = sorted((y0, y1) for x0, y0, x1, y1 in rectangles if x0 < right and x1 > left)
        if not intervals:
            continue
        covered, start, end = 0.0, intervals[0][0], intervals[0][1]
        for next_start, next_end in intervals[1:]:
            if next_start > end:
                covered += end-start
                start, end = next_start, next_end
            else:
                end = max(end, next_end)
        area += (right-left)*(covered+end-start)
    return area


def _slide_report(root: ET.Element, number: int, part: str, relationships: dict,
                  canvas: dict, content_types: dict) -> dict:
    counts = {"shapes": 0, "text_shapes": 0, "connectors": 0, "images": 0,
              "groups": 0, "graphic_frames": 0}
    objects, warnings = [], []
    all_ids = [node.attrib.get("id", "") for node in root.findall(".//p:cNvPr", NS)]
    if len(all_ids) != len(set(all_ids)) or any(not item.isdigit() or int(item) <= 0 for item in all_ids):
        raise PptxQAError(f"Duplicate or invalid drawing object IDs in {part}")
    background = root.find("p:cSld/p:bg/p:bgPr/a:solidFill/a:srgbClr", NS)
    background_color = background.attrib.get("val", "").upper() if background is not None else None

    def walk(container: ET.Element, transform=(1.0, 1.0, 0.0, 0.0)) -> None:
        for node in container:
            kind = _local(node.tag)
            if kind == "AlternateContent":
                choices = [child for child in node if _local(child.tag) == "Choice"]
                fallbacks = [child for child in node if _local(child.tag) == "Fallback"]
                if choices or fallbacks:
                    walk((choices or fallbacks)[0], transform)
                continue
            if kind == "grpSp":
                counts["groups"] += 1
                walk(node, _group_transform(node, transform))
                continue
            if kind not in {"sp", "cxnSp", "pic", "graphicFrame"}:
                continue
            count_key = {"sp": "shapes", "cxnSp": "connectors", "pic": "images", "graphicFrame": "graphic_frames"}[kind]
            counts[count_key] += 1
            if sum(counts[key] for key in ("shapes", "connectors", "images", "graphic_frames")) > MAX_SLIDE_OBJECTS:
                raise PptxQAError("Slide exceeds the object-count safety limit")
            text = _shape_text(node)
            if text and kind == "sp":
                counts["text_shapes"] += 1
            c_nv_pr = node.find(".//p:cNvPr", NS)
            obj = {"kind": {"sp": "text_shape" if text else "shape", "cxnSp": "connector",
                            "pic": "image", "graphicFrame": "graphic_frame"}[kind],
                   "id": c_nv_pr.attrib.get("id") if c_nv_pr is not None else None,
                   "name": c_nv_pr.attrib.get("name", "") if c_nv_pr is not None else "",
                   "text": text, "bounds": _object_bounds(node, transform)}
            hidden = c_nv_pr is not None and c_nv_pr.attrib.get("hidden") in {"1", "true"}
            text_invisible = bool(text) and _text_explicitly_invisible(node)
            obj["text_explicitly_invisible"] = text_invisible or hidden
            props = node.find("p:spPr", NS)
            outline = props.find("a:ln", NS) if props is not None else None
            custom = props.find("a:custGeom", NS) if props is not None else None
            obj["geometry"] = "custom" if custom is not None else None
            preset = props.find("a:prstGeom", NS) if props is not None else None
            if preset is not None:
                obj["geometry"] = preset.attrib.get("prst")
            geometry_invisible = _invisible_paint(props) and _invisible_paint(outline)
            custom_paths = custom.findall("a:pathLst/a:path", NS) if custom is not None else []
            if custom_paths and all(path.attrib.get("fill") == "none" and path.attrib.get("stroke") in {"0", "false"} for path in custom_paths):
                geometry_invisible = True
            obj["explicitly_invisible"] = hidden or (kind in {"sp", "cxnSp"} and geometry_invisible and (not text or text_invisible))
            shape_color = props.find("a:solidFill/a:srgbClr", NS) if props is not None else None
            obj["background_matching_geometry"] = (bool(background_color) and shape_color is not None
                                                     and shape_color.attrib.get("val", "").upper() == background_color
                                                     and _invisible_paint(outline) and not text)
            if obj["background_matching_geometry"]:
                warnings.append(_warning("background_matching_native", number, f"{obj['name'] or obj['id']}: fill matches the declared slide background and has no visible outline/text; counts alone are insufficient."))
            if obj["bounds"] and (not (obj["bounds"]["width"] > 0 or obj["bounds"]["height"] > 0)
                                   or (kind != "cxnSp" and obj["geometry"] != "line" and not (obj["bounds"]["width"] > 0 and obj["bounds"]["height"] > 0))):
                warnings.append(_warning("zero_area_object", number, f"{obj['name'] or obj['id']} has no two-dimensional extent; a line may still be intentional."))
            if obj["explicitly_invisible"] or text_invisible:
                warnings.append(_warning("explicitly_invisible_native", number, f"{obj['name'] or obj['id']}: explicit hidden/no-fill/zero-alpha evidence; counts do not prove usable editability."))
            has_image = kind == "pic" or node.find(".//a:blip", NS) is not None
            if has_image:
                obj["image_backed"] = True
                if kind != "pic":
                    counts["images"] += 1
                if counts["images"] > MAX_SLIDE_IMAGES:
                    raise PptxQAError("Slide exceeds the image-count safety limit")
                targets = []
                for descendant in node.iter():
                    for attr in (f"{{{NS['r']}}}embed", f"{{{NS['r']}}}link"):
                        rel_id = descendant.attrib.get(attr)
                        if rel_id:
                            if rel_id not in relationships:
                                raise PptxQAError(f"Unresolved image relationship {rel_id} in {part}")
                            if relationships[rel_id]["external"] or relationships[rel_id]["kind"] != "image":
                                raise PptxQAError(f"Picture references a non-internal-image relationship: {part}")
                            targets.append(relationships[rel_id]["target"])
                obj["targets"] = list(dict.fromkeys(targets))
                obj["svg"] = any(target.lower().endswith(".svg") or content_types.get(target) == "image/svg+xml" for target in targets)
                bounds = obj["bounds"]
                if bounds:
                    width_ratio, height_ratio = bounds["width"]/canvas["cx"], bounds["height"]/canvas["cy"]
                    obj["width_ratio"], obj["height_ratio"] = width_ratio, height_ratio
                    visible_width = max(0.0, min(canvas["cx"], bounds["x"]+bounds["width"])-max(0.0, bounds["x"]))
                    visible_height = max(0.0, min(canvas["cy"], bounds["y"]+bounds["height"])-max(0.0, bounds["y"]))
                    obj["canvas_coverage"] = visible_width*visible_height/(canvas["cx"]*canvas["cy"])
                    obj["full_canvas"] = visible_width >= .9*canvas["cx"] and visible_height >= .9*canvas["cy"]
                    if obj["full_canvas"]:
                        code = "full_canvas_svg" if obj["svg"] else "full_canvas_image"
                        warnings.append(_warning(code, number, f"{obj['name'] or obj['id']}: a whole-slide image is not native editable diagram objects."))
                else:
                    warnings.append(_warning("image_bounds_unknown", number, "An image has no local extent; inspect its actual rendering."))
            objects.append(obj)

    tree = root.find("p:cSld/p:spTree", NS)
    if tree is None:
        raise PptxQAError(f"Slide has no shape tree: {part}")
    walk(tree)
    native_objects = counts["shapes"]+counts["connectors"]+counts["graphic_frames"]
    native = [obj for obj in objects if obj["kind"] != "image"]
    visible_native = [obj for obj in native if not obj["explicitly_invisible"] and not obj["background_matching_geometry"]]
    if native and not visible_native:
        warnings.append(_warning("no_visible_native_evidence", number, "All counted native objects are explicitly hidden or have no visible paint/text. A large count is not an editable reconstruction."))
    image_rects = []
    for obj in objects:
        bounds = obj["bounds"]
        if obj.get("image_backed") and bounds:
            x0, y0 = max(0, bounds["x"]), max(0, bounds["y"])
            x1, y1 = min(canvas["cx"], bounds["x"]+bounds["width"]), min(canvas["cy"], bounds["y"]+bounds["height"])
            if x1 > x0 and y1 > y0:
                image_rects.append((x0, y0, x1, y1))
    image_union_fraction = _rectangle_union_area(image_rects)/(canvas["cx"]*canvas["cy"]) if image_rects else 0
    if len(image_rects) >= 4 and image_union_fraction >= .8:
        warnings.append(_warning("image_mosaic_slide", number, "Multiple images cover at least 80% of the slide. Tiling a screenshot does not make its components native editable objects."))
    if counts["images"] and not native_objects:
        warnings.append(_warning("image_only_slide", number, "No native shape, text shape, connector, or graphic frame was found."))
    if not counts["text_shapes"]:
        warnings.append(_warning("no_editable_text", number, "No native editable text shape was found."))
    return {"slide": number, "part": part, **counts, "native_objects": native_objects,
            "native_objects_not_explicitly_invisible": len(visible_native), "image_union_canvas_fraction": image_union_fraction,
            "texts": [obj["text"] for obj in objects if obj["text"]],
            "visible_texts": [obj["text"] for obj in objects if obj["text"] and not obj["text_explicitly_invisible"]], "objects": objects,
            "warnings": warnings}


def validate_pptx_package(path: str | Path) -> dict:
    """Validate bounded, passive PPTX package structure; raster-only packages are valid.

    Returns a JSON-serializable report using standard-library dependencies only.
    Raises PptxQAError on unsafe/malformed packages, never on low editability alone.
    """
    path = Path(path)
    try:
        if not path.is_file() or path.stat().st_size > MAX_PACKAGE_BYTES:
            raise PptxQAError("PPTX is missing or exceeds the package size limit")
        with zipfile.ZipFile(path) as package:
            infos = package.infolist()
            if len(infos) > MAX_ENTRIES or sum(info.file_size for info in infos) > MAX_UNCOMPRESSED_BYTES:
                raise PptxQAError("PPTX exceeds entry-count or expanded-size limits")
            names, seen = set(), set()
            for info in infos:
                _safe_name(info.filename)
                lowered = unquote(info.filename).casefold()
                if lowered in seen:
                    raise PptxQAError(f"Duplicate or case-conflicting ZIP part: {info.filename}")
                seen.add(lowered)
                if info.flag_bits & 1 or info.file_size > MAX_ENTRY_BYTES:
                    raise PptxQAError(f"Encrypted or oversized part: {info.filename}")
                if info.file_size > 1024*1024 and info.file_size/max(1, info.compress_size) > 250:
                    raise PptxQAError(f"Suspicious compression ratio: {info.filename}")
                if any(token in lowered for token in ("vbaproject", "/activex/", "/embeddings/")):
                    raise PptxQAError(f"Macros/active or embedded objects are unsupported: {info.filename}")
                if not info.is_dir():
                    names.add(info.filename)
            if not {"[Content_Types].xml", "_rels/.rels"}.issubset(names):
                raise PptxQAError("Missing OPC content-types or root relationships")
            xml_parts = {}
            for name in names:
                if name.lower().endswith((".xml", ".rels", ".svg")):
                    xml_parts[name] = _xml(package.read(name), name)
                else:
                    # Consume bounded binary entries to check ZIP CRC, without extraction.
                    with package.open(name) as entry:
                        for unused_block in iter(lambda: entry.read(1024*1024), b""):
                            pass
            types = xml_parts["[Content_Types].xml"]
            if types.tag != f"{{{CT_NS}}}Types":
                raise PptxQAError("Invalid content-types root")
            defaults, content_types = {}, {}
            for node in types:
                value = node.attrib.get("ContentType", "")
                if any(token in value.lower() for token in ("macroenabled", "vbaproject", "activex", "oleobject")):
                    raise PptxQAError("Macro/active content type is not accepted")
                if _local(node.tag) == "Default":
                    defaults[node.attrib.get("Extension", "").lower()] = value
                elif _local(node.tag) == "Override":
                    target = _resolve_target("", node.attrib.get("PartName", ""))
                    if target not in names:
                        raise PptxQAError(f"Content type points to missing part: {target}")
                    content_types[target] = value
            for name in names:
                content_types.setdefault(name, defaults.get(name.rsplit(".", 1)[-1].lower(), ""))
            relationships, citations = {}, []
            for rel_part, root in xml_parts.items():
                if not rel_part.endswith(".rels"):
                    continue
                if root.tag != f"{{{REL_NS}}}Relationships":
                    raise PptxQAError(f"Invalid relationships root: {rel_part}")
                source, mapping = _relationship_source(rel_part), {}
                if source and source not in names:
                    raise PptxQAError(f"Relationships source part is missing: {source}")
                for rel in root:
                    rel_id, rel_type, target = (rel.attrib.get(key, "") for key in ("Id", "Type", "Target"))
                    if not rel_id or rel_id in mapping or not rel_type or not target:
                        raise PptxQAError(f"Incomplete/duplicate relationship: {rel_part}")
                    rel_kind = rel_type.rsplit("/", 1)[-1].lower()
                    if rel_kind in {"oleobject", "package", "control", "vbaproject", "activexcontrol", "attachedtemplate"}:
                        raise PptxQAError(f"Active/embedded relationship is not accepted: {rel_kind}")
                    external = rel.attrib.get("TargetMode", "Internal") == "External"
                    if external:
                        parsed = urlsplit(target)
                        if rel_kind != "hyperlink" or parsed.scheme.lower() not in {"https", "http", "mailto"}:
                            raise PptxQAError(f"External non-citation link is not accepted: {rel_kind}")
                        citations.append({"source": source, "target": target})
                        resolved = target
                    else:
                        resolved = _resolve_target(source, target)
                        if resolved not in names:
                            raise PptxQAError(f"Missing relationship target: {resolved}")
                    mapping[rel_id] = {"kind": rel_kind, "target": resolved, "external": external}
                relationships[source] = mapping
            for name, root in xml_parts.items():
                for node in root.iter():
                    if _local(node.tag).lower() in {"oleobj", "control", "script", "foreignobject"}:
                        raise PptxQAError(f"Active markup is not accepted: {name}")
                    if name.lower().endswith(".svg"):
                        css = " ".join(node.attrib.values()) + " " + (node.text or "")
                        css_urls = re.findall(r"url\(\s*([^)]*?)\s*\)", css, re.I)
                        if re.search(r"@import\b", css, re.I) or any(not value.strip().strip("\"'").startswith("#") for value in css_urls):
                            raise PptxQAError(f"External SVG CSS resource is not accepted: {name}")
                        for key, value in node.attrib.items():
                            if (_local(key).lower().startswith("on") or _local(key) == "base"
                                    or (_local(key) == "href" and not value.startswith("#"))):
                                raise PptxQAError(f"Active/external SVG content is not accepted: {name}")
                    if any(_local(key) == "action" and re.match(r"ppaction://(?:program|macro|ole)", value, re.I) for key, value in node.attrib.items()):
                        raise PptxQAError(f"Executable Office action is not accepted: {name}")
            office = [rel for rel in relationships.get("", {}).values() if rel["kind"] == "officedocument" and not rel["external"]]
            if len(office) != 1:
                raise PptxQAError("Expected one internal officeDocument relationship")
            presentation_part = office[0]["target"]
            presentation = xml_parts.get(presentation_part)
            if presentation is None or presentation.tag != f"{{{NS['p']}}}presentation":
                raise PptxQAError("Missing/invalid PresentationML presentation")
            if content_types.get(presentation_part) != "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml":
                raise PptxQAError("Package is not a non-macro PPTX presentation")
            size = presentation.find("p:sldSz", NS)
            cx, cy = _integer_pair(size, ("cx", "cy"), (0, 0))
            if cx <= 0 or cy <= 0:
                raise PptxQAError("Presentation must declare positive slide dimensions")
            canvas, slides = {"cx": cx, "cy": cy}, []
            slide_ids = presentation.findall("p:sldIdLst/p:sldId", NS)
            if not slide_ids:
                raise PptxQAError("Presentation has no listed slides")
            seen_slides = set()
            for number, slide_id in enumerate(slide_ids, 1):
                rel = relationships.get(presentation_part, {}).get(slide_id.attrib.get(f"{{{NS['r']}}}id", ""))
                if not rel or rel["kind"] != "slide" or rel["external"] or rel["target"] in seen_slides:
                    raise PptxQAError("Invalid or duplicate listed-slide relationship")
                part = rel["target"]
                seen_slides.add(part)
                root = xml_parts.get(part)
                if root is None or root.tag != f"{{{NS['p']}}}sld":
                    raise PptxQAError(f"Missing/invalid slide XML: {part}")
                slides.append(_slide_report(root, number, part, relationships.get(part, {}), canvas, content_types))
            return {"package_valid": True, "validation_scope": "Bounded passive OPC/PresentationML structure, not full ISO schema or visual fidelity",
                    "output_sha256": sha256_file(path), "package_bytes": path.stat().st_size,
                    "slide_count": len(slides), "canvas": canvas, "slides": slides,
                    "citation_hyperlinks": citations, "warnings": [warning for slide in slides for warning in slide["warnings"]],
                    "editability_scope": "Object/text counts and explicit visibility diagnostics only. Unknown theme styles, occlusion, cropped images, glyph quality and semantic correspondence require actual rendering and human review.",
                    "visual_review": "not_performed", "fidelity": "not_assessed"}
    except PptxQAError:
        raise
    except (OSError, zipfile.BadZipFile, RuntimeError, KeyError, ValueError, NotImplementedError) as exc:
        raise PptxQAError(f"Could not safely inspect PPTX: {exc}") from exc


def _normalized(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).split())


def check_inventory(report: dict, inventory: dict) -> dict:
    """Compare explicit text/native-object minima; no visual or semantic pass implied."""
    if not isinstance(inventory, dict) or inventory.get("schema_version") != 1 or not isinstance(inventory.get("slides"), list) or not inventory["slides"]:
        raise PptxQAError("Inventory requires schema_version=1 and a non-empty slides list")
    failures, checked = [], set()
    allowed_counts = {"shapes", "text_shapes", "connectors", "graphic_frames", "groups", "native_objects"}
    allowed_kinds = {"shape", "text_shape", "connector", "graphic_frame"}
    for expected in inventory["slides"]:
        if not isinstance(expected, dict) or type(expected.get("slide")) is not int or expected["slide"] < 1 or expected["slide"] in checked:
            raise PptxQAError("Inventory slide indices must be distinct positive integers")
        number = expected["slide"]
        checked.add(number)
        if number > report["slide_count"]:
            failures.append({"slide": number, "code": "missing_slide"})
            continue
        actual = report["slides"][number-1]
        text = _normalized("\n".join(actual["visible_texts"]))
        required_text = expected.get("required_text", [])
        if not isinstance(required_text, list) or any(not isinstance(item, str) or not item.strip() for item in required_text):
            raise PptxQAError("required_text must be a list of non-empty strings")
        for label in required_text:
            if _normalized(label) not in text:
                failures.append({"slide": number, "code": "missing_text", "text": label})
        minima = expected.get("required_native_objects", {})
        if not isinstance(minima, dict) or any(key not in allowed_counts or type(value) is not int or value < 0 for key, value in minima.items()):
            raise PptxQAError("required_native_objects contains an unknown kind or invalid minimum")
        for key, minimum in minima.items():
            if actual[key] < minimum:
                failures.append({"slide": number, "code": "native_object_minimum", "kind": key, "required": minimum, "actual": actual[key]})
        important = expected.get("important_objects", [])
        if not isinstance(important, list):
            raise PptxQAError("important_objects must be a list")
        for required in important:
            if not isinstance(required, dict) or required.get("kind") not in allowed_kinds:
                raise PptxQAError("Each important object requires a supported native kind")
            for field in ("text", "name", "label"):
                if field in required and not isinstance(required[field], str):
                    raise PptxQAError(f"Important-object {field} must be a string")
            matches = [obj for obj in actual["objects"]
                       if (obj["kind"] == required["kind"] or (required["kind"] == "shape" and obj["kind"] == "text_shape"))
                       and ("text" not in required or _normalized(required["text"]) in _normalized(obj["text"]))
                       and ("name" not in required or required["name"] == obj["name"])
                       and not obj["explicitly_invisible"]
                       and not ("text" in required and obj["text_explicitly_invisible"])]
            if not matches:
                failures.append({"slide": number, "code": "important_object_not_native", "object": required})
    for warning in report["warnings"]:
        if warning["code"] in {"full_canvas_image", "full_canvas_svg", "image_only_slide", "image_mosaic_slide", "no_visible_native_evidence", "explicitly_invisible_native"}:
            failures.append({"slide": warning["slide"], "code": "non_editable_slide", "warning": warning["code"]})
    return {"structure_requirements_met": not failures, "failures": failures,
            "checked_slides": sorted(checked), "unchecked_slides": sorted(set(range(1, report["slide_count"]+1))-checked),
            "scope": "Text and native-object minima only; not semantic correspondence or visual fidelity"}


def compare_images(reference: str | Path, rendered: str | Path, out_dir: str | Path) -> dict:
    """Make aspect-preserving same-canvas comparisons. Metrics never grant acceptance."""
    try:
        from PIL import Image, ImageChops, ImageOps, ImageStat
    except ImportError as exc:
        raise PptxQAError("Image comparison requires Pillow; package inspection does not") from exc
    reference, rendered, out_dir = Path(reference), Path(rendered), Path(out_dir)
    outputs = [out_dir/name for name in ("reference.png", "rendered.png", "side_by_side.png", "overlay.png", "difference.png", "metrics.json")]
    if any(output.resolve() in {reference.resolve(), rendered.resolve()} for output in outputs):
        raise PptxQAError("Comparison output would overwrite an input image")
    def load(path: Path):
        try:
            with Image.open(path) as source:
                if source.width*source.height > MAX_IMAGE_PIXELS:
                    raise PptxQAError("Comparison image exceeds pixel limit")
                image = ImageOps.exif_transpose(source).convert("RGBA")
                white = Image.new("RGBA", image.size, "white")
                white.alpha_composite(image)
                return white.convert("RGB")
        except (OSError, Image.DecompressionBombError) as exc:
            raise PptxQAError(f"Invalid comparison image: {path}") from exc
    ref, candidate = load(reference), load(rendered)
    original_size = candidate.size
    scale = min(ref.width/candidate.width, ref.height/candidate.height)
    size = (max(1, round(candidate.width*scale)), max(1, round(candidate.height*scale)))
    scaled = candidate.resize(size, Image.Resampling.LANCZOS)
    aligned = Image.new("RGB", ref.size, "white")
    offset = ((ref.width-size[0])//2, (ref.height-size[1])//2)
    aligned.paste(scaled, offset)
    difference = ImageChops.difference(ref, aligned)
    mae = sum(ImageStat.Stat(difference).mean)/3
    squared = sum(sum(index*index*count for index, count in enumerate(difference.getchannel(channel).histogram())) for channel in range(3))
    rmse = math.sqrt(squared/(3*ref.width*ref.height))
    ref_gray, aligned_gray = ref.convert("L"), aligned.convert("L")
    mask = ImageChops.lighter(ref_gray.point(lambda value: 255 if value < 245 else 0), aligned_gray.point(lambda value: 255 if value < 245 else 0))
    foreground_pixels = mask.histogram()[255]
    foreground_mae = sum(ImageStat.Stat(difference, mask=mask).mean)/3 if foreground_pixels else None
    aspect_error = abs((original_size[0]/original_size[1])/(ref.width/ref.height)-1)
    warnings = []
    if aspect_error > .02:
        warnings.append("Aspect ratios differ by more than 2%; only uniform scaling and white letterboxing were applied.")
    if foreground_pixels/(ref.width*ref.height) < .01:
        warnings.append("Less than 1% foreground content; white background can dominate full-canvas metrics.")
    report = {"reference_sha256": sha256_file(reference), "rendered_sha256": sha256_file(rendered),
              "reference_size": list(ref.size), "rendered_original_size": list(original_size),
              "alignment": {"method": "uniform fit, centered white letterbox; no crop, local warp, or per-axis stretch", "scale": scale, "size": list(size), "offset": list(offset)},
              "metrics": {"mae_0_255": mae, "rmse_0_255": rmse, "foreground_union_mae_0_255": foreground_mae,
                          "foreground_fraction": foreground_pixels/(ref.width*ref.height), "relative_aspect_error": aspect_error},
              "warnings": warnings, "visual_review": "not_performed", "acceptance": "not_determined",
              "limitation": "Image comparison is diagnostic only. It does not prove PPTX editability, scientific accuracy, or a passed visual review."}
    out_dir.mkdir(parents=True, exist_ok=True)
    ref.save(outputs[0])
    aligned.save(outputs[1])
    side_by_side = Image.new("RGB", (ref.width*2, ref.height), "white")
    side_by_side.paste(ref, (0, 0))
    side_by_side.paste(aligned, (ref.width, 0))
    side_by_side.save(outputs[2])
    Image.blend(ref, aligned, .5).save(outputs[3])
    ImageOps.autocontrast(difference).save(outputs[4])
    outputs[5].write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    inspect_parser = subparsers.add_parser("inspect", help="Inspect safe OOXML and optional native/text requirements")
    inspect_parser.add_argument("--pptx", required=True, type=Path)
    inspect_parser.add_argument("--reference", type=Path)
    inspect_parser.add_argument("--inventory", type=Path)
    inspect_parser.add_argument("--report", type=Path)
    compare_parser = subparsers.add_parser("compare", help="Write diagnostics, never an automatic visual pass")
    compare_parser.add_argument("--reference", required=True, type=Path)
    compare_parser.add_argument("--rendered", required=True, type=Path)
    compare_parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "compare":
            report = compare_images(args.reference, args.rendered, args.out_dir)
            code = 0
        else:
            report = validate_pptx_package(args.pptx)
            report["output_file"] = str(args.pptx.resolve())
            report["reference_sha256"] = sha256_file(args.reference) if args.reference else None
            report["inventory_sha256"] = sha256_file(args.inventory) if args.inventory else None
            if args.inventory:
                if args.inventory.stat().st_size > 1024*1024:
                    raise PptxQAError("Inventory JSON exceeds 1 MiB limit")
                inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
                report["inventory_check"] = check_inventory(report, inventory)
                code = 0 if report["inventory_check"]["structure_requirements_met"] else 1
            else:
                report["inventory_check"] = {"status": "not_provided", "scope": "Package and object structure only; fidelity cannot be assessed"}
                code = 0
            if args.report:
                inputs = [args.pptx, args.reference, args.inventory]
                if args.report.resolve() in {path.resolve() for path in inputs if path}:
                    raise PptxQAError("Report output would overwrite an input")
                args.report.parent.mkdir(parents=True, exist_ok=True)
                args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return code
    except (PptxQAError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc), "visual_review": "not_performed"}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
