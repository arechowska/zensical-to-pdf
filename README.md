# zensical-to-pdf

PDF export for [Zensical](https://zensical.dev) documentation projects.

Generates a professional PDF from your Zensical docs with a cover page, table of contents, headers/footers, and proper handling of MkDocs admonition blocks (`!!!`).

## How it works

The script reads page order and project name from `zensical.toml`, pre-scales images to reduce memory usage, and runs Pandoc + XeLaTeX to produce the PDF.

## Requirements

- Python 3.11+
- [Pandoc](https://pandoc.org/installing.html)
- XeLaTeX:
  - macOS: `brew install --cask basictex`
  - Linux: `apt install texlive-xetex texlive-lang-cyrillic fonts-liberation`
- Python packages: `pip install Pillow`

## Installation

Copy the files from `tools/` into your project's `tools/` directory:

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
    open public/documentation.pdf
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

## CI/CD (GitLab)

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
    - python3 tools/generate_pdf.py --skip index.md --output public/documentation.pdf
  artifacts:
    paths:
      - public
```

## Font handling

Specify any system font in `pdf_vars.yaml`. If the font is not installed (common on CI servers), the tool automatically falls back to **Liberation Sans**, which is metrically identical to Arial.

This means you can set `mainfont: "Arial"` and get Arial locally on macOS and Liberation Sans on Linux CI — no configuration changes needed.

## License

MIT © Ina Arechowska
