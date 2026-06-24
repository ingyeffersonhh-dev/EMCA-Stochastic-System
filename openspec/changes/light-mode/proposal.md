# Proposal: light-mode

- **Change ID**: `light-mode`
- **Title**: Add light/dark mode toggle to EMCA UI
- **Status**: proposed
- **Created**: 2026-06-23

## Intent

Users want a light mode option for accessibility and flexibility. The current
app is dark-only — every color is hardcoded for a dark palette with `!important`
overrides that ignore Streamlit's native theme system. This change adds a
runtime light/dark switch that works across all pages, custom CSS, and Plotly
charts.

### Product decisions (approved by user)

1. **Full palette redesign for BOTH modes** — not a simple inversion. Both the
   light and dark palettes are redesigned to professional-grade standards worthy
   of a system named "SISTEMA DE GESTIÓN ESTOCÁSTICA PARA LA PLANIFICACIÓN DE
   PERFORACIÓN DE PILOTES MEDIANTE MODELOS DE PRONÓSTICO DE TIEMPOS DE CICLO".
   The aesthetic targets enterprise engineering/construction software: clean,
   authoritative, high-contrast, data-legible.
2. **Light mode is the default** — the app opens in light mode on first visit.
   `config.toml` sets `base="light"`. Dark mode is the user's opt-in.
3. **No OS preference detection** — the app always starts in light mode
   (default) regardless of `prefers-color-scheme`. The user switches via
   Streamlit's native Settings menu toggle. No `prefers-color-scheme` media
   query.

## Current State

### Architecture

| File | Role | Lines |
|---|---|---|
| `app/components/theme.py` | 17 dark color constants + 4 aliases. Single source of truth. | 38 |
| `app/main.py` | ~365 lines of inline CSS injected via `st.markdown(css, unsafe_allow_html=True)`. CSS uses f-string interpolation with theme tokens. Defines 15+ custom component classes (nav-card, stepper, kpi-grid, alerta-*, etc.). | 491 |
| `.streamlit/config.toml` | `[theme]` section with dark colors hardcoded. No `base` key. No light theme defined. | 14 |

### How colors flow today

```
theme.py (17 dark constants)
    ↓ imported
main.py → builds CSS f-string → st.markdown(unsafe_allow_html=True)
    ↓
Pages use a MIX of:
  - theme.py imports (03_dashboard, 04_comparacion)
  - hardcoded hex literals: #8892B0, #E2E8F0, #4C8BF5, #A0AEC0, #00E68A, #FFD43B, #FF6B6B
  - hardcoded rgba(): rgba(76,139,245,0.08), rgba(22,22,37,0.7), rgba(0,230,138,0.1), ...
```

### Problem: 75 hardcoded colors in pages

A grep across `app/pages/*.py` found **75 inline hardcoded hex/rgba colors** that
bypass `theme.py` entirely:

| Page | Hardcoded colors | Example |
|---|---|---|
| `01_parametrizacion.py` | ~40 (heaviest) | `#8892B0`, `#E2E8F0`, `#4C8BF5`, `rgba(76,139,245,0.08)` |
| `03_dashboard.py` | ~15 | `rgba(22,22,37,0.9)`, `rgba(0,230,138,0.1)`, `#FF8C42` |
| `04_comparacion.py` | ~10 | `rgba(17,30,56,0.8)`, `rgba(245,166,35,0.06)` |
| `00_home.py` | ~4 | `#8892B0` (subtitle, should be TX2) |
| `02_simulacion.py` | ~4 | `#8892B0`, `#A0AEC0` |

These hardcoded colors are the core obstacle: even if we configure a light theme
in `config.toml`, the inline `!important` CSS and hardcoded hex values will
override it, keeping the app dark.

### Streamlit native theming (verified)

Streamlit 1.58.0 (installed) supports:
- **Dual light/dark themes in `config.toml`** — users switch via the hamburger
  menu → Settings → Theme. No restart needed.
- **`st.context.theme.type`** — returns `"light"` or `"dark"` at runtime
  (verified: `StreamlitTheme` class with `type: Literal["dark", "light"] | None`).
  When the user toggles theme, Streamlit reruns the script and `st.context.theme`
  reflects the new mode.
- **CSS variables** — `--st-text-color`, `--st-background-color`,
  `--st-border-color`, `--st-font` auto-update based on active theme.

### What's broken with a config-only approach

The 365 lines of custom CSS in `main.py` use hardcoded hex values with
`!important` (e.g. `background:{card}!important`). These override Streamlit's
native CSS variables, so changing `config.toml` alone has NO visible effect on
custom components. The CSS must be made mode-aware.

## Proposed Approach

### Recommendation: Option C — Dual token sets + `st.context.theme` detection

> **Note**: Both palettes (light AND dark) receive a full professional redesign.
> Light mode is the default. No OS preference detection — always starts light.

### Option A: Streamlit native theme via `config.toml` only

Define `[theme]` with `base="light"` and dark overrides in `config.toml`.

| Pros | Cons |
|---|---|
| Zero code changes | 75 hardcoded colors + 365 lines of `!important` CSS override native theme — no visible effect |
| Native toggle in settings menu | No control over Plotly chart colors (set in Python) |
| | Pages still use hardcoded hex — light mode would look broken |

**Verdict**: Necessary as foundation but insufficient alone.

### Option B: CSS variables + custom session-state toggle

Replace hardcoded colors with `var(--st-*)` CSS variables. Add a custom
`st.toggle` in the sidebar.

| Pros | Cons |
|---|---|
| Full control over toggle UI | Redundant — Streamlit already has a native toggle in settings |
| CSS variables auto-update | Two toggles (native + custom) = confusing UX |
| | Session state doesn't reliably persist theme across reruns |
| | Doesn't solve Plotly chart colors (Python-side, not CSS) |

