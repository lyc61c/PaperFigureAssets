"""Synthetic fixtures: no Office process, network, or author code is executed."""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from xml.sax.saxutils import escape
import zipfile


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'method_pptx_qa.py'
SPEC = importlib.util.spec_from_file_location('method_pptx_qa', SCRIPT)
qa = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(qa)
P = qa.NS['p']
A = qa.NS['a']
R = qa.NS['r']
REL = qa.REL_NS
CT = qa.CT_NS
BASE_REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/'


def relationships(items):
    return f'<Relationships xmlns="{REL}">' + ''.join(
        '<Relationship ' + ' '.join(f'{key}="{escape(str(value))}"' for key, value in item.items()) + '/>'
        for item in items) + '</Relationships>'


def shape(text, object_id=2, name='Module'):
    return f'''<p:sp><p:nvSpPr><p:cNvPr id="{object_id}" name="{name}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
    <p:spPr><a:xfrm><a:off x="500000" y="500000"/><a:ext cx="2000000" cy="1000000"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>
    <p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:t>{escape(text)}</a:t></a:r></a:p></p:txBody></p:sp>'''


def connector():
    return '<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="4" name="Flow"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr><p:spPr><a:xfrm><a:off x="2500000" y="1000000"/><a:ext cx="2000000" cy="100000"/></a:xfrm></p:spPr></p:cxnSp>'


def picture(full=True, svg=False):
    width, height = (10000000, 6000000) if full else (1000000, 1000000)
    svg_ext = '<a:extLst><a:ext uri="test"><asvg:svgBlip xmlns:asvg="http://schemas.microsoft.com/office/drawing/2016/SVG/main" r:embed="rSvg"/></a:ext></a:extLst>' if svg else ''
    return f'<p:pic><p:nvPicPr><p:cNvPr id="5" name="Preview"/><p:cNvPicPr/><p:nvPr/></p:nvPicPr><p:blipFill><a:blip r:embed="rImg">{svg_ext}</a:blip></p:blipFill><p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{width}" cy="{height}"/></a:xfrm></p:spPr></p:pic>'


def minimal_parts(body=None, slide_rels=None, extras=None):
    if body is None:
        body = shape('Encoder', 2, 'Encoder block') + shape('Decoder', 3, 'Decoder block') + connector()
    content_types = f'''<Types xmlns="{CT}"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/><Default Extension="svg" ContentType="image/svg+xml"/>
    <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
    <Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/></Types>'''
    parts = {
        '[Content_Types].xml': content_types,
        '_rels/.rels': relationships([{'Id': 'rOffice', 'Type': BASE_REL+'officeDocument', 'Target': 'ppt/presentation.xml'}]),
        'ppt/presentation.xml': f'<p:presentation xmlns:p="{P}" xmlns:r="{R}"><p:sldIdLst><p:sldId id="256" r:id="rSlide"/></p:sldIdLst><p:sldSz cx="10000000" cy="6000000"/></p:presentation>',
        'ppt/_rels/presentation.xml.rels': relationships([{'Id': 'rSlide', 'Type': BASE_REL+'slide', 'Target': 'slides/slide1.xml'}]),
        'ppt/slides/slide1.xml': f'<p:sld xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}"><p:cSld><p:spTree>{body}</p:spTree></p:cSld></p:sld>',
    }
    if slide_rels:
        parts['ppt/slides/_rels/slide1.xml.rels'] = relationships(slide_rels)
    parts.update(extras or {})
    return parts


def write_package(path, parts):
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as package:
        for name, source in parts.items():
            package.writestr(name, source)
    return path


def inventory(**changes):
    slide = {'slide': 1, 'required_text': ['Encoder', 'Decoder'],
             'required_native_objects': {'shapes': 2, 'text_shapes': 2, 'connectors': 1},
             'important_objects': [{'label': 'Encoder', 'kind': 'text_shape', 'text': 'Encoder'}, {'label': 'flow', 'kind': 'connector'}]}
    slide.update(changes)
    return {'schema_version': 1, 'slides': [slide]}


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def package(self, **kwargs):
        return write_package(self.root/'test.pptx', minimal_parts(**kwargs))

    def test_native_minimal_package(self):
        report = qa.validate_pptx_package(self.package())
        self.assertTrue(report['package_valid'])
        self.assertEqual(report['slide_count'], 1)
        self.assertEqual(report['slides'][0]['shapes'], 2)
        self.assertEqual(report['slides'][0]['text_shapes'], 2)
        self.assertEqual(report['slides'][0]['connectors'], 1)
        self.assertEqual(report['slides'][0]['native_objects'], 3)
        self.assertEqual(report['slides'][0]['texts'], ['Encoder', 'Decoder'])
        self.assertEqual(report['visual_review'], 'not_performed')
        self.assertEqual(report['fidelity'], 'not_assessed')
        self.assertEqual(len(report['output_sha256']), 64)
        self.assertTrue(qa.check_inventory(report, inventory())['structure_requirements_met'])

    def test_transparent_custom_geometry_with_visible_stroke_is_native(self):
        body = '''<p:sp><p:nvSpPr><p:cNvPr id="2" name="Bezier"/></p:nvSpPr><p:spPr>
        <a:xfrm><a:off x="1000000" y="1000000"/><a:ext cx="3000000" cy="2000000"/></a:xfrm>
        <a:noFill/><a:ln><a:solidFill><a:srgbClr val="237E7B"/></a:solidFill></a:ln>
        <a:custGeom><a:pathLst><a:path w="300" h="200" fill="none"><a:moveTo><a:pt x="0" y="100"/></a:moveTo><a:cubicBezTo><a:pt x="100" y="0"/><a:pt x="200" y="200"/><a:pt x="300" y="100"/></a:cubicBezTo></a:path></a:pathLst></a:custGeom></p:spPr></p:sp>'''
        report = qa.validate_pptx_package(self.package(body=body))
        self.assertEqual(report['slides'][0]['native_objects'], 1)
        self.assertEqual(report['slides'][0]['native_objects_not_explicitly_invisible'], 1)
        self.assertFalse(report['slides'][0]['objects'][0]['explicitly_invisible'])
        self.assertTrue(qa.check_inventory(report, inventory(required_text=[], required_native_objects={'shapes': 1}, important_objects=[{'kind': 'shape', 'name': 'Bezier'}]))['structure_requirements_met'])

    def test_blank_native_count_is_not_an_editability_pass(self):
        body = ''.join(f'<p:sp><p:nvSpPr><p:cNvPr id="{i}" name="Invisible"/></p:nvSpPr><p:spPr><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr></p:sp>' for i in range(1, 11))
        report = qa.validate_pptx_package(self.package(body=body))
        self.assertEqual(report['slides'][0]['native_objects'], 10)
        self.assertIn('no_visible_native_evidence', [item['code'] for item in report['warnings']])
        self.assertFalse(qa.check_inventory(report, inventory(required_text=[], required_native_objects={'shapes': 10}, important_objects=[]))['structure_requirements_met'])

    def test_white_shapes_matching_explicit_background_warn(self):
        body = ''.join(f'<p:sp><p:nvSpPr><p:cNvPr id="{i}" name="White"/></p:nvSpPr><p:spPr><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill><a:ln><a:noFill/></a:ln></p:spPr></p:sp>' for i in range(1, 6))
        parts = minimal_parts(body=body)
        parts['ppt/slides/slide1.xml'] = parts['ppt/slides/slide1.xml'].replace('<p:cSld>', '<p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill></p:bgPr></p:bg>')
        report = qa.validate_pptx_package(write_package(self.root/'white.pptx', parts))
        self.assertIn('background_matching_native', [item['code'] for item in report['warnings']])
        self.assertIn('no_visible_native_evidence', [item['code'] for item in report['warnings']])

    def test_transparent_text_mask_does_not_meet_visible_label_inventory(self):
        body = shape('Encoder').replace('<a:r><a:t>', '<a:r><a:rPr><a:solidFill><a:srgbClr val="000000"><a:alpha val="0"/></a:srgbClr></a:solidFill></a:rPr><a:t>')
        report = qa.validate_pptx_package(self.package(body=body))
        self.assertEqual(report['slides'][0]['text_shapes'], 1)
        self.assertEqual(report['slides'][0]['texts'], ['Encoder'])
        self.assertEqual(report['slides'][0]['visible_texts'], [])
        check = qa.check_inventory(report, inventory(required_text=['Encoder'], required_native_objects={'text_shapes': 1}, important_objects=[{'kind': 'text_shape', 'text': 'Encoder'}]))
        self.assertFalse(check['structure_requirements_met'])
        self.assertIn('missing_text', [item['code'] for item in check['failures']])

    def test_nine_image_tiles_do_not_disguise_whole_slide_image(self):
        tiles = []
        for index in range(9):
            x, y = (index % 3)*3333334, (index // 3)*2000000
            tiles.append(picture(full=False).replace('id="5"', f'id="{index+5}"').replace('x="0" y="0"', f'x="{x}" y="{y}"').replace('cx="1000000" cy="1000000"', 'cx="3333334" cy="2000000"'))
        report = qa.validate_pptx_package(self.package(body=''.join(tiles), slide_rels=[{'Id': 'rImg', 'Type': BASE_REL+'image', 'Target': '../media/tile.png'}], extras={'ppt/media/tile.png': b'fixture'}))
        codes = [item['code'] for item in report['warnings']]
        self.assertNotIn('full_canvas_image', codes)
        self.assertIn('image_mosaic_slide', codes)
        self.assertAlmostEqual(report['slides'][0]['image_union_canvas_fraction'], 1.0)
        self.assertFalse(qa.check_inventory(report, inventory(required_text=[], required_native_objects={}, important_objects=[]))['structure_requirements_met'])

    def test_empty_slide_is_structurally_valid_not_fidelity(self):
        report = qa.validate_pptx_package(self.package(body=''))
        self.assertEqual(report['slides'][0]['native_objects'], 0)
        self.assertIn('no_editable_text', [item['code'] for item in report['warnings']])

    def test_fake_pptx_rejected(self):
        path = self.root/'fake.pptx'
        path.write_bytes(b'not zip')
        with self.assertRaises(qa.PptxQAError):
            qa.validate_pptx_package(path)
        write_package(path, {'hello.txt': 'not Office'})
        with self.assertRaises(qa.PptxQAError):
            qa.validate_pptx_package(path)

    def test_macro_and_active_ole_rejected(self):
        for filename in ('ppt/vbaProject.bin', 'ppt/activeX/control1.xml', 'ppt/embeddings/oleObject1.bin'):
            with self.subTest(filename=filename), self.assertRaises(qa.PptxQAError):
                qa.validate_pptx_package(self.package(extras={filename: b'payload'}))
        parts = minimal_parts()
        parts['[Content_Types].xml'] = parts['[Content_Types].xml'].replace('presentation.main+xml', 'presentation.macroEnabled.main+xml')
        with self.assertRaises(qa.PptxQAError):
            qa.validate_pptx_package(write_package(self.root/'macro.pptx', parts))
        with self.assertRaises(qa.PptxQAError):
            qa.validate_pptx_package(self.package(body='<p:oleObj/>'))

    def test_external_media_and_non_web_hyperlinks_rejected(self):
        for rel_type, target in [('image', 'https://example.com/image.png'), ('audio', 'https://example.com/audio.mp3'), ('hyperlink', 'file:///C:/private.txt'), ('hyperlink', 'javascript:alert(1)')]:
            with self.subTest(rel_type=rel_type, target=target), self.assertRaises(qa.PptxQAError):
                qa.validate_pptx_package(self.package(slide_rels=[{'Id': 'rExternal', 'Type': BASE_REL+rel_type, 'Target': target, 'TargetMode': 'External'}]))

    def test_citation_hyperlink_allowed_without_fetch(self):
        report = qa.validate_pptx_package(self.package(slide_rels=[{'Id': 'rCitation', 'Type': BASE_REL+'hyperlink', 'Target': 'https://arxiv.org/abs/2605.10832', 'TargetMode': 'External'}]))
        self.assertEqual(len(report['citation_hyperlinks']), 1)

    def test_picture_cannot_misuse_citation_relationship(self):
        with self.assertRaises(qa.PptxQAError):
            qa.validate_pptx_package(self.package(body=picture(), slide_rels=[{'Id': 'rImg', 'Type': BASE_REL+'hyperlink', 'Target': 'https://example.com/img.png', 'TargetMode': 'External'}]))

    def test_traversal_and_duplicate_names_rejected(self):
        for filename in ('../escape.txt', '/absolute.xml', 'C:/drive.xml', 'ppt\\bad.xml', 'ppt/%2e%2e/escape.xml'):
            with self.subTest(filename=filename), self.assertRaises(qa.PptxQAError):
                qa.validate_pptx_package(self.package(extras={filename: 'x'}))
        parts = minimal_parts(slide_rels=[{'Id': 'escape', 'Type': BASE_REL+'image', 'Target': '../../../escape.png'}])
        with self.assertRaises(qa.PptxQAError):
            qa.validate_pptx_package(write_package(self.root/'escape.pptx', parts))
        with self.assertRaises(qa.PptxQAError):
            qa.validate_pptx_package(self.package(extras={'PPT/PRESENTATION.XML': '<x/>'}))

    def test_size_limits_are_bounded(self):
        path = self.package()
        for limit in ('MAX_ENTRIES', 'MAX_ENTRY_BYTES', 'MAX_UNCOMPRESSED_BYTES', 'MAX_PACKAGE_BYTES'):
            with self.subTest(limit=limit), patch.object(qa, limit, 1), self.assertRaises(qa.PptxQAError):
                qa.validate_pptx_package(path)

    def test_dtd_rejected_in_utf8_and_utf16(self):
        for encoding in ('utf-8', 'utf-16'):
            source = '<!DOCTYPE test [<!ENTITY e "boom">]><test>&e;</test>'.encode(encoding)
            with self.subTest(encoding=encoding), self.assertRaises(qa.PptxQAError):
                qa.validate_pptx_package(self.package(extras={'ppt/test.xml': source}))

    def test_raster_only_is_valid_package_but_inventory_fails(self):
        path = self.package(body=picture(), slide_rels=[{'Id': 'rImg', 'Type': BASE_REL+'image', 'Target': '../media/image1.png'}], extras={'ppt/media/image1.png': b'fake-image-fixture'})
        report = qa.validate_pptx_package(path)
        self.assertTrue(report['package_valid'])
        self.assertEqual(report['slides'][0]['images'], 1)
        self.assertIn('full_canvas_image', [item['code'] for item in report['warnings']])
        result = qa.check_inventory(report, inventory())
        self.assertFalse(result['structure_requirements_met'])
        self.assertIn('missing_text', [item['code'] for item in result['failures']])
        self.assertIn('important_object_not_native', [item['code'] for item in result['failures']])
        self.assertIn('non_editable_slide', [item['code'] for item in result['failures']])

    def test_svg_as_picture_not_native(self):
        rels = [{'Id': 'rImg', 'Type': BASE_REL+'image', 'Target': '../media/image1.png'}, {'Id': 'rSvg', 'Type': BASE_REL+'image', 'Target': '../media/image1.svg'}]
        extras = {'ppt/media/image1.png': b'fixture', 'ppt/media/image1.svg': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><rect width="10" height="10"/></svg>'}
        report = qa.validate_pptx_package(self.package(body=picture(svg=True), slide_rels=rels, extras=extras))
        self.assertIn('full_canvas_svg', [item['code'] for item in report['warnings']])
        self.assertEqual(report['slides'][0]['native_objects'], 0)
        extras['ppt/media/image1.svg'] = '<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'
        with self.assertRaises(qa.PptxQAError):
            qa.validate_pptx_package(self.package(body=picture(svg=True), slide_rels=rels, extras=extras))

    def test_svg_cannot_load_css_resources(self):
        for body in ('<style>@import "https://evil.test/font.css";</style>', '<rect fill="url(https://evil.test/bg.svg)"/>', '<g xml:base="https://evil.test/"/>'):
            svg = f'<svg xmlns="http://www.w3.org/2000/svg">{body}</svg>'
            with self.subTest(body=body), self.assertRaises(qa.PptxQAError):
                qa.validate_pptx_package(self.package(extras={'ppt/media/extra.svg': svg}))

    def test_executable_office_action_rejected(self):
        body = '<p:sp><p:nvSpPr><p:cNvPr id="1" name="Run"><a:hlinkClick action="ppaction://program"/></p:cNvPr></p:nvSpPr></p:sp>'
        with self.assertRaises(qa.PptxQAError):
            qa.validate_pptx_package(self.package(body=body))

    def test_grouped_full_canvas_image_detected(self):
        grouped = '<p:grpSp><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="10000000" cy="6000000"/><a:chOff x="0" y="0"/><a:chExt cx="1000000" cy="1000000"/></a:xfrm></p:grpSpPr>'+picture(full=False)+'</p:grpSp>'
        report = qa.validate_pptx_package(self.package(body=grouped, slide_rels=[{'Id': 'rImg', 'Type': BASE_REL+'image', 'Target': '../media/image1.png'}], extras={'ppt/media/image1.png': b'fixture'}))
        self.assertIn('full_canvas_image', [item['code'] for item in report['warnings']])
        self.assertEqual(report['slides'][0]['groups'], 1)

    def test_missing_text_and_bad_inventory(self):
        report = qa.validate_pptx_package(self.package())
        result = qa.check_inventory(report, inventory(required_text=['Missing module']))
        self.assertFalse(result['structure_requirements_met'])
        for bad in ({}, {'schema_version': 1, 'slides': []}, inventory(required_native_objects={'unknown': 1})):
            with self.subTest(bad=bad), self.assertRaises(qa.PptxQAError):
                qa.check_inventory(report, bad)

    def test_cli_hash_report_and_failure_exit(self):
        path = self.package()
        reference = self.root/'reference.png'
        reference.write_bytes(b'reference')
        manifest = self.root/'inventory.json'
        manifest.write_text(json.dumps(inventory()), encoding='utf-8')
        report_path = self.root/'reports/inspect.json'
        with contextlib.redirect_stdout(io.StringIO()):
            code = qa.main(['inspect', '--pptx', str(path), '--reference', str(reference), '--inventory', str(manifest), '--report', str(report_path)])
        report = json.loads(report_path.read_text(encoding='utf-8'))
        self.assertEqual(code, 0)
        self.assertEqual(report['reference_sha256'], qa.sha256_file(reference))
        self.assertEqual(report['inventory_sha256'], qa.sha256_file(manifest))
        manifest.write_text(json.dumps(inventory(required_text=['Absent'])), encoding='utf-8')
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(qa.main(['inspect', '--pptx', str(path), '--inventory', str(manifest)]), 1)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(qa.main(['inspect', '--pptx', str(path), '--report', str(path)]), 2)
        self.assertTrue(qa.validate_pptx_package(path)['package_valid'])


try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = None


@unittest.skipUnless(Image is not None, 'Pillow optional comparison dependency unavailable')
class CompareTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def image(self, name, size, square=None):
        image = Image.new('RGB', size, 'white')
        if square:
            ImageDraw.Draw(image).rectangle(square, fill='#227766')
        path = self.root/name
        image.save(path)
        return path

    def test_comparison_uniform_scale_letterbox(self):
        reference = self.image('reference-input.png', (200, 100), (20, 20, 80, 80))
        rendered = self.image('rendered-input.png', (100, 100), (10, 10, 40, 40))
        report = qa.compare_images(reference, rendered, self.root/'comparison')
        self.assertEqual(report['alignment']['size'], [100, 100])
        self.assertEqual(report['alignment']['offset'], [50, 0])
        self.assertEqual(report['acceptance'], 'not_determined')
        self.assertGreater(report['metrics']['foreground_union_mae_0_255'], 0)
        self.assertTrue(report['warnings'])
        with Image.open(self.root/'comparison/side_by_side.png') as image:
            self.assertEqual(image.size, (400, 100))
        for name in ('overlay.png', 'difference.png', 'metrics.json'):
            self.assertTrue((self.root/'comparison'/name).is_file())

    def test_white_background_never_automatically_passes(self):
        reference = self.image('white-a.png', (100, 50))
        rendered = self.image('white-b.png', (100, 50))
        report = qa.compare_images(reference, rendered, self.root/'comparison')
        self.assertEqual(report['metrics']['mae_0_255'], 0)
        self.assertIsNone(report['metrics']['foreground_union_mae_0_255'])
        self.assertEqual(report['acceptance'], 'not_determined')
        self.assertEqual(report['visual_review'], 'not_performed')
        self.assertTrue(report['warnings'])

    def test_input_overwrite_protected(self):
        reference = self.image('reference.png', (10, 10))
        rendered = self.image('other.png', (10, 10))
        with self.assertRaises(qa.PptxQAError):
            qa.compare_images(reference, rendered, self.root)


if __name__ == '__main__':
    unittest.main()
