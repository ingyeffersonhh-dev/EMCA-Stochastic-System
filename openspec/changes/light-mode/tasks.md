# Tasks: Light/Dark Mode Toggle for EMCA UI

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~540 (additions + deletions) |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 (foundation ~300) -> PR 2 (main + small pages ~104) -> PR 3 (heavy pages ~135) |
| Delivery strategy | ask-always |
| Chain strategy | feature-branch-chain |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Token system + tests + config | PR 1 | base: main; ~300 lines; tests with code per work-unit-commits |
| 2 | main.py CSS tokenization + small pages (00, 02) | PR 2 | base: PR 1 branch; ~104 lines |
| 3 | Heavy pages: 03_dashboard, 04_comparacion, 01_parametrizacion | PR 3 | base: PR 2 branch; ~135 lines; completes static test |

> **STOP**: Forecast exceeds 400 lines. With `ask-always` delivery strategy, the orchestrator MUST ask the user which chain strategy to use before proceeding to `sdd-apply`.

## Phase 1: Foundation (TDD RED -> GREEN)

- [x] **1.1** Create `tests/test_theme.py` (RED). Tests: all 19 token fields present in LIGHT+DARK; `get_tokens("light"/"dark"/"invalid")` returns correct mode; `TX` alias == `TX1`; LIGHT/DARK are independent (not inversions); WCAG AA contrast for TX1/TX2/TX3 x BG/BG2/CARD + GREEN/YELLOW/RED/BLUE/ACC on CARD; `_rgba("#FF0000", 0.5) == "rgba(255,0,0,0.5)"`; static grep asserting zero hardcoded hex/rgba in pages+main (allow `_rgba(` and `rgba(0,0,0,0)`). Files: `tests/test_theme.py`. Deps: none. ~150 lines. Verify: `pytest tests/test_theme.py -v` fails (RED).
- [x] **1.2** Rewrite `app/components/theme.py` (GREEN). Replace 38-line constant module with: `Tokens` frozen dataclass (19 fields + `mode` + `TX` property); `_LIGHT` instance (values from design palette table); `_DARK` instance; `get_tokens(mode)` with `None`/invalid -> light default; `get_active_tokens()` reading `st.context.theme.type`; `_rgba(hex, alpha)` helper. Remove all module-level constants. Files: `app/components/theme.py`. Deps: 1.1. ~128 lines (38 del + 90 add). Verify: token/contrast/`_rgba` tests pass; static test still fails (pages not yet tokenized).
- [x] **1.3** Update `.streamlit/config.toml`. Replace `[theme]` section with `base = "light"`, `font = "sans serif"`, `[theme.light]` (primaryColor, backgroundColor, secondaryBackgroundColor, textColor, borderColor from design), `[theme.dark]` (same fields from design). Keep `[server]` and `[browser]` unchanged. Files: `.streamlit/config.toml`. Deps: 1.2. ~22 lines. Verify: app opens in light mode; native toggle switches palettes.

## Phase 2: Core Consumer — main.py CSS

- [x] **2.1** Update `app/main.py`. Replace static theme imports (lines 22-29) with `from app.components.theme import get_active_tokens, _rgba` + `t = get_active_tokens()`. Convert CSS f-string: all `{bg}` -> `{t.BG}`, `{card}` -> `{t.CARD}`, etc. Replace 28 hardcoded `rgba(76,139,245,.N)` -> `_rgba(t.ACC, N)`, `rgba(0,230,138,.N)` -> `_rgba(t.GREEN, N)`, `rgba(255,107,107,.N)` -> `_rgba(t.RED, N)`, `rgba(77,124,254,.N)` -> `_rgba(t.BLUE, N)`. Replace `#FFFFFF` -> `{t.CARD}`, `#0B0B0F` -> `{t.BG}`, `#00E68A`/`#00CC7A` (logo gradient) -> keep constant or token per open question. Files: `app/main.py`. Deps: 1.2. ~80 lines. Verify: app renders without error; fewer static test failures.

## Phase 3: Page Tokenization