**Verdict**: Redundant and confusing. Reject.

### Option C: Dual token sets in `theme.py` + `st.context.theme` detection (RECOMMENDED)

Add a LIGHT token set to `theme.py`. Use `st.context.theme.type` to detect the
user's choice from the native settings menu. Inject the matching CSS and feed
the matching tokens to Plotly.

```
config.toml: define both [theme] (light base) + dark overrides
    ↓ user toggles in Settings menu
st.context.theme.type → "light" | "dark"
    ↓
theme.py: get_tokens(mode) → returns DARK or LIGHT token set
    ↓
main.py: builds CSS with the active token set → st.markdown()
    ↓
pages: import tokens from theme.py (replace 75 hardcoded colors)
    ↓
Plotly: _layout() and chart colors use active token set
```

| Pros | Cons |
|---|---|
| Works WITH Streamlit's native toggle (no duplicate UI) | Must tokenize 75 hardcoded colors across 5 pages |
| Keeps centralized token architecture | Must design a full light palette (17 tokens) with good contrast |
| Handles BOTH CSS and Plotly charts | `st.context.theme` is relatively new (2025) — API stable in 1.58 |
| Runtime switch, no restart | rgba() opacities need light-mode equivalents |
| No new components or layout changes | |

### Why Option C wins

1. **No duplicate toggle** — leverages Streamlit's built-in settings menu toggle
2. **Single source of truth** — `theme.py` remains the token hub, now with two sets
3. **Covers everything** — CSS, inline styles, AND Plotly charts all respond to mode
4. **Minimal surface area** — no new components, no layout changes, no session state hacks
5. **Graceful degradation** — if `st.context.theme.type` is `None` (undetermined),
   default to dark (current behavior)

## Scope

### Files that WILL change

| File | Changes |
|---|---|
| `app/components/theme.py` | Full redesign: 17 LIGHT tokens + 17 DARK tokens (both new professional palettes) + aliases. Add `get_tokens(mode)` helper returning a named tuple or dataclass of the active set. Light is default. |
| `app/main.py` | Detect mode via `st.context.theme.type`. Build CSS f-string with the active token set. Add light-mode equivalents for custom component classes (gradients, hover states, scrollbar). |
| `.streamlit/config.toml` | Set `base="light"` with the new light palette as default. Add dark-mode overrides so the native toggle switches between redesigned palettes. Set `font="sans serif"` (keep). |
| `app/pages/00_home.py` | Replace ~4 hardcoded `#8892B0` with `TX2` token. |
| `app/pages/01_parametrizacion.py` | Replace ~40 hardcoded colors with theme.py tokens. Replace `rgba(...)` backgrounds with token-based equivalents. |
| `app/pages/02_simulacion.py` | Replace ~4 hardcoded `#8892B0`, `#A0AEC0` with tokens. |
| `app/pages/03_dashboard.py` | Make `_layout()` mode-aware (grid color, font color, annotation bgcolor). Replace ~15 hardcoded `rgba(...)` with tokens. |
| `app/pages/04_comparacion.py` | Make Plotly charts mode-aware. Replace ~10 hardcoded `rgba(...)` with tokens. |

### Files that WON'T change

- `core/` — no business logic, simulation, or analytics changes
- `config/settings.toml` — no simulation parameter changes
- `app/components/stepper.py` — uses CSS classes from main.py, no direct colors
- `tests/` — no test changes (UI theming is not covered by existing tests)
- No new pages, no new components, no layout redesign

## Non-Goals

- **No layout redesign** — component structure, spacing, and layout stay identical
- **No new UI components** — no custom toggle widget, no theme picker dropdown
- **No core logic changes** — simulation, KPIs, analytics untouched
- **No Plotly chart redesign** — same chart types, only colors adapt to mode
- **No persistence of theme preference** — Streamlit's native toggle handles this
- **No per-page theming** — the toggle is global, all pages switch together

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| 75 hardcoded colors missed during tokenization | Patches of dark-on-dark or light-on-light in light mode | Grep audit before/after; visual QA in both modes |
| Light palette contrast ratios insufficient | Accessibility issues (WCAG AA failure) | Verify contrast for each token pair (TX1/TX2 on CARD, etc.) — both redesigned palettes must pass WCAG AA |
| Full palette redesign increases design effort | More time to define 34 tokens (17 light + 17 dark) vs simple inversion | Design tokens systematically with contrast verification per pair |
| `rgba()` opacities look wrong on light backgrounds | Washed-out borders, invisible hover states | Design light-mode rgba equivalents per token (separate alpha values) |
| Plotly annotation `bgcolor` hardcoded as `rgba(22,22,37,0.9)` | Dark annotation boxes on light charts | Replace with token-derived bgcolor in `_layout()` |
| `st.context.theme.type` returns `None` | No mode detected, falls back to dark | Default to dark (current behavior) when type is None |
| `!important` conflicts with native theme variables | Native widgets (buttons, inputs) may not fully switch | Keep `!important` for custom components; use native theme for Streamlit widgets |
| Theme toggle triggers full script rerun | Brief flicker on mode switch | Acceptable — same behavior as any Streamlit interaction |

## Rollback Plan

This is a UI-only change with no impact on simulation logic or data. Rollback
is a simple `git revert` of the change commits. No data migrations, no config
breakage. The `config.toml` change can be reverted independently of the code
changes.

## Performance / Reproducibility Impact

None. Theming is purely cosmetic — no changes to seed wiring, distribution
parameters, replica counts, or simulation engine. Plotly chart rendering
performance is unchanged (same number of traces, same data).
