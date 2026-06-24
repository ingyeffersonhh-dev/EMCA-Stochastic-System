# Theme Specification

> New spec for the `theme` domain (no prior spec existed). Change: `light-mode`.
>
> **Resolution of a proposal conflict**: the proposal body (Risks / Option C
> recap) says default to dark when `st.context.theme.type` is `None`, but the
> approved product decisions state light is the default. This spec follows the
> approved product decisions: **light is the default; `None` → light.**

## Purpose

Governs the EMCA UI color/token system, light/dark mode switching, and Plotly
chart coloring. Two full, independently-designed professional palettes (light
default, dark opt-in) selected at runtime via Streamlit's native theme toggle.
The change is **cosmetic only** — core logic, simulation, analytics, and data
flow are untouched; the 34/34 test suite passes unmodified.

## Requirements

### Requirement: Token System

`app/components/theme.py` SHALL hold two complete, independently-designed
palettes — LIGHT and DARK — exposing identical token categories. LIGHT is the
default. Each palette MUST provide these token categories:

| Group | Tokens |
|---|---|
| Background | `BG`, `BG2` |
| Surface | `CARD`, `CARD_H` |
| Text | `TX1` (primary), `TX2` (secondary), `TX3` (tertiary) |
| Line/Shadow | `BRD` (border), `GRD` (grid), `SHD` (shadow) |
| Accent | `ACC`, `ACC2` |
| Status | `GREEN` (success), `YELLOW` (warning), `RED`, `RED2` (danger), `BLUE` (info) |
| Hues | `CYAN`, `PURPLE` |
| Aliases | `TX`, `BLUE`, `YELLOW`, `CYAN`, `PURPLE` (resolve to active set) |

The system MUST expose `get_tokens(mode)` returning the active set for a given
mode. Both palettes are **full redesigns**, not RGB inversions.

#### Scenario: both palettes are full redesigns

- GIVEN the LIGHT and DARK token sets
- WHEN any token value is compared across the two sets
- THEN it is an independently chosen professional-grade color, not a simple RGB inversion of its counterpart.

#### Scenario: aliases follow active mode

- GIVEN DARK mode is active and `get_tokens("dark")`
- WHEN code reads the alias `TX`
- THEN the value equals DARK `TX1`, never a hardcoded hex literal.

### Requirement: WCAG AA Contrast

Every text-on-background pair in BOTH palettes MUST meet WCAG AA: ≥4.5:1 for
normal text, ≥3:1 for large text and graphical objects. Status colors used as
text MUST meet the same threshold against their backgrounds.

#### Scenario: light pairs pass AA

- GIVEN the LIGHT palette
- WHEN contrast is computed for TX1, TX2, TX3 each against BG, BG2, CARD
- THEN every normal-text pair is ≥4.5:1 and every large-text/graphic pair ≥3:1.

#### Scenario: dark pairs pass AA

- GIVEN the DARK palette
- WHEN the same pairs are computed
- THEN all thresholds pass.

### Requirement: Mode Detection

The system SHALL detect the active mode from `st.context.theme.type`. Values
`"light"` or `"dark"` select that mode. When the value is `None`, the system
MUST default to `"light"`. The system MUST NOT implement
`prefers-color-scheme` media-query detection.

#### Scenario: light default when undetermined

- GIVEN `st.context.theme.type` returns `None`
- WHEN the app builds its tokens and CSS
- THEN the LIGHT palette is applied.

#### Scenario: native toggle drives rerun

- GIVEN the app is running in light mode
- WHEN the user switches theme in Streamlit's Settings menu to dark
- THEN Streamlit reruns the script and `st.context.theme.type` returns `"dark"`.

### Requirement: config.toml Light Base

`.streamlit/config.toml` MUST set `[theme] base = "light"` with the redesigned
LIGHT palette as the active default, and MUST define DARK overrides so
Streamlit's native toggle switches between the redesigned palettes. `font`
SHALL remain `"sans serif"`.

#### Scenario: app opens in light by default

- GIVEN a fresh visitor with no stored preference and `base="light"`
- WHEN the app first renders
- THEN the LIGHT palette is active on all pages and native widgets render light.

### Requirement: CSS Injection from Active Tokens

`app/main.py` MUST build its injected CSS from the active token set via
`get_tokens(mode)`. All 75 hardcoded hex and raw `rgba()` literals across
`app/pages/*.py` and `main.py` MUST be replaced with token references. rgba()
opacities MUST have light-mode equivalents that preserve hover/border/subtle-
background intent (not a plain value swap).

#### Scenario: no hardcoded colors remain in pages

- GIVEN tokenization complete
- WHEN a grep searches `app/pages/*.py` for literal hex (`#[0-9A-Fa-f]{3,6}`) and raw `rgba(`
- THEN zero matches bypass the token hub.

#### Scenario: light-mode rgba equivalents preserve intent

- GIVEN LIGHT mode with a token-based hover/border/subtle background
- WHEN it renders on a light surface
- THEN it is visibly distinct from the resting surface and matches the original dark-mode hover intent, not a washed-out literal.

### Requirement: Mode-Aware Plotly Charts

Plotly `_layout()` and every chart color — grid color, font color, annotation
`bgcolor`, `paper_bgcolor`, `plot_bgcolor` — MUST derive from the active token
set so charts adapt to the active mode.

#### Scenario: charts follow mode switch

- GIVEN dark mode is active
- WHEN a Plotly figure renders
- THEN grid, paper, plot, annotation `bgcolor`, and font colors all use DARK tokens; toggling to light re-renders them with LIGHT tokens.

### Requirement: Toggle UX via Native Settings

The mode toggle SHALL be Streamlit's native Settings-menu theme toggle only.
The system MUST NOT add a custom toggle widget, theme-picker dropdown, or
`st.toggle`, and MUST NOT persist theme preference beyond Streamlit's native
behavior.

#### Scenario: single native toggle source

- GIVEN the running app
- WHEN the user opens Settings
- THEN exactly one theme control exists (Streamlit's native one); no custom toggle is present.

#### Scenario: toggle returns to light

- GIVEN the app is in dark mode
- WHEN the user toggles back to light in Settings
- THEN all pages, CSS, and charts return to the LIGHT palette with no leftover dark elements.

### Requirement: No Behavior Changes

The change MUST be cosmetic. Core logic, simulation engine, KPIs, analytics,
data flow, page structure, and component layout MUST NOT change. The existing
34/34 tests MUST continue to pass unmodified.

#### Scenario: test suite unaffected

- GIVEN the change applied
- WHEN `python -m pytest tests/ -v` runs
- THEN all 34 tests pass with no test file edits.

#### Scenario: layout unchanged

- GIVEN the tokenized app
- WHEN pages render in either mode
- THEN component structure, spacing, and layout are identical to pre-change — only colors differ.