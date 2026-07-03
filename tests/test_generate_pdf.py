import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
from generate_pdf import extract_pages


def test_flat_list():
    nav = ["index.md", "intro.md"]
    result = []
    extract_pages(nav, result)
    assert result == ["index.md", "intro.md"]


def test_nested_sections():
    nav = [
        {"Overview": "index.md"},
        {"Payments": ["payments/order.md", "payments/salary.md"]},
    ]
    result = []
    extract_pages(nav, result)
    assert result == ["index.md", "payments/order.md", "payments/salary.md"]


def test_deeply_nested():
    nav = [{"Guide": [{"Payments": ["payments/order.md"]}, "guide/intro.md"]}]
    result = []
    extract_pages(nav, result)
    assert result == ["payments/order.md", "guide/intro.md"]


def test_empty_nav():
    result = []
    extract_pages([], result)
    assert result == []
