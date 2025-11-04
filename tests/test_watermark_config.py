"""Tests for watermark_config.py"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Documents', 'Invensis'))

from watermark_config import (
    get_watermark_css, get_watermark_html, get_watermark_js,
    WATERMARK_CONFIG
)


def test_get_watermark_css_contains_key_elements():
    """Test watermark CSS contains key elements"""
    css = get_watermark_css()
    assert ".watermark" in css
    assert "position" in css
    assert "bottom" in css
    assert "right" in css
    assert "@keyframes watermarkFadeIn" in css


def test_get_watermark_html_structure():
    """Test watermark HTML structure"""
    html = get_watermark_html()
    assert 'class="watermark"' in html
    assert WATERMARK_CONFIG["text"] in html


def test_get_watermark_js_when_clickable():
    """Test watermark JS when clickable"""
    if WATERMARK_CONFIG["clickable"]:
        js = get_watermark_js()
        assert "function handleWatermarkClick()" in js
        assert "handleWatermarkClick" in js


def test_watermark_config_constants():
    """Test watermark config constants"""
    assert 'text' in WATERMARK_CONFIG
    assert 'font_size' in WATERMARK_CONFIG
    assert 'color' in WATERMARK_CONFIG
    assert 'position' in WATERMARK_CONFIG

