# zensical-to-pdf

PDF export for [Zensical](https://zensical.dev) documentation projects.

Generates a professional PDF from your Zensical docs with a cover page, table of contents, headers/footers, and proper handling of MkDocs admonition blocks (`!!!`).

**Live example:** [internet-bank-docs-02ed91.gitlab.io/en/](https://internet-bank-docs-02ed91.gitlab.io/en/) — a bilingual documentation site with PDF export built with this tool.

## Quick start

1. Make sure you have Python 3.11+
2. Install [Pandoc](https://pandoc.org/installing.html)
3. Install XeLaTeX:
   - macOS: `brew install --cask basictex`
   - Linux: `apt install texlive-xetex texlive-lang-cyrillic fonts-liberation`
   - Windows: install [MiKTeX](https://miktex.org/download)

   Verify the installation:

   ```bash
   pandoc --version && xelatex --version
   ```

   Both commands should print a version number. If either fails, the tool won't run.

4. Install Python dependencies: `pip install -r requirements.txt`
5. Copy the files from `tools/` into your project's `tools/` directory and edit `pdf_vars.yaml`
6. Run: `python3 tools/generate_pdf.py --output public/documentation.pdf`

## How it works

The script reads page order and project name from `zensical.toml`, pre-scales images to reduce memory usage, and runs Pandoc + XeLaTeX to produce the PDF.

## Requirements

- Python 3.11+
- Pandoc, XeLaTeX, Pillow — see Quick start above

## Installation

Clone this repository and copy the files from `tools/` into your project's `tools/` directory (on Windows, use Git Bash):

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
| `--vars FILE` | YAML metadata file (default: `tools/pdf_vars.yaml`) |
| `--verbose` | Show full Pandoc log on error |

The script automatically reads page order and project name from `zensical.toml`. If no `nav` is defined, all `.md` files in `docs/` are included alphabetically.

### Makefile

Create a `Makefile` in the root of your project:

```makefile
build:
    zensical build --clean

pdf:
    python3 tools/generate_pdf.py --skip index.md --output public/documentation.pdf
    open public/documentation.pdf  # macOS only; on Linux use xdg-open, on Windows open manually
```

### Download button on the site

To add a PDF download button to your documentation homepage, add this line to `docs/index.md`:

```markdown
[Download PDF](documentation.pdf){ .md-button }
```

The filename in the link must match the `--output` value in your Makefile. If you change one, update both:

- `Makefile` → `--output public/your-name.pdf`
- `docs/index.md` → `[Download PDF](your-name.pdf){ .md-button }`

## Configuration (pdf_vars.yaml)

| Variable | Description |
| --- | --- |
| `mainfont` | Font name. Falls back to Liberation Sans if not found on the system |
| `geometry-left/right/top/bottom` | Page margins |
| `header-left` | Left header text |
| `header-right` | Right header text (auto-filled from `site_name` in zensical.toml) |
| `cover-title` | Cover page title |
| `cover-subtitle` | Cover page subtitle |
| `cover-org` | Organization name on cover (auto-filled from `site_name`) |
| `cover-date` | Year shown on cover |
| `toc-depth` | Table of contents depth: 1 = sections only, 2 = sections + subsections (default: 2) |

`cover-org` and `header-right` are automatically set from `site_name` in `zensical.toml` and override any values in `pdf_vars.yaml`.

## Language support

Admonition labels are automatically localized based on the `language` setting in `zensical.toml`:

```toml
[project.theme]
language = "ru"  # → Примечание, Внимание, Совет...
```

The PDF engine (LaTeX babel package) is also automatically configured for the correct language — hyphenation, typography, and text direction are handled per language.

Built-in languages: `en` (default), `ru`, `de`, `fr`, `es`. To add more, extend `BABEL_LANGS` in `generate_pdf.py` and `LABELS` in `admonitions.lua`.

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
    - python3 tools/generate_pdf.py --verbose --output public/documentation.pdf
  artifacts:
    paths:
      - public
```

> **Note:** Without a pinned version, CI always uses the latest commit of the tool. If a future update introduces a breaking change, your pipeline may fail unexpectedly. To pin to a specific release, replace `--depth 1` with `--depth 1 --branch v1.0.0` once a version tag is available. Alternatively, commit the tool files directly to your project (see the next option) — this gives full control over when you update.

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
          python3 tools/generate_pdf.py --verbose --output public/documentation.pdf
      - name: Deploy to GitHub Pages
        uses: actions/upload-pages-artifact@v3
        with:
          path: public
```

## Multilingual sites

For sites with multiple language versions (separate `zensical.toml` per language):

### Setup

Create a `pdf_vars.yaml` copy for each language. Keep all vars files in `tools/` — that's where the script looks by default:

```text
tools/
├── pdf_vars.yaml       # English
└── pdf_vars.ru.yaml    # Russian
```

### Makefile targets

```makefile
pdf-en:
    python3 tools/generate_pdf.py --config zensical.toml --vars tools/pdf_vars.yaml --output public/en/guide.pdf

pdf-ru:
    python3 tools/generate_pdf.py --config zensical.ru.toml --vars tools/pdf_vars.ru.yaml --output public/ru/guide.pdf
```

```bash
make pdf-en  # → public/en/guide.pdf
make pdf-ru  # → public/ru/guide.pdf
```

### Download buttons

Add a download button in each language's index page:

```markdown
<!-- docs/en/index.md -->
[Download PDF](guide.pdf){ .md-button }

<!-- docs/ru/index.md -->
[Скачать PDF](guide.pdf){ .md-button }
```

### CI/CD example

```yaml
pages:
  stage: deploy
  image: python:latest
  script:
    - apt-get update -qq && apt-get install -y -qq pandoc texlive-xetex texlive-lang-cyrillic fonts-liberation
    - pip install -r requirements.txt
    - git clone --depth 1 https://github.com/arechowska/zensical-to-pdf.git /tmp/pdf-tool
    - zensical build --clean
    - zensical build --config-file zensical.ru.toml
    - python3 /tmp/pdf-tool/tools/generate_pdf.py --config zensical.toml --vars tools/pdf_vars.yaml --output public/en/guide.pdf
    - python3 /tmp/pdf-tool/tools/generate_pdf.py --config zensical.ru.toml --vars tools/pdf_vars.ru.yaml --output public/ru/guide.pdf
  artifacts:
    paths:
      - public
```

## Troubleshooting

**`pandoc: command not found` or `xelatex: command not found`**
Pandoc or XeLaTeX is not installed or not on PATH. Repeat steps 2–3 from Quick start and run the verify command again.

**Cyrillic text appears as squares or question marks**
Install the Cyrillic LaTeX package: `apt install texlive-lang-cyrillic` (Linux) or add the full TeX Live distribution on macOS/Windows.

**Font not found warning**
Not an error — the tool automatically falls back to Liberation Sans. The PDF will still generate correctly.

**PDF generation fails with a cryptic error**
Run with `--verbose` to see the full LaTeX log:

```bash
python3 tools/generate_pdf.py --verbose
```

## Known limitations

- **Multiline admonitions**: admonition body on a separate indented line is not parsed — only inline single-line admonitions are supported
- **SVG images**: LaTeX does not render SVG natively; SVG files will be skipped in the PDF
- **CI speed**: `texlive-xetex` is installed on every run (~3–5 min); caching is not configured in the examples above

## Font handling

Specify any system font in `pdf_vars.yaml`. If the font is not installed (common on CI servers), the tool automatically falls back to **Liberation Sans**, which is metrically identical to Arial.

This means you can set `mainfont: "Arial"` and get Arial locally on macOS and Liberation Sans on Linux CI — no configuration changes needed.

## License

MIT © Ina Arechowska
