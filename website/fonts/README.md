# Self-hosted ReFigure typography

These WOFF2 files were downloaded from the official Google Fonts service on
2026-10-14 and are served from the same site as the gallery. Browsing ReFigure
does not request fonts from Google or another third-party font CDN.

The binaries are **unmodified Google Fonts webfont payloads**, including the
service-generated Latin and headline-only subsets. Internal font family names
remain the upstream names. `Figarium Sans`, `Figarium Serif`, and
`Figarium Editorial SC` are legacy CSS family aliases, not modified font releases.
The ReFigure rename preserves these aliases and font filenames for compatibility.

| Local file | Upstream family | Style / weight | Size | Included characters |
|---|---|---|---:|---|
| `manrope-latin.woff2` | Manrope | Normal, variable 200–800 | 24,836 bytes | Google Fonts Latin subset |
| `instrument-serif-latin.woff2` | Instrument Serif | Normal, 400 | 21,032 bytes | Google Fonts Latin subset |
| `figarium-editorial-sc.woff2` | Noto Serif SC | Normal, 500 | 2,512 bytes | Only `好图，值得再用。` |

Total font payload: **48,380 bytes**. Other Chinese text uses the site's system
font fallback. If the headline is changed, request a new official text subset
and update its local file, CSS `unicode-range`, and this record together.

## Sources and licenses

Each family is distributed under the SIL Open Font License 1.1. The original
copyright notices and full license texts are bundled beside the fonts:

- Manrope: [upstream family](https://github.com/google/fonts/tree/main/ofl/manrope),
  [bundled license](Manrope-OFL.txt).
- Instrument Serif: [upstream family](https://github.com/google/fonts/tree/main/ofl/instrumentserif),
  [bundled license](Instrument-Serif-OFL.txt).
- Noto Serif SC: [upstream family](https://github.com/google/fonts/tree/main/ofl/notoserifsc),
  [bundled license](Noto-Serif-SC-OFL.txt).

The gallery's repository license does not replace these font licenses.

### Exact payloads

These links record the source of the committed bytes; they are not runtime
dependencies. Google Fonts CSS was requested with a modern desktop browser
User-Agent to select WOFF2 responses.

- Manrope [CSS request](https://fonts.googleapis.com/css2?family=Manrope:wght@200..800&display=swap),
  [Latin WOFF2](https://fonts.gstatic.com/s/manrope/v20/xn7gYHE41ni1AdIRggexSg.woff2).
- Instrument Serif [CSS request](https://fonts.googleapis.com/css2?family=Instrument+Serif&display=swap),
  [Latin WOFF2](https://fonts.gstatic.com/s/instrumentserif/v5/jizBRFtNs2ka5fXjeivQ4LroWlx-6zUTjg.woff2).
- Noto Serif SC [headline CSS request](https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@500&display=swap&text=%E5%A5%BD%E5%9B%BE%EF%BC%8C%E5%80%BC%E5%BE%97%E5%86%8D%E7%94%A8%E3%80%82),
  [headline WOFF2](https://fonts.gstatic.com/l/font?kit=H4cyBXePl9DZ0Xe7gG9cyOj7uK2-n-D2rd4FY7SwqyWq65IK9a9mwfovBtYuTllhxgiMHMWu2cb9VVM&skey=37fe335b8fd815cc&v=v36).

### SHA-256

```text
a30ddcd349703aff7464c34bef3fffdff405ee50c113440d7c8693c02d210972  manrope-latin.woff2
5eb09b5ac0e28b67c2f041c8ba6d244604ca0c0980d65912ab2d47fed84ddc31  instrument-serif-latin.woff2
0dd9402212f1b2ba0938f746777945d81c95586e8dc6692be737fdc946c5b2ea  figarium-editorial-sc.woff2
58172e0c0fac2cda8a37b348164bb55e44b0e69051e557e92b1d3f6910141f7b  Manrope-OFL.txt
129ed7618959716959f2941fdd5b49e0ad6e6c1d78726761786a00253d865521  Instrument-Serif-OFL.txt
5e0da210fb04058a8c0087985d2d456b931c2579811a49655721d3cf0c36b6d6  Noto-Serif-SC-OFL.txt
```
