"""
app/components/theme.py
Dual-palette token system for EMCA — single source of truth.

Two independently-designed professional palettes (LIGHT default, DARK opt-in)
selected at runtime via Streamlit's native theme toggle (st.context.theme.type).
Light is the default; an undetermined (None) context falls back to light.

Public API
----------
- ``Tokens``        frozen dataclass holding the 19 color fields + ``mode`` + ``TX`` alias
- ``get_tokens(m)`` return the token set for ``"light"`` / ``"dark"`` (default: light)
- ``get_active_tokens()`` detect the active mode at runtime via ``st.context.theme.type``
- ``_rgba(hex, a)`` convert ``#RRGGBB`` + alpha to an ``rgba(r,g,b,a)`` CSS string
"""
from dataclasses import dataclass

# ──────────────────────────────────────────────────────────────────────────
# Token dataclass
# ──────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Tokens:
    """Immutable color token set for a single palette (light or dark)."""

    mode: str

    # Background
    BG: str
    BG2: str
    # Surface
    CARD: str
    CARD_H: str
    # Text
    TX1: str
    TX2: str
    TX3: str
    # Line / Shadow (rgba strings)
    BRD: str
    GRD: str
    SHD: str
    # Accent
    ACC: str
    ACC2: str
    # Status
    GREEN: str
    YELLOW: str
    RED: str
    RED2: str
    BLUE: str
    # Hues
    CYAN: str
    PURPLE: str

    # ── Aliases (resolve to active set) ──
    @property
    def TX(self) -> str:
        return self.TX1


# ──────────────────────────────────────────────────────────────────────────
# Palette instances (exact values from design.md — do NOT modify)
# ──────────────────────────────────────────────────────────────────────────

_LIGHT = Tokens(
    mode="light",
    BG="#F7F8FA",
    BG2="#EDF0F4",
    CARD="#FFFFFF",
    CARD_H="#F0F3F7",
    TX1="#1A2332",
    TX2="#5C6B80",
    TX3="#7B8794",
    BRD="rgba(37,99,235,0.15)",
    GRD="rgba(37,99,235,0.06)",
    SHD="rgba(15,23,42,0.06)",
    ACC="#2563EB",
    ACC2="#1A4DC9",
    GREEN="#15803D",
    YELLOW="#B45309",
    RED="#C2241E",
    RED2="#E0362C",
    BLUE="#0369A1",
    CYAN="#0E7490",
    PURPLE="#6D28D9",
)

_DARK = Tokens(
    mode="dark",
    BG="#0F1218",
    BG2="#181C26",
    CARD="#1B2030",
    CARD_H="#262D40",
    TX1="#DCE2EE",
    TX2="#8E9AAB",
    TX3="#6B7589",
    BRD="rgba(59,130,246,0.15)",
    GRD="rgba(59,130,246,0.06)",
    SHD="rgba(0,0,0,0.40)",
    ACC="#4B8EF7",
    ACC2="#2563EB",
    GREEN="#22C55E",
    YELLOW="#F59E0B",
    RED="#F65A5A",
    RED2="#F87171",
    BLUE="#0EA5E9",
    CYAN="#22D3EE",
    PURPLE="#A78BFA",
)

_PALETTE_MAP = {"light": _LIGHT, "dark": _DARK}


# ──────────────────────────────────────────────────────────────────────────
# Selection
# ──────────────────────────────────────────────────────────────────────────

def get_tokens(mode: str) -> Tokens:
    """Return the token set for the given mode. Defaults to light."""
    return _PALETTE_MAP.get(mode, _LIGHT)


def get_active_tokens() -> Tokens:
    """Detect the active mode at runtime via st.context.theme.type. None -> light."""
    try:
        import streamlit as st
        mode = st.context.theme.type  # "light" | "dark" | None
    except Exception:
        mode = None
    return get_tokens(mode or "light")


def _rgba(hex_color: str, alpha: float) -> str:
    """Convert #RRGGBB to rgba(r,g,b,alpha) for CSS inline styles."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    return f"rgba({r},{g},{b},{alpha})"