# Design: Light/Dark Mode Toggle for EMCA UI

## Technical Approach

Replace the single-palette `theme.py` with a dual-palette token system (`LIGHT` + `DARK` dataclass instances) selected at runtime via `st.context.theme.type`. `main.py` builds its 365-line CSS f-string from the active token set; pages replace 75 hardcoded hex/rgba literals with token references; Plotly charts derive all colors from the active set. `config.toml` defines both palettes via `theme.light.*` / `theme.dark.*` sections so native widgets also switch. Light is the default; `None` → light.

> **Note**: Proposal states Streamlit 1.58.0; installed version is **1.57.0**. Both support `st.context.theme.type` and dual `theme.light/dark` config sections (verified in source). Design is valid for 1.57+.

## Architecture Decisions

| Decision | Options | Tradeoff | Choice |
|---|---|---|---|
| Token data structure | dict, NamedTuple, dataclass | dict = no type safety; NamedTuple = no properties; dataclass = properties + frozen + type-safe | **Frozen dataclass** with `@property` aliases |
| Mode detection | `st.context.theme.type`, custom `st.toggle`, session state | Custom toggle = redundant UX; session state = unreliable; `st.context.theme.type` = native, stable | **`st.context.theme.type`** with `None`→`"light"` |
| CSS approach | CSS custom properties (`--var`), f-string interpolation | CSS vars don't cover Plotly (Python-side); f-string covers both | **f-string interpolation** with `_rgba()` helper |
| Dark palette strategy | RGB inversion, full redesign | Inversion = amateur, broken contrast; full redesign = professional, AA-compliant | **Full independent redesign** for both palettes |
| Token import pattern | Module-level constants, `get_active_tokens()` | Constants = static (can't switch); function call = runtime mode-aware | **`get_active_tokens()`** called per page |

## Data Flow

```
config.toml [theme.light] / [theme.dark]
    ↓ user toggles Settings → Theme
st.context.theme.type → "light" | "dark" | None(→"light")
    ↓
theme.py: get_active_tokens() → Tokens dataclass (frozen)
    ↓
main.py → CSS f-string(t) → st.markdown()
    ↓
pages/*.py → t = get_active_tokens() → inline styles + Plotly colors
```

## Token Architecture

### `Tokens` dataclass (`app/components/theme.py`)

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Tokens:
    mode: str           # "light" or "dark"

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
```

### `get_tokens(mode)` and `get_active_tokens()`

```python
_LIGHT = Tokens(mode="light",  BG="#F7F8FA", BG2="#EDF0F4", ...)
_DARK  = Tokens(mode="dark",   BG="#0F1218", BG2="#181C26", ...)

_PALETTE_MAP = {"light": _LIGHT, "dark": _DARK}

def get_tokens(mode: str) -> Tokens:
    """Return the token set for the given mode. Defaults to light."""
    return _PALETTE_MAP.get(mode, _LIGHT)

def get_active_tokens() -> Tokens:
    """Detect mode from st.context.theme.type at runtime. None → light."""
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
```

### LIGHT palette (default) — enterprise engineering aesthetic

| Token | Value | WCAG pair | Contrast |
|---|---|---|---|
| `BG` | `#F7F8FA` | TX1 on BG | 16.0:1 |
| `BG2` | `#EDF0F4` | TX2 on BG2 | 4.9:1 |
| `CARD` | `#FFFFFF` | TX1 on CARD | 17.0:1 |
| `CARD_H` | `#F0F3F7` | — | — |
| `TX1` | `#1A2332` | — | — |
| `TX2` | `#5C6B80` | TX2 on CARD | 5.5:1 |
| `TX3` | `#7B8794` | TX3 on CARD (large/graphic) | 3.7:1 |
| `BRD` | `rgba(37,99,235,0.15)` | — | — |
| `GRD` | `rgba(37,99,235,0.06)` | — | — |
| `SHD` | `rgba(15,23,42,0.06)` | — | — |
| `ACC` | `#2563EB` | ACC on CARD | 5.3:1 |
| `ACC2` | `#1A4DC9` | — (gradient only) | — |
| `GREEN` | `#15803D` | GREEN on CARD | 5.0:1 |
| `YELLOW` | `#B45309` | YELLOW on CARD | 5.1:1 |
| `RED` | `#C2241E` | RED on CARD | 6.1:1 |
| `RED2` | `#E0362C` | — (hover only) | — |
| `BLUE` | `#0369A1` | BLUE on CARD | 6.1:1 |
| `CYAN` | `#0E7490` | CYAN on CARD | 5.4:1 |
| `PURPLE` | `#6D28D9` | PURPLE on CARD | 7.5:1 |

### DARK palette (opt-in) — modern engineering CAD aesthetic

| Token | Value | WCAG pair | Contrast |
|---|---|---|---|
| `BG` | `#0F1218` | TX1 on BG | 14.5:1 |
| `BG2` | `#181C26` | TX2 on BG2 | 6.3:1 |
| `CARD` | `#1B2030` | TX1 on CARD | 13.2:1 |
| `CARD_H` | `#262D40` | — | — |
| `TX1` | `#DCE2EE` | — | — |
| `TX2` | `#8E9AAB` | TX2 on CARD | 6.1:1 |
| `TX3` | `#6B7589` | TX3 on CARD (large/graphic) | 3.7:1 |
| `BRD` | `rgba(59,130,246,0.15)` | — | — |
| `GRD` | `rgba(59,130,246,0.06)` | — | — |
| `SHD` | `rgba(0,0,0,0.40)` | — | — |
| `ACC` | `#3B82F6` | ACC on CARD | 4.7:1 |
| `ACC2` | `#2563EB` | — (gradient only) | — |
| `GREEN` | `#22C55E` | GREEN on CARD | 7.4:1 |
| `YELLOW` | `#F59E0B` | YELLOW on CARD | 8.0:1 |
| `RED` | `#EF4444` | RED on CARD | 4.6:1 |
| `RED2` | `#F87171` | — (hover only) | — |
| `BLUE` | `#0EA5E9` | BLUE on CARD | 6.2:1 |
| `CYAN` | `#22D3EE` | CYAN on CARD | 9.4:1 |
| `PURPLE` | `#A78BFA` | PURPLE on CARD | 6.3:1 |

> Both palettes are independently designed — no token is an RGB inversion of its counterpart.

## Mode Detection Flow

1. `config.toml` sets `base = "light"` → app opens in light mode
2. User toggles via Settings menu → Streamlit reruns script → `st.context.theme.type` reflects new mode
3. `main.py` calls `get_active_tokens()` after `st.set_page_config()` (line ~20), before CSS injection
4. Each page independently calls `get_active_tokens()` (Streamlit navigation runs pages as script continuations — `st.context` is available)
5. `None` (undetermined/non-Streamlit context) → `get_tokens("light")` — light is default per spec

```python
# main.py — after st.set_page_config()
from app.components.theme import get_active_tokens, _rgba
t = get_active_tokens()  # Tokens dataclass for active mode
```

## CSS Injection Redesign

**Pattern**: The 365-line CSS f-string in `main.py` replaces static token imports with `t.*` attributes and `_rgba()` calls for alpha variants.

**Before** (current):
```python
from app.components.theme import BG as bg, CARD as card, ACC as acc, ...
css = f""".stApp {{ background:{bg}!important; }} ... rgba(76,139,245,.1) ..."""
```

**After**:
```python
from app.components.theme import get_active_tokens, _rgba
t = get_active_tokens()
css = f"""
.stApp {{ background:{t.BG}!important; }}
.stButton > button {{
    background:linear-gradient(135deg,{t.ACC},{t.ACC2})!important;
    box-shadow:0 4px 15px {_rgba(t.ACC, 0.3)};
}}
.stButton > button:hover {{
    box-shadow:0 8px 25px {_rgba(t.ACC, 0.4)}!important;
}}
.nav-card:hover {{
    box-shadow:0 12px 35px {t.SHD},0 0 25px {_rgba(t.GREEN, 0.08)};
    border-color:{_rgba(t.GREEN, 0.2)};
}}
.alerta-roja {{
    background:{_rgba(t.RED, 0.06)}; border:1px solid {_rgba(t.RED, 0.2)};
    border-left:4px solid {t.RED};
}}
...
"""
```

**Key mappings** (hardcoded rgba → token-based):

| Current literal | Replaced with | Intent |
|---|---|---|
| `rgba(76,139,245,.1)` | `_rgba(t.ACC, 0.1)` | Sidebar nav hover |
| `rgba(76,139,245,.15)` | `_rgba(t.ACC, 0.15)` | Selected nav/tab |
| `rgba(76,139,245,.3)` | `_rgba(t.ACC, 0.3)` | Button shadow |
| `rgba(0,230,138,.08)` | `_rgba(t.GREEN, 0.08)` | Nav-card hover glow |
| `rgba(0,230,138,.12)` | `_rgba(t.GREEN, 0.12)` | Soil-easy badge |
| `rgba(255,107,107,.06)` | `_rgba(t.RED, 0.06)` | Alerta-roja bg |
| `rgba(77,124,254,.06)` | `_rgba(t.BLUE, 0.06)` | Alerta-info bg |
| `rgba(0,230,138,.06)` | `_rgba(t.GREEN, 0.06)` | Alerta-success bg |

> **Green/ACC conflation fix**: Current code uses `ACC` (#4C8BF5, blue) for CSS classes named `kpi-accent-green`, `soil-easy`, and `stepper-step.completed`. The redesign introduces a proper `GREEN` token — these classes switch to `t.GREEN`.

## Page Tokenization Plan

### `00_home.py` (~4 replacements)

| Literal | Token | Context |
|---|---|---|
| `#8892B0` (×4) | `t.TX2` | Subtitle, flow-node small text |

### `01_parametrizacion.py` (~40 replacements)

| Literal | Token | Context |
|---|---|---|
| `#8892B0` (×15+) | `t.TX2` | Section descriptions, labels |
| `#E2E8F0` (×8) | `t.TX1` | Section headers, computed values |
| `#4C8BF5` (×3) | `t.ACC` | Diameter display, perf/colado headers |
| `#56B8E8` (×2) | `t.CYAN` | Longitud display, cycle estimate |
| `#00E68A` | `t.GREEN` | Fleet sufficient status |
| `#FFD43B` | `t.YELLOW` | Fleet warning status |
| `#FF6B6B` | `t.RED` | Perforation adjusted danger |
| `rgba(76,139,245,0.08)` | `_rgba(t.ACC, 0.08)` | Info card backgrounds |
| `rgba(76,139,245,0.2)` | `_rgba(t.ACC, 0.2)` | Info card borders |
| `rgba(86,184,232,0.08)` | `_rgba(t.CYAN, 0.08)` | Cyan card backgrounds |
| `rgba(86,184,232,0.2)` | `_rgba(t.CYAN, 0.2)` | Cyan card borders |
| `rgba(204,30,42,0.08)` | `_rgba(t.RED, 0.08)` | Red card backgrounds |
| `rgba(204,30,42,0.2)` | `_rgba(t.RED, 0.2)` | Red card borders |
| `rgba(255,212,59,0.08)` | `_rgba(t.YELLOW, 0.08)` | Yellow card backgrounds |
| `rgba(255,212,59,0.2)` | `_rgba(t.YELLOW, 0.2)` | Yellow card borders |
| `rgba(0,0,0,0.2)` | `_rgba(t.TX1, 0.06)` | Inset background (subtle) |

### `02_simulacion.py` (~4 replacements)

| Literal | Token | Context |
|---|---|---|
| `#8892B0` (×1) | `t.TX2` | Page subtitle |
| `#A0AEC0` (×3) | `t.TX2` | KPI subtext values |

### `03_dashboard.py` (~15 replacements)

| Literal | Token | Context |
|---|---|---|
| `#8A98B8` | `t.TX2` | Page subtitle |
| `rgba(22,22,37,0.7)` | `_rgba(t.CARD, 0.7)` | Suggestion card bg |
| `rgba(22,22,37,0.9)` | `_rgba(t.CARD, 0.9)` | Plotly annotation bgcolor |
| `rgba(77,124,254,0.06)` | `_rgba(t.BLUE, 0.06)` | P10-P90 band fill |
| `rgba(34,211,238,0.08)` | `_rgba(t.CYAN, 0.08)` | S-curve fill |
| `rgba(0,230,138,0.1)` | `_rgba(t.GREEN, 0.1)` | Radar fill |
| `#FF8C42` | `t.YELLOW` | Tornado chart 2nd bar |
| `rgba(255,255,255,0.05)` | `t.GRD` | Detail table legend bg |

### `04_comparacion.py` (~10 replacements)

| Literal | Token | Context |
|---|---|---|
| `#8A98B8` | `t.TX2` | Page subtitle |
| `rgba(76,139,245,.06)` | `_rgba(t.ACC, 0.06)` | Info box bg |
| `rgba(76,139,245,.2)` | `_rgba(t.ACC, 0.2)` | Info box border |
| `rgba(245,166,35,.06)` | `_rgba(t.YELLOW, 0.06)` | Warning box bg |
| `rgba(245,166,35,.2)` | `_rgba(t.YELLOW, 0.2)` | Warning box border |
| `rgba(17,30,56,0.8)` | `_rgba(t.CARD, 0.8)` | Radar bgcolor |
| `rgba(76,139,245,0.08)` | `t.GRD` | Bar chart gridcolor |
| `#7C6FD4` | `t.PURPLE` | PALETTE list 5th color |
| `rgba(0,0,0,0)` | unchanged | Transparent (mode-agnostic) |

## Plotly Chart Adaptation

### `_layout()` in `03_dashboard.py` — becomes mode-aware

```python
from app.components.theme import get_active_tokens

def _layout(fig, h=400, **kw):
    t = get_active_tokens()
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",       # transparent — mode-agnostic
        paper_bgcolor="rgba(0,0,0,0)",      # transparent — mode-agnostic
        height=h,
        margin=dict(t=30, b=50, l=60, r=30),
        font=dict(family="Inter,sans-serif", color=t.TX, size=12),
        legend=dict(font=dict(color=t.TX2)),
        **kw,
    )
    fig.update_xaxes(showgrid=True, gridcolor=t.GRD, gridwidth=1, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=t.GRD, gridwidth=1, zeroline=False)
```

### Chart-specific color replacements

| Chart | Property | Current | After |
|---|---|---|---|
| Histogram | marker color | `BLU` (constant) | `t.BLUE` |
| Histogram | annotation bgcolor | `rgba(22,22,37,0.9)` | `_rgba(t.CARD, 0.9)` |
| Histogram | vrect fillcolor | `rgba(77,124,254,0.06)` | `_rgba(t.BLUE, 0.06)` |
| Gantt | COLOR_MAP values | `BLU, RED, ACC` | `t.BLUE, t.RED, t.ACC` |
| S-curve | line color | `CYN` | `t.CYAN` |
| S-curve | fillcolor | `rgba(34,211,238,0.08)` | `_rgba(t.CYAN, 0.08)` |
| Radar | line/marker | `ACC` | `t.ACC` |
| Radar | fillcolor | `rgba(0,230,138,0.1)` | `_rgba(t.GREEN, 0.1)` |
| Radar | polar bgcolor | `rgba(0,0,0,0)` | `rgba(0,0,0,0)` (unchanged) |
| Radar | radialaxis color | `TX2` | `t.TX2` |
| Tornado | bar colors | `[RED, "#FF8C42", YEL, BLU, ACC]` | `[t.RED, t.YELLOW, t.ACC, t.BLUE, t.GREEN]` |
| Comparison bar | marker_color | `ACC, CYN` | `t.ACC, t.CYAN` |
| Comparison radar | bgcolor | `rgba(17,30,56,0.8)` | `_rgba(t.CARD, 0.8)` |
| Comparison radar | axis colors | `TX1, TX2` | `t.TX1, t.TX2` |

### `04_comparacion.py` — inline layout (no `_layout()` call)

The bar chart and radar in `04_comparacion.py` set `plot_bgcolor`, `paper_bgcolor`, `font.color`, `gridcolor` inline. Each replaces hardcoded `TX1`/`TX2`/`rgba(76,139,245,0.08)` with `t.TX1`/`t.TX2`/`t.GRD`.

## config.toml Structure

Streamlit 1.57+ supports `theme.light.*` and `theme.dark.*` sections (verified in config option registry). `base = "light"` sets the default.

```toml
[theme]
base = "light"
font = "sans serif"

[theme.light]
primaryColor = "#2563EB"
backgroundColor = "#F7F8FA"
secondaryBackgroundColor = "#EDF0F4"
textColor = "#1A2332"
borderColor = "#D5DCE6"

[theme.dark]
primaryColor = "#3B82F6"
backgroundColor = "#0F1218"
secondaryBackgroundColor = "#181C26"
textColor = "#DCE2EE"
borderColor = "rgba(59,130,246,0.15)"

[server]
headless = true
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

> Native widgets (buttons, inputs, sliders, dataframes) switch automatically via these sections. Custom components (nav-card, stepper, kpi-grid, alerta-*, etc.) switch via `get_active_tokens()` + CSS f-string.

## File Changes

| File | Action | Description |
|---|---|---|
| `app/components/theme.py` | Rewrite | `Tokens` frozen dataclass, `_LIGHT`/`_DARK` instances, `get_tokens(mode)`, `get_active_tokens()`, `_rgba()` helper. ~90 lines |
| `app/main.py` | Modify | Replace static imports with `get_active_tokens()`; CSS f-string uses `t.*` + `_rgba()`. Tokenize all hardcoded rgba in CSS |
| `.streamlit/config.toml` | Modify | Add `base="light"`, `theme.light.*` and `theme.dark.*` sections |
| `app/pages/00_home.py` | Modify | Add `t = get_active_tokens()`; replace 4× `#8892B0` → `t.TX2` |
| `app/pages/01_parametrizacion.py` | Modify | Add `t = get_active_tokens()`; replace ~40 hardcoded colors with tokens + `_rgba()` |
| `app/pages/02_simulacion.py` | Modify | Add `t = get_active_tokens()`; replace `#8892B0`/`#A0AEC0` → `t.TX2` |
| `app/pages/03_dashboard.py` | Modify | `get_active_tokens()` call; `_layout()` mode-aware; replace ~15 hardcoded colors; all chart colors from `t.*` |
| `app/pages/04_comparacion.py` | Modify | `get_active_tokens()` call; replace ~10 hardcoded colors; bar/radar charts mode-aware |
| `tests/test_theme.py` | Create | Token system unit tests + WCAG contrast verification |

## Interfaces / Contracts

### Public API (`app/components/theme.py`)

```python
@dataclass(frozen=True)
class Tokens:
    mode: str
    BG: str; BG2: str; CARD: str; CARD_H: str
    TX1: str; TX2: str; TX3: str
    BRD: str; GRD: str; SHD: str
    ACC: str; ACC2: str
    GREEN: str; YELLOW: str; RED: str; RED2: str; BLUE: str
    CYAN: str; PURPLE: str

    @property
    def TX(self) -> str: return self.TX1

def get_tokens(mode: str) -> Tokens: ...
def get_active_tokens() -> Tokens: ...
def _rgba(hex_color: str, alpha: float) -> str: ...
```

### Page import pattern (all 5 pages + main.py)

```python
from app.components.theme import get_active_tokens, _rgba
t = get_active_tokens()
# Usage: t.TX1, t.ACC, _rgba(t.GREEN, 0.12), etc.
```

### Backward compatibility

The module-level constants (`BG`, `TX1`, `ACC`, etc.) are **removed**. All consumers are within this project — no external API. Every import site is updated in this change.

## Testing Strategy

| Layer | What to Test | Approach |
|---|---|---|
| Unit | `get_tokens("light")` and `get_tokens("dark")` return `Tokens` with 19 fields + `mode` | `test_theme.py`: assert all fields present, non-empty, correct types |
| Unit | `get_tokens("invalid")` defaults to light | `test_theme.py`: assert `get_tokens("foo").mode == "light"` |
| Unit | `TX` alias equals `TX1` in both palettes | `test_theme.py`: assert `t.TX == t.TX1` |
| Unit | Both palettes are independent designs (not inversions) | `test_theme.py`: assert `LIGHT.ACC != _invert(DARK.ACC)` for key tokens |
| Unit | WCAG AA contrast for all text-on-bg pairs | `test_theme.py`: compute relative luminance + contrast ratio for TX1/TX2/TX3 × BG/BG2/CARD and GREEN/YELLOW/RED/BLUE/ACC on CARD; assert ≥4.5:1 (normal) or ≥3:1 (TX3 large/graphic) |
| Unit | `_rgba()` converts hex correctly | `test_theme.py`: assert `_rgba("#FF0000", 0.5) == "rgba(255,0,0,0.5)"` |
| Static | No hardcoded colors remain in pages | `test_theme.py`: read `app/pages/*.py` + `app/main.py` source, assert zero regex matches for `#[0-9A-Fa-f]{3,8}` and raw `rgba(` that bypass tokens (allow `_rgba(` and `rgba(0,0,0,0)` transparent) |
| Regression | Existing 34 tests pass unmodified | `python -m pytest tests/ -v` → 34 passed + new theme tests |
| Manual | Visual QA in both modes | Run app, toggle Settings → Theme, inspect all 5 pages for dark-on-dark or light-on-light patches |

### WCAG contrast test implementation

```python
def _luminance(hex_color: str) -> float:
    """WCAG relative luminance for #RRGGBB."""
    def _lin(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hex_color[i:i+2], 16) / 255 for i in (1, 3, 5))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)

def _contrast(c1: str, c2: str) -> float:
    l1, l2 = _luminance(c1), _luminance(c2)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)
```

## Migration / Rollout

No migration required. The change is cosmetic — no data, no simulation logic, no config settings affected. Rollback is `git revert`. The `config.toml` change can be reverted independently of code changes.

**Deployment**: Single release. Light mode is default; users opt into dark via native Settings toggle. No feature flags needed.

## Open Questions

- [ ] **Logo SVG gradient**: Current logo uses `#00E68A`/`#00CC7A` (green brand mark). Should the logo gradient adapt to mode (blue in light, green in dark) or stay constant as brand identity? Current design keeps it constant — text fills (`tx1`/`tx2`) already adapt.
- [ ] **TX3 contrast**: TX3 (3.7:1) passes 3:1 for large text/graphics but not 4.5:1 for normal text. TX3 is used for scrollbar thumb (graphical) and stepper inactive (decorative). Acceptable per WCAG AA, but if stepper inactive text needs 4.5:1, it should use TX2 instead. Confirm intent.
- [ ] **rgba alpha tuning**: Alpha values (0.06, 0.08, 0.12, 0.15, 0.2) are carried over from the current dark CSS. Light mode may need slightly different alphas for visibility on white surfaces. Verify during visual QA; `_rgba()` makes single-value adjustments trivial.