- [x] **3.1** Update `app/pages/00_home.py`. Add `t = get_active_tokens()`; replace 4x `#8892B0` -> `t.TX2` (subtitle line 17, flow-node small text lines 72/74/76). Remove old theme imports. Files: `app/pages/00_home.py`. Deps: 1.2. ~12 lines. Verify: `grep "#8892B0" app/pages/00_home.py` returns 0.
- [x] **3.2** Update `app/pages/02_simulacion.py`. Add `t = get_active_tokens()`; replace `#8892B0` (line 16) + 3x `#A0AEC0` (lines 211/216/225) -> `t.TX2`. Remove old theme imports. Files: `app/pages/02_simulacion.py`. Deps: 1.2. ~12 lines. Verify: `grep "#8892B0|#A0AEC0" app/pages/02_simulacion.py` returns 0.
- [x] **3.3** Update `app/pages/04_comparacion.py`. Add `t = get_active_tokens()`; replace `#7C6FD4` -> `t.PURPLE` (PALETTE line 13); `#8A98B8` -> `t.TX2` (line 18); `rgba(76,139,245,.06/.2)` -> `_rgba(t.ACC, .06/.2)` (line 31); `rgba(245,166,35,.06/.2)` -> `_rgba(t.YELLOW, .06/.2)` (lines 117/126); `rgba(17,30,56,0.8)` -> `_rgba(t.CARD, 0.8)` (line 243); gridcolor `rgba(76,139,245,0.08)` -> `t.GRD` (lines 204/205); replace old ACC/RED/CYN/YEL refs with `t.*`. Keep `rgba(0,0,0,0)` transparent and `#fff` badge text. Files: `app/pages/04_comparacion.py`. Deps: 1.2. ~30 lines. Verify: `grep "#[0-9A-Fa-f]{3,8}" app/pages/04_comparacion.py` returns only `#fff`.
- [x] **3.4** Update `app/pages/03_dashboard.py`. Add `t = get_active_tokens()`; make `_layout()` mode-aware: `font.color=t.TX`, `gridcolor=t.GRD`. Replace: `#8A98B8` -> `t.TX2` (line 36); `rgba(22,22,37,0.7)` -> `_rgba(t.CARD, 0.7)` (line 148); `rgba(22,22,37,0.9)` -> `_rgba(t.CARD, 0.9)` (line 188); `rgba(77,124,254,0.06)` -> `_rgba(t.BLUE, 0.06)` (line 196); `rgba(34,211,238,0.08)` -> `_rgba(t.CYAN, 0.08)` (line 258); `rgba(0,230,138,0.1)` -> `_rgba(t.GREEN, 0.1)` (line 291); `#FF8C42` -> `t.YELLOW` (line 310); `rgba(255,255,255,0.05)` -> `t.GRD` (line 331). Replace all RED/YEL/BLU/ACC/CYN/TX/TX2 constant refs with `t.*`. Keep `rgba(0,0,0,0)` transparent. Files: `app/pages/03_dashboard.py`. Deps: 1.2. ~45 lines. Verify: `grep "#[0-9A-Fa-f]{3,8}" app/pages/03_dashboard.py` returns 0.
- [x] **3.5** Update `app/pages/01_parametrizacion.py` (heaviest). Add `t = get_active_tokens()`. Replace: 15x `#8892B0` -> `t.TX2`; 8x `#E2E8F0` -> `t.TX1`; 3x `#4C8BF5` -> `t.ACC`; 2x `#56B8E8` -> `t.CYAN`; `#00E68A` -> `t.GREEN` (lines 257/325); `#FFD43B` -> `t.YELLOW` (line 257); `#FF6B6B` -> `t.RED` (line 325); `rgba(76,139,245,0.08/0.2/0.06/0.15)` -> `_rgba(t.ACC, N)` (lines 153/163/272/277/296/335); `rgba(86,184,232,0.08/0.2)` -> `_rgba(t.CYAN, N)` (line 158); `rgba(204,30,42,0.08/0.2)` -> `_rgba(t.RED, N)` (line 262); `rgba(255,212,59,0.08/0.2)` -> `_rgba(t.YELLOW, N)` (line 267); `rgba(0,0,0,0.2)` -> `_rgba(t.TX1, 0.06)` (lines 327/365). Remove old theme imports. Files: `app/pages/01_parametrizacion.py`. Deps: 1.2. ~60 lines. Verify: `grep "#[0-9A-Fa-f]{3,8}|rgba\(" app/pages/01_parametrizacion.py` returns 0.

## Phase 4: Verification

- [x] **4.1** Run full test suite: `python -m pytest tests/ -v`. Verify 34 existing tests + new theme tests all pass (34 + N). Files: none. Deps: 1.1-1.2, 2.1, 3.1-3.5. 0 lines. Verify: all green, 0 failures. **DONE — 77 passed, 0 failures.**
- [x] **4.2** Static grep audit: grep `app/pages/*.py` + `app/main.py` for `#[0-9A-Fa-f]{3,8}` and raw `rgba(` (exclude `_rgba(` calls and `rgba(0,0,0,0)` transparent). Confirm zero matches bypass the token hub. Files: none. Deps: 3.1-3.5. 0 lines. Verify: zero hardcoded color matches remaining. **DONE — only logo gradient (#00E68A/#00CC7A) remains, allow-listed in tests.**
