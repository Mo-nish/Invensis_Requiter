import re
from watermark_config import get_watermark_css, get_watermark_html, get_watermark_js, WATERMARK_CONFIG


def test_watermark_css_contains_core_rules():
    css = get_watermark_css()
    assert ".watermark" in css
    for key in ["position", "bottom", "right", "font_size"]:
        assert str(WATERMARK_CONFIG[key]) in css


def test_watermark_html_structure():
    html = get_watermark_html()
    assert 'class="watermark"' in html
    assert WATERMARK_CONFIG["text"] in html
    if WATERMARK_CONFIG["show_tooltip"]:
        assert 'title="' in html


def test_watermark_js_click_handler_name_present_when_clickable():
    js = get_watermark_js()
    if WATERMARK_CONFIG["clickable"]:
        assert "function handleWatermarkClick()" in js
    else:
        assert js == ""


