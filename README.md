# zensical-to-pdf

PDF export for [Zensical](https://zensical.dev) documentation projects.

Generates a professional PDF from your Zensical docs with a cover page, table of contents, headers/footers, and proper handling of MkDocs admonition blocks (`!!!`).

## Quick start

1. Install [Pandoc](https://pandoc.org/installing.html)
2. Install XeLaTeX:
   - macOS: `brew install --cask basictex`
   - Linux: `apt install texlive-xetex texlive-lang-cyrillic fonts-liberation`
   - Windows: install [MiKTeX](https://miktex.org/download)
3. Install Python dependencies: `pip install -r requirements.txt`
4. Copy the files from `tools/` into your project's `tools/` directory and edit `pdf_vars.yaml`
5. Run: `python3 tools/generate_pdf.py --output public/documentation.pdf`

## How it works

The script reads page order and project name from `zensical.toml`, pre-scales images to reduce memory usage, and runs Pandoc + XeLaTeX to produce the PDF.

## Requirements

- Python 3.11+
- Pandoc, XeLaTeX, Pillow — see Quick start above

## Installation

Clone this repository and copy the files from `tools/` into your project's `tools/` directory:

```bash
git clone https://github.com/arechowska/zensical-to-pdf.git
cp zensical-to-pdf/tools/generate_pdf.py \
   zensical-to-pdf/tools/pdf_template.tex \
   zensical-to-pdf/tools/admonitions.lua \
   zensical-to-pdf/tools/pdf_vars.yaml \
   your-project/tools/
```

```text
tools/
├── generate_pdf.py    # main script
├── pdf_template.tex   # LaTeX template
├── admonitions.lua    # Lua filter for MkDocs admonition blocks
└── pdf_vars.yaml      # project-specific settings (copy and edit)
```

Edit `pdf_vars.yaml` with your project details.

## Usage

```bash
python3 tools/generate_pdf.py --output public/documentation.pdf
```

Optional flags:

| Flag | Description |
| --- | --- |
| `--output FILE` | Output path (default: `public/documentation.pdf`) |
| `--config FILE` | Zensical config file (default: `zensical.toml`) |
| `--skip FILE ...` | Pages to exclude from PDF (e.g. `--skip index.md`) |
| `--verbose` | Show full Pandoc log on error |

The script automatically reads page order and project name from `zensical.toml`. If no `nav` is defined, all `.md` files in `docs/` are included alphabetically.

### Makefile

```makefile
build:
    zensical build --clean

pdf:
    python3 tools/generate_pdf.py --skip index.md --output public/documentation.pdf
    open public/documentation.pdf  # macOS; use xdg-open on Linux
```

## Configuration (pdf_vars.yaml)

| Variable | Description |
| --- | --- |
| `mainfont` | Font name. Falls back to Liberation Sans if not found on the system |
| `geometry-left/right/top/bottom` | Page margins |
| `header-left` | Left header text |
| `header-right` | Right header text (auto-filled from `site_name` in zensical.toml) |
| `cover-title` | Cover page title |
| `cover-subtitle` | Cover page subtitle |
| `cover-bank` | Organization name on cover (auto-filled from `site_name`) |
| `cover-date` | Year shown on cover |

`cover-bank` and `header-right` are automatically set from `site_name` in `zensical.toml` and override any values in `pdf_vars.yaml`.

## Language support

Admonition labels are automatically localized based on the `language` setting in `zensical.toml`:

```toml
[project.theme]
language = "ru"  # → Примечание, Внимание, Совет...
```

Supported languages: `en` (default), `ru`. To add more, extend `LABELS` in `admonitions.lua`.

## CI/CD

Make sure `Pillow` is in your `requirements.txt`:

```text
Pillow>=10.0.0
```

### GitLab — tool downloaded from GitHub

```yaml
pages:
  stage: deploy
  image: python:latest
  script:
    - apt-get update -qq && apt-get install -y -qq pandoc texlive-xetex texlive-lang-cyrillic fonts-liberation
    - pip install -r requirements.txt
    - git clone --depth 1 https://github.com/arechowska/zensical-to-pdf.git /tmp/zensical-to-pdf
    - cp /tmp/zensical-to-pdf/tools/generate_pdf.py /tmp/zensical-to-pdf/tools/pdf_template.tex /tmp/zensical-to-pdf/tools/admonitions.lua tools/
    - zensical build --clean
    - python3 tools/generate_pdf.py --output public/documentation.pdf
  artifacts:
    paths:
      - public
```

### GitLab — tool files committed to the project

Use this if your CI has no external internet access, or if you want to pin the tool version. Commit the three tool files to your project's `tools/` directory — no download needed at CI time.

```yaml
pages:
  stage: deploy
  image: python:latest
  script:
    - apt-get update -qq && apt-get install -y -qq pandoc texlive-xetex texlive-lang-cyrillic fonts-liberation
    - pip install -r requirements.txt
    - zensical build --clean
    - python3 tools/generate_pdf.py --output public/documentation.pdf
  artifacts:
    paths:
      - public
```

### GitHub Actions

```yaml
name: Deploy docs

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install dependencies
        run: |
          sudo apt-get update -qq && sudo apt-get install -y -qq pandoc texlive-xetex texlive-lang-cyrillic fonts-liberation
          pip install -r requirements.txt
      - name: Download pdf tool
        run: git clone --depth 1 https://github.com/arechowska/zensical-to-pdf.git /tmp/zensical-to-pdf
      - name: Copy tool files
        run: cp /tmp/zensical-to-pdf/tools/generate_pdf.py /tmp/zensical-to-pdf/tools/pdf_template.tex /tmp/zensical-to-pdf/tools/admonitions.lua tools/
      - name: Build and generate PDF
        run: |
          zensical build --clean
          python3 tools/generate_pdf.py --output public/documentation.pdf
      - name: Deploy to GitHub Pages
        uses: actions/upload-pages-artifact@v3
        with:
          path: public
```

## Font handling

Specify any system font in `pdf_vars.yaml`. If the font is not installed (common on CI servers), the tool automatically falls back to **Liberation Sans**, which is metrically identical to Arial.

This means you can set `mainfont: "Arial"` and get Arial locally on macOS and Liberation Sans on Linux CI — no configuration changes needed.

## Windows

The script is compatible with Windows. Install Pandoc and MiKTeX (which includes XeLaTeX), then run the script as usual.

Note: the `open` command in the Makefile example is macOS-only. On Windows, use `start` instead, or open the file manually.

## License

MIT © Ina Arechowska
