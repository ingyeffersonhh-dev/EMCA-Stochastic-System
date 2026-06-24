"""
tests/test_theme.py
Unit tests for the dual-palette token system (app/components/theme.py).

Covers:
- Token dataclass shape (19 fields + mode) for LIGHT and DARK
- get_tokens() mode selection + invalid default
- TX alias == TX1 in both palettes
- _rgba() hex -> rgba conversion
- WCAG AA contrast for all text-on-bg pairs in BOTH palettes
- LIGHT/DARK are independent redesigns (not RGB inversions)
- Static grep: no hardcoded colors remain in pages + main (enforced since slice 3)
"""
import re
from dataclasses import fields as dataclass_fields
from pathlib import Path

import pytest

from app.components.theme import Tokens, get_tokens, _rgba

# ────────────────────────────────────────────────────────────────────────────
# Token shape
# ────────────────────────────────────────────────────────────────────────────

# 19 color fields defined by the spec, in order — plus `mode`.
_EXPECTED_FIELDS = [
    "mode",
    "BG", "BG2", "CARD", "CARD_H",
    "TX1", "TX2", "TX3",
    "BRD", "GRD", "SHD",
    "ACC", "ACC2",
    "GREEN", "YELLOW", "RED", "RED2", "BLUE",
    "CYAN", "PURPLE",
]


def test_tokens_has_expected_fields():
    """Tokens dataclass exposes exactly mode + 19 color fields."""
    actual = [f.name for f in dataclass_fields(Tokens)]
    assert actual == _EXPECTED_FIELDS


@pytest.mark.parametrize("mode", ["light", "dark"])
def test_get_tokens_returns_all_fields_non_empty(mode):
    """get_tokens(mode) returns a Tokens instance with every field populated."""
    t = get_tokens(mode)
    assert isinstance(t, Tokens)
    assert t.mode == mode
    for name in _EXPECTED_FIELDS:
        val = getattr(t, name)
        assert isinstance(val, str) and val, f"{name} empty in {mode} palette"
    # frozen dataclass — immutable
    assert t.__dataclass_params__.frozen is True


def test_get_tokens_invalid_defaults_to_light():
    """An unknown mode MUST fall back to the LIGHT palette (spec: light default)."""
    t = get_tokens("invalid")
    assert t.mode == "light"


def test_get_tokens_none_is_handled_by_caller():
    """get_tokens(None) is not a mode string — defaults to light (None is falsy)."""
    t = get_tokens(None)  # type: ignore[arg-type]
    assert t.mode == "light"


# ────────────────────────────────────────────────────────────────────────────
# Alias
# ────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("mode", ["light", "dark"])
def test_TX_alias_equals_TX1(mode):
    """The TX alias MUST resolve to the active palette's TX1 (not a hex literal)."""
    t = get_tokens(mode)
    assert t.TX == t.TX1


# ────────────────────────────────────────────────────────────────────────────
# _rgba helper
# ────────────────────────────────────────────────────────────────────────────

def test_rgba_converts_hex_to_rgba():
    """_rgba() converts #RRGGBB + alpha to the rgba(r,g,b,alpha) CSS string."""
    assert _rgba("#FF0000", 0.5) == "rgba(255,0,0,0.5)"


def test_rgba_blue_channel():
    """Triangulate: a different hex proves _rgba parses all three channels."""
    assert _rgba("#00FF7F", 0.25) == "rgba(0,255,127,0.25)"


# ────────────────────────────────────────────────────────────────────────────
# WCAG AA contrast
# ────────────────────────────────────────────────────────────────────────────

