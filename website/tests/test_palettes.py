"""Optional authoring tests; site builds never require Pillow."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("extract_palettes", Path(__file__).parents[1] / "extract_palettes.py")
palettes = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(palettes)
try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = None


@unittest.skipIf(Image is None, "Pillow is an optional palette-authoring dependency")
class PaletteTests(unittest.TestCase):
    def test_deterministic_actual_pixels_and_antialias_deduplication(self):
        image = Image.new("RGB", (80, 80), "white")
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 19, 79), fill="#2563EB")
        draw.rectangle((20, 0, 39, 79), fill="#DE5A42")
        draw.rectangle((40, 0, 59, 79), fill="#36A16B")
        draw.line((60, 0, 60, 79), fill="#8DADF4")
        first = palettes.extract_image_palette(image)
        self.assertEqual(first, palettes.extract_image_palette(image))
        actual = {"#%02X%02X%02X" % rgb for rgb in image.getdata()}
        self.assertTrue(all(row["hex"] in actual for row in first["colors"]))
        self.assertEqual(len(first["colors"]), 3)

    def test_white_background_black_text_and_grid_are_not_palette(self):
        image = Image.new("RGB", (100, 100), "white")
        draw = ImageDraw.Draw(image)
        draw.line((0, 50, 99, 50), fill="#DDDDDD", width=2)
        draw.rectangle((10, 10, 30, 20), fill="black")
        result = palettes.extract_image_palette(image)
        self.assertEqual(result["colors"], [])
        self.assertEqual(result["mode"], "empty")

    def test_transparency_does_not_introduce_hidden_rgb_colors(self):
        image = Image.new("RGBA", (50, 50), (255, 0, 0, 0))
        ImageDraw.Draw(image).rectangle((10, 10, 20, 20), fill=(40, 120, 220, 255))
        result = palettes.extract_image_palette(image)
        self.assertEqual([r["hex"] for r in result["colors"]], ["#2878DC"])

    def test_rare_thin_line_survives_dominant_color(self):
        image = Image.new("RGB", (200, 200), "#2563EB")
        ImageDraw.Draw(image).line((0, 0, 11, 0), fill="#E34735", width=1)
        self.assertIn("#E34735", [r["hex"] for r in palettes.extract_image_palette(image)["colors"]])

    def test_scattered_color_noise_is_not_a_rare_series(self):
        image = Image.new("RGB", (200, 200), "#2563EB")
        for index in range(12):
            image.putpixel((index * 10, index * 10), (227, 71, 53))
        self.assertNotIn("#E34735", [r["hex"] for r in palettes.extract_image_palette(image)["colors"]])

    def test_grayscale_uses_real_middle_grays_and_discloses_scope(self):
        image = Image.new("L", (100, 100), 255)
        draw = ImageDraw.Draw(image)
        for i, value in enumerate((64, 104, 152, 192)):
            draw.rectangle((i * 20, 0, i * 20 + 19, 99), fill=value)
        result = palettes.extract_image_palette(image)
        self.assertEqual(result["mode"], "grayscale")
        self.assertEqual(len(result["colors"]), 4)
        self.assertIn("not inferred data-series colors", result["note"])

    def test_invalid_input_and_color_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(palettes.PaletteError):
                palettes.extract_palette(Path(directory))
            with self.assertRaises(palettes.PaletteError):
                palettes.extract_palette(Path(directory) / "missing.png")
            bad = Path(directory) / "bad.png"
            bad.write_bytes(b"not an image")
            with self.assertRaises(palettes.PaletteError):
                palettes.extract_palette(bad)
        with self.assertRaises(palettes.PaletteError):
            palettes.extract_image_palette(Image.new("RGB", (1, 1)), 0)

    def test_single_colored_noise_pixel_does_not_block_gray_fallback(self):
        image = Image.new("RGB", (30, 30), "#909090")
        image.putpixel((15, 15), (255, 0, 0))
        result = palettes.extract_image_palette(image)
        self.assertEqual(result["mode"], "grayscale")
        self.assertEqual([row["hex"] for row in result["colors"]], ["#909090"])


if __name__ == "__main__":
    unittest.main()
