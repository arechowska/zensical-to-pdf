#!/usr/bin/env python3
"""
generate_pdf.py — generate PDF from a Zensical documentation project.

Reads page order and project name from zensical.toml,
generates a PDF with cover page, table of contents, and headers/footers.

Usage:
  python3 tools/generate_pdf.py
  python3 tools/generate_pdf.py --output my.pdf
  python3 tools/generate_pdf.py --config zensical.toml --skip index.md
  python3 tools/generate_pdf.py --verbose
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print("Python 3.11+ required, or: pip install tomli")
        sys.exit(1)

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


def extract_pages(nav: list, result: list) -> None:
    for item in nav:
        if isinstance(item, str):
            result.append(item)
        elif isinstance(item, dict):
            for value in item.values():
                if isinstance(value, str):
                    result.append(value)
                elif isinstance(value, list):
                    extract_pages(value, result)


MAX_IMG_WIDTH = 800


def find_xelatex() -> str:
    for path in ["/Library/TeX/texbin/xelatex", "/usr/bin/xelatex", "/usr/local/bin/xelatex"]:
        if os.path.exists(path):
            return path
    found = shutil.which("xelatex")
    if found:
        return found
    return "xelatex"


def resize_images(media_dirs: list[str], dest: Path) -> None:
    """Copy images to dest, scaling down wide ones to MAX_IMG_WIDTH px."""
    if not HAS_PIL:
        return
    for src_dir in media_dirs:
        src_path = Path(src_dir)
        if not src_path.is_dir():
            continue
        for img_path in src_path.iterdir():
            if img_path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
                continue
            out = dest / img_path.name
            if out.exists():
                continue
            try:
                with Image.open(img_path) as im:
                    if im.width > MAX_IMG_WIDTH:
                        ratio = MAX_IMG_WIDTH / im.width
                        new_size = (MAX_IMG_WIDTH, int(im.height * ratio))
                        im = im.resize(new_size, Image.Resampling.LANCZOS)
                    im.save(out)
            except Exception:
                shutil.copy2(img_path, out)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate PDF from Zensical documentation")
    parser.add_argument("--output", default="public/documentation.pdf", metavar="FILE")
    parser.add_argument("--config", default="zensical.toml", metavar="FILE")
    parser.add_argument("--skip", nargs="*", default=[], metavar="FILE",
                        help="Pages to exclude from PDF (e.g. index.md)")
    parser.add_argument("--verbose", action="store_true",
                        help="Show full Pandoc log on error")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Config not found: {config_path}")
        sys.exit(1)

    with open(config_path, "rb") as f:
        config = tomllib.load(f)

    project = config.get("project", {})
    site_name = project.get("site_name", "Documentation")
    nav = project.get("nav", config.get("nav", []))
    docs_dir = Path(project.get("docs_dir", config.get("docs_dir", "docs")))
    lang = project.get("theme", {}).get("language", config.get("language", "en"))

    md_pages: list[str] = []
    if nav:
        extract_pages(nav, md_pages)
    else:
        md_pages = sorted(
            str(p.relative_to(docs_dir))
            for p in docs_dir.rglob("*.md")
        )

    skip = set(args.skip)
    md_files = []
    for p in md_pages:
        path = docs_dir / p
        if p in skip:
            continue
        if not path.exists():
            print(f"  skipped (not found): {p}")
            continue
        md_files.append(str(path))

    if not md_files:
        print("No files to include in PDF")
        sys.exit(1)

    print(f"Project: {site_name}")
    print(f"Pages: {len(md_files)}")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img_exts = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
    media_dirs: list[str] = []
    for dirpath, _, filenames in os.walk(docs_dir):
        if any(Path(f).suffix.lower() in img_exts for f in filenames):
            if dirpath not in media_dirs:
                media_dirs.append(dirpath)

    tmp_dir = Path(tempfile.mkdtemp(prefix="pdf_imgs_"))
    try:
        if HAS_PIL and media_dirs:
            print(f"Resizing images to {MAX_IMG_WIDTH}px...")
            resize_images(media_dirs, tmp_dir)
            resource_paths = [".", str(tmp_dir)] + media_dirs
        else:
            resource_paths = ["."] + media_dirs
        resource_path_str = os.pathsep.join(resource_paths)

        tools_dir = Path(__file__).parent
        xelatex = find_xelatex()

        cmd = [
            "pandoc",
            *md_files,
            f"--output={output_path}",
            f"--pdf-engine={xelatex}",
            f"--template={tools_dir / 'pdf_template.tex'}",
            f"--metadata-file={tools_dir / 'pdf_vars.yaml'}",
            f"--lua-filter={tools_dir / 'admonitions.lua'}",
            f"--metadata=cover-bank:{site_name}",
            f"--metadata=header-right:{site_name}",
            f"--metadata=pdf-lang:{lang}",
            "--toc",
            "--toc-depth=2",
            f"--resource-path={resource_path_str}",
            "--dpi=120",
        ]

        env = os.environ.copy()
        if sys.platform == "darwin":
            env["PATH"] = "/Library/TeX/texbin:" + env.get("PATH", "")

        result = subprocess.run(cmd, capture_output=True, text=True, env=env, check=False)

        if result.returncode != 0:
            if args.verbose:
                print(result.stderr)
            else:
                errors = [
                    line for line in result.stderr.splitlines()
                    if "error" in line.lower() or "fatal" in line.lower()
                ]
                for e in errors:
                    print(e)
                print("\nRun with --verbose for full log")
            sys.exit(1)

        size_kb = output_path.stat().st_size // 1024
        print(f"Done: {output_path} ({size_kb} KB)")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