def _luminance(hex_color: str) -> float:
    """WCAG relative luminance for #RRGGBB."""
    def _lin(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def _contrast(fg: str, bg: str) -> float:
    """WCAG contrast ratio between two #RRGGBB colors."""
    l1, l2 = _luminance(fg), _luminance(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


# Normal-text pairs MUST meet WCAG AA (>= 4.5:1); TX3 is large/graphic (>= 3:1).
_NORMAL_TEXT = ["TX1", "TX2"]
_LARGE_GRAPHIC = ["TX3"]
_BG_SURFACES = ["BG", "BG2", "CARD"]
_STATUS_ON_CARD = ["GREEN", "YELLOW", "RED", "BLUE", "ACC", "CYAN", "PURPLE"]


def _hex(token: str) -> str:
    """True hex for a token's *_luminance; rgba BRD/GRD/SHD are excluded."""
    return token  # tokens used in contrast tests are #RRGGBB


@pytest.mark.parametrize("mode", ["light", "dark"])
@pytest.mark.parametrize("fg", _NORMAL_TEXT)
@pytest.mark.parametrize("bg", _BG_SURFACES)
def test_normal_text_pairs_pass_AA(mode, fg, bg):
    """TX1/TX2 on BG/BG2/CARD MUST be >= 4.5:1 in both palettes."""
    t = get_tokens(mode)
    ratio = _contrast(getattr(t, fg), getattr(t, bg))
    assert ratio >= 4.5, f"{mode}: {fg} on {bg} = {ratio:.2f}:1 < 4.5"


@pytest.mark.parametrize("mode", ["light", "dark"])
@pytest.mark.parametrize("fg", _LARGE_GRAPHIC)
@pytest.mark.parametrize("bg", _BG_SURFACES)
def test_large_graphic_pairs_pass_AA(mode, fg, bg):
    """TX3 (large/graphic) on every background MUST be >= 3:1 in both palettes."""
    t = get_tokens(mode)
    ratio = _contrast(getattr(t, fg), getattr(t, bg))
    assert ratio >= 3.0, f"{mode}: {fg} on {bg} = {ratio:.2f}:1 < 3.0"


@pytest.mark.parametrize("mode", ["light", "dark"])
@pytest.mark.parametrize("fg", _STATUS_ON_CARD)
def test_status_colors_on_card_pass_AA(mode, fg):
    """Status/accent colors used as text on CARD MUST be >= 4.5:1."""
    t = get_tokens(mode)
    ratio = _contrast(getattr(t, fg), t.CARD)
    assert ratio >= 4.5, f"{mode}: {fg} on CARD = {ratio:.2f}:1 < 4.5"


# ────────────────────────────────────────────────────────────────────────────
# Palette independence (not RGB inversions)
# ────────────────────────────────────────────────────────────────────────────

def _invert_hex(hex_color: str) -> str:
    """Bitwise NOT of the 24-bit RGB value -> the candidate 'inverted' color."""
    n = int(hex_color[1:], 16)
    return f"#{(0xFFFFFF ^ n):06X}"


_HEX_TOKENS = ["BG", "BG2", "CARD", "TX1", "TX2", "ACC", "GREEN", "YELLOW", "RED", "BLUE"]


def test_dark_is_not_rgb_inversion_of_light():
    """LIGHT and DARK palettes must be independent designs, not inversions."""
    light = get_tokens("light")
    dark = get_tokens("dark")
    for name in _HEX_TOKENS:
        lv = getattr(light, name)
        dv = getattr(dark, name)
        # palettes differ
        assert lv != dv, f"{name}: palettes identical for {name}"
        # dark is not the bitwise inversion of light
        assert dv.upper() != _invert_hex(lv).upper(), (
            f"{name}: dark ({dv}) is the RGB inversion of light ({lv})"
        )


# ────────────────────────────────────────────────────────────────────────────
# Static: no hardcoded colors remain in pages + main (slice 3 enforces this)
# ────────────────────────────────────────────────────────────────────────────

_PAGES_DIR = Path(__file__).resolve().parent.parent / "app" / "pages"
_MAIN = Path(__file__).resolve().parent.parent / "app" / "main.py"

_HEX_RE = re.compile(r"#[0-9A-Fa-f]{3,8}\b")
_RGBA_RE = re.compile(r"rgba\(")
_ALLOWED_RGBA = re.compile(r"_rgba\(|rgba\(0,0,0,0\)")


_BRAND_SWATCH = {"#00E68A", "#00CC7A"}  # logo SVG gradient — brand identity, not theme tokens


def _hardcoded_color_lines(src: str):
    """Return lines containing a hardcoded color that bypasses the token hub."""
    offenders = []
    for line in src.splitlines():
        hex_matches = _HEX_RE.findall(line)
        # skip line if ALL hex colors are brand swatch (allow-listed)
        if hex_matches and all(h.upper() in {s.upper() for s in _BRAND_SWATCH} for h in hex_matches):
            continue
        if _HEX_RE.search(line):
            offenders.append(line.strip())
            continue
        # raw rgba( not introduced by _rgba( and not the transparent rgba(0,0,0,0)
        for m in _RGBA_RE.finditer(line):
            start = m.start()
            # allowed if immediately preceded by '_' or is rgba(0,0,0,0)
            if start > 0 and line[start - 1] == "_":
                continue
            if "rgba(0,0,0,0" in line:
                continue
            offenders.append(line.strip())
            break
    return offenders


def test_no_hardcoded_colors_in_pages_and_main():
    """After full tokenization, zero hardcoded hex/rgba bypass the token hub."""
    sources = []
    for page in sorted(_PAGES_DIR.glob("*.py")):
        sources.append((page.name, page.read_text(encoding="utf-8")))
    if _MAIN.exists():
        sources.append((_MAIN.name, _MAIN.read_text(encoding="utf-8")))

    all_offenders = []
    for name, src in sources:
        for off in _hardcoded_color_lines(src):
            all_offenders.append(f"{name}: {off}")
    assert not all_offenders, "Hardcoded colors found:\n" + "\n".join(all_offenders)