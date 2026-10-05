# ICINAi brand assets

Logo, icons and favicons for the International Consortium for Interpretable AI ([icinai.org](https://icinai.org)).

![All logo variants](preview.png)

The wordmark reads "AI" first. The final "i" is also a person: the ringed dot is the head, and an orbit sweeps from above the A round the whole word and closes into it.

## Logo

| File | Use |
|---|---|
| `logo/icinai-logo-color-on-dark.svg` | Primary. White letters fade into the brand gradient. Use on navy or other dark grounds. |
| `logo/icinai-logo-color-on-light.svg` | Primary on white or light grounds. Navy letters fade into the gradient. |
| `logo/icinai-logo-gradient.svg` | Color variant: the whole mark in the gradient. Works on light or dark. |
| `logo/icinai-logo-black.svg` | One-color black. |
| `logo/icinai-logo-white.svg` | One-color white. |

Each has a `lockup` version with the full name set below (`logo/icinai-lockup-*.svg`). PNG renders at 1200 and 600 px wide are in `png/`.

Keep clear space around the logo equal to the height of the ringed dot. Don't recolor, stretch or rearrange the parts. Below about 120 px wide, use the app icon instead.

## Icons

| File | Use |
|---|---|
| `icon/icinai-app-icon.svg` | App and social avatar: gradient tile, white figure. |
| `icon/icinai-app-icon-navy.svg`, `-black.svg`, `-white.svg` | Tile alternatives. |
| `icon/icinai-mark-gradient.svg`, `-black.svg`, `-white.svg` | The figure alone, no tile. |
| `icon/favicon.svg`, `icon/favicon.ico` | Browser favicon (simplified: no orbit at 16 px). |
| `png/apple-touch-icon.png` | 180 px iOS home-screen icon. |

Favicon markup:

```html
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
```

## Color

Shared with [NDIF](https://ndif.us).

| | Hex |
|---|---|
| Gradient start (purple) | `#B875B1` |
| Gradient middle | `#838CC1` |
| Gradient end (blue) | `#4EA3D1` |
| Navy ground | `#0F172A` |
| Light ground | `#F8FAFC` |
| Tagline on dark | `#94A3B8` |
| Tagline on light | `#475569` |

## Type

[Space Grotesk](https://fonts.google.com/specimen/Space+Grotesk) (SIL Open Font License): SemiBold 600 for the wordmark, Regular 400 for the tagline. All text in the SVGs is converted to outlines, so no font needs to be installed.

## Rebuilding

`source/build.py` generates every file from the geometry and palette defined at the top of the script.

```sh
npm pack @fontsource/space-grotesk && tar xzf fontsource-space-grotesk-*.tgz
pip install numpy fonttools pillow playwright
python3 source/build.py package/files
```
