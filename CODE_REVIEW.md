# Terminally Simple — Full Code Review

**Commit:** `544a077` ("Implement Pomodoro timer feature … (STILL NEEDS DEBUGING)")
**Stack:** Python + [Textual](https://textual.textualize.io/) (TUI), `httpx` (Open-Meteo API),
`psutil` (CPU/RAM header)
**Scope:** every file in the repo, plus behavioural verification by actually running the app
headless (`App.run_test()`), running the existing test suite, `ruff`, `mypy`, and exercising the
real Open-Meteo API. No source file was modified for this review.

---

## 0. How this was verified

| Check | Result |
|---|---|
| `App.run_test()` smoke test | App mounts, all 4 screens open — works on Textual **8.2.8** |
| `pytest` on the repo | **crashes** with `INTERNALERROR` (tests are scripts calling `sys.exit()` at import) |
| `ruff check .` (0.17.3) | **583 errors** (474 × W293) + deprecated `[tool.ruff]` layout |
| `mypy .` (1.19) | 24 errors, incl. `python_version "3.8" is not supported` |
| `pip install -e .` | **fails** — invalid `[tool.setuptools] packages = ["."]` |
| `pip install -e ".[dev]"` | **fails** — `pytest-textual` does not exist on PyPI |
| Real Open-Meteo call | works, but hourly forecast is timezone-broken (P0-5) |
| Type-then-quit test | **unsaved editor content is silently lost** (P0-1) |

---

## 1. TL;DR — top priority

| # | Prio | Issue | Why it matters |
|---|---|---|---|
| 1 | **P0** | Unsaved editor content **lost on quit/crash** | Data loss; the "final autosave on unmount" throws every time |
| 2 | **P0** | `notes/` lives **inside the package directory** | Breaks/`PermissionError` for any `pipx` install; notes commit themselves into the repo |
| 3 | **P0** | Tasks/config writes **non-atomic, silently discard everything** | One truncated write ⇒ all tasks gone, only a log line |
| 4 | **P0** | **`w` / `p` shortcuts dead in the editor** | README's headline claim ("press `w` anywhere") is false on the main screen |
| 5 | **P0** | Forecast filtered with **device timezone, not city timezone** | Tokyo shows forecasts that already happened |
| 6 | **P1** | Pomodoro/weather state **per-screen**, not per-app | Timer silently resets on navigation; several timers tick at once |
| 7 | **P1** | Theme "preview" **persists immediately** | `Esc` doesn't undo the preview; Settings lies about it |
| 8 | **P1** | Header **breaks on emoji / narrow terminals** (manual `len()` padding) | Overflows below ~80 cols, clock disappears |
| 9 | **P1** | Tests aren't tests + **no CI** | `pytest` can't even collect; no regression guard |
| 10 | **P1** | Packaging broken (`pip install .`, `pytest-textual`, `requires-python>=3.8`) | Announced install path + console script don't work |

---

## 2. P0 — correctness bugs (evidence attached)

### P0-1. Unsaved work is lost on quit

```python
# editor.py
def on_unmount(self) -> None:
    # Perform final autosave before unmounting (always try to save)
    try:
        self._autosave()
    except Exception as e:
        logger.error(f"Failed to autosave on unmount: {e}")
```

`_autosave()` starts with `query_one("#text-area")`, but by the time `on_unmount` runs the screen's
DOM is already detached — so the "final save" never saves. Typed text, then `app.exit()`
(same path as `Ctrl+C` / closing the terminal):

```
is_modified: True   current_file: None
autosave file exists: False | content: None
ERROR:editor:Failed to autosave on unmount: No nodes match '#text-area' on EditorScreen()
```

So **type → quit within the 30 s autosave window → text is gone**, and quitting is not guarded by a
confirmation (only `Esc` on `EditorScreen` is). `Ctrl+C` / `q` bypass everything.

Fix: keep a reference to the `TextArea` (or cache `text` on `TextArea.Changed`), persist from
`App.on_shutdown` / `Screen.on_screen_suspend`, and add a single global "unsaved work — quit
anyway?" gate.

### P0-2. `notes/` is inside the package directory

```python
# editor.py
self.documents_dir = Path(__file__).parent / "notes"
self.documents_dir.mkdir(parents=True, exist_ok=True)
```

* For a wheel/`pipx` install this is `…/site-packages/notes` → **read-only** ⇒ `PermissionError`
  in `EditorScreen.__init__`, i.e. the editor never opens.
* The repo ships a user file: `notes/asdasdasd.md` = `sdjfhsdhjfsdhujf`.
* `.gitignore` only ignores `notes/.autosave/`, so every real note is one `git add .` away from
  being published.

Fix: `platformdirs.user_documents_dir() / "Terminally Simple"` (fallback
`user_data_dir`), configurable, created lazily, plus a migration for the old `notes/`.

### P0-3. Non-atomic persistence ⇒ silent total data loss

```python
# tasks.py
with open(self.tasks_file, 'w') as f:       # truncates first
    json.dump([t.to_dict() for t in tasks], f, indent=2)
...
except (json.JSONDecodeError, KeyError) as e:
    logger.error(f"Error loading tasks: {e}")
    return []                               # ← the whole list is gone, silently
```

Verified with a truncated file and with one legacy record missing `id`:

```
Error loading tasks: 'id'
Error loading tasks: Expecting ',' delimiter: line 1 column 31 (char 30)
loaded with missing key -> []
loaded from truncated file -> []
```

`config.py` has the same shape (`_load` → defaults, `save()` writes per file) and there is no file
lock, so two terminals = last-writer-wins.

Fix: `*.tmp` + `os.replace()` + `*.bak`; validate per record so one bad entry doesn't drop the list;
`notify(severity="error")` when data had to be discarded.

### P0-4. `w` / `p` shortcuts don't work where the user is

`TerminallySimple.BINDINGS` are non-priority, so the focused `TextArea`/`Input` consumes the key
first:

```
after 'p' in editor -> screen: EditorScreen | textarea text = 'pTest content…'
after 'w' in editor -> screen: EditorScreen | textarea text = 'pwTest content…'
```

The same applies to any screen with an `Input` open. The README claims *"Press `w` anywhere"*.

Fix: priority chords (`ctrl+w`, `ctrl+p`) or a leader key, and make them configurable in Settings —
which is exactly requested feature #1 in the README.

### P0-5. Forecast filtered with the wrong timezone

```python
# utils/weather.py
forecast_time = datetime.fromisoformat(time_str)   # city-local, naive
current_time = datetime.now()                      # device-local
if forecast_time > current_time: ...
```

The request uses `timezone=auto`, so `hourly.time` is in the **city's** zone. Verified:

```
local now: 2026-11-01 11:44 UTC
Tokyo, Japan: api tz=Asia/Tokyo, first api hour=2026-11-01T00:00
  parsed: [('12:00', 19.6), ('13:00', 20.0), ('14:00', 20.2)]   # Tokyo local time is 20:44
```

A Tokyo user sees hours that already passed and misses the next 8 hours (the list is capped at
`hours=24` counted from the wrong origin). `data["timezone"]` / `utc_offset_seconds` are ignored.

Fix: `zoneinfo.ZoneInfo(data["timezone"])`, or slice relative to the API's own `current.time`.



---

## 3. P1 — high-impact issues

### P1-6. App state is stored inside widgets that get thrown away

`WeatherWidget` / `PomodoroWidget` are **never mounted**: `SystemHeader.compose()` instantiates them
but only yields `Static(id="header-content")`.

```
header children: ['Static']
#weather-widget  NOT MOUNTED (widget object exists but is not in the DOM): True True
#pomodoro-widget NOT MOUNTED (widget object exists but is not in the DOM): True True
```

Consequences:
* The header re-implements rendering by calling `widget.render()` by hand and pasting the markup into
  a `Text` — two rendering paths, no CSS, no `:hover`.
* Click handling is a **coordinate heuristic** (`click_x > width * 0.85` ⇒ weather, `> 0.55` ⇒
  pomodoro). On narrow terminals clicking CPU/RAM opens the weather dialog.
* Every screen composes a *new* `SystemHeader`, so Pomodoro state is duplicated per screen:

```
MainMenu header  remaining: 1499 running: True
Editor   header  remaining: 1500 running: False     ← timer "vanished"
back to MainMenu remaining: 1497 running: True      ← old one still ticking, invisible
```

* Every screen mount fires its own weather request (two SSL/fetch errors logged during that run),
  because state and cache live per widget and only in memory.

Fix: move session state (pomodoro clock, weather) into a small app-level service
(`TerminallySimple.services` / a `PomodoroModel` with reactive attributes) and make the header a
pure view; mount the real `WeatherWidget`/`PomodoroWidget` inside a `Horizontal` so CSS + `on_click`
work normally.

### P1-7. Theme "preview" is saved instantly — `Esc` cannot undo it

`SettingsScreen._toggle_option()` sets `self.app.theme = …`, and `TerminallySimple.watch_theme()`
writes the config straight away:

```
theme after preview (not saved): nord
config on disk after preview: {"theme": "nord", …}
theme after escape: nord
config on disk after escape: {"theme": "nord", …}
```

So the "Preview: … (press 's' to save)" message is misleading, `action_back()`'s
`apply_theme_from_config()` restores the *already-overwritten* value, and `r` (reset) can't help
either. Also `apply_theme_from_config()`'s try/except means an unknown theme silently becomes
`textual-dark` while config keeps the bad value.

Fix: keep a `self._pending_theme`, only write `config` in `action_save()`; make `watch_theme`
persist only when a flag `self._persist_theme` is true (or drop the watcher entirely and save
explicitly).

### P1-8. Header layout math is broken for emoji and narrow terminals

`_update_display()` pads with `len()` and `total_width = self.size.width`:

```
120x40: header cells=116 (screen width 120)
 80x24: header cells= 76 (screen width 80)
 60x20: header cells= 65 (screen width 60)   ← 5 cells of overflow
 40x15: header cells= 65 (screen width 40)   ← 25 cells clipped, clock gone
 25x10: header cells= 65 (screen width 25)
```

`len("🍅 25:00") == 7` but `cell_len("🍅 25:00") == 8` (wide glyphs), so the right-hand block drifts
one column per emoji. Multi-byte/CJK city names make it worse.

Fix: don't hand-pad. Use a `Horizontal` header with three children
(`dock: left` / `width: 1fr; text-align: center` / `dock: right`) and let Textual lay it out; if you
must measure, use `rich.cells.cell_len`. Hide the clock/weather below a width threshold.

### P1-9. The test suite is not a test suite

* `tests/*.py` are **scripts** with `print` + `sys.exit(1)` at import time ⇒ `pytest` dies:
  `INTERNALERROR … File "tests/test_autosave_recovery.py", line 23 … SystemExit: 1`.
* They test *implementation details* (`hasattr(cls, 'action_show_weather')`, `'ctrl+a' in
  [b.key …]`) instead of behaviour, and they write into the repo (`tests/notes/…`).
* `test_pomodoro.py` / `test_weather_keyboard.py` still sit in the repo root (outside `testpaths`).
* `test_weather_api.py` is a network script declared as `async def test_weather()` — pytest would try
  to run it as a sync test.
* No `conftest.py`; and since `config = Config()` runs at **import** time and touches
  `Path.home()`, tests can't be isolated without monkeypatching `HOME`.

Fix: `pytest-asyncio` with `asyncio_mode = "auto"`, `conftest.py` fixture that points
`XDG_CONFIG_HOME`/`HOME` at `tmp_path` **before** importing the modules, real `async with
app.run_test()` tests (keys, screens, persistence), and `pytest-textual-snapshot` for the header /
dialog visuals.

### P1-10. Packaging and metadata are broken

```
$ pip install --no-build-isolation --no-deps -e .
configuration error: `tool.setuptools.packages` must be valid exactly by one definition (0 matches)
```

* `packages = ["."]` is invalid; `py-modules` omits `tasks`, `base_screen`, `utils`, `widgets`,
  `dialogs` — so even with a valid config, `terminallysimple = "app:main"` would ship a half package.
* `pytest-textual` (dev extra) **does not exist on PyPI** → `pip install -e ".[dev]"` fails
  (the real package is `pytest-textual-snapshot`).
* `requires-python = ">=3.8"` + `Programming Language :: Python :: 3.8` but the code uses PEP 585
  generics (`list[Widget]`, `dict[str, Any]`, …28 occurrences) with **no**
  `from __future__ import annotations` ⇒ `TypeError` at import on 3.8. Textual 8 itself requires
  ≥3.9, and current `mypy` refuses 3.8.
* `textual>=0.41.0` is not honest either: `App.theme` / theme registry only landed in **0.86.0**
  (Textual CHANGELOG, PR #5087), so 0.41–0.85 installs give a Settings screen that does nothing.
* No `__main__.py` ⇒ `python -m terminallysimple` unsupported; no `py.typed`; no lockfile even though
  the README pushes `uv`.
* Flat layout at repo root means `import app` shadows/conflicts with anything named `app`.

Fix: move to `src/terminallysimple/`, hatchling (like `posting`/`toolong`), `requires-python =
">=3.9"` (better: `>=3.10`), `textual>=0.86` (or pin `>=2,<9`), correct dev extras, `uv.lock`,
`__main__.py`, `py.typed`.

---

## 4. P2 — medium issues / correctness nits

**Editor**
* `action_save()` **overwrites an existing note without asking** (verified: `PRECIOUS DATA` →
  `new content`). `action_rename()` does check `new_file_path.exists()` — inconsistent.
* Save always rewrites the extension to `.md`, so a `.txt` file silently becomes `.md` on "Save As".
* Autosave recovery is **silent and sticky**: any `notes/.autosave/untitled-autosave.md` left behind
  (e.g. by the repo's own scripts) is auto-loaded into the next session with `is_modified = True`
  and never removed. Verified — a fresh editor opened with `Test content from new file…` from a
  previous run. Should prompt ("Recover previous session? y/n") and clean up on discard.
* `_autosave()` swallows "text area not accessible" and skips — fine, but combined with P0-1 it
  means the *only* safety net is the 30 s timer.
* `FilenamePrompt` says "Alphanumeric, spaces, hyphens, underscores only" but `sanitize_filename`
  accepts any printable char ⇒ doc/behaviour mismatch.
* Typing `Ctrl+A` (priority binding) replaces `TextArea`'s own select-all; harmless but duplicated.
* No find/replace, no markdown preview, no word count, no "reopen last file", no cursor restore.
  `TextArea(language="markdown")` + `textual[syntax]` would give highlighting for free.
* `on_text_area_changed` writes the status bar on every keystroke (minor redraw churn).

**Tasks**
* `Task.id` falls back to `id(self)` (memory address) when not supplied — unstable, and
  `Task.from_dict` requires the `id` key, so older/hand-edited files nuke the list (P0-3).
* No filtering, sorting, priorities, due dates, tags, or undo for delete/clear.
* `c` (clear completed) reuses `ConfirmDeleteDialog` with a sentence, so the dialog renders as
  `DELETE TASK` → "Delete this task? Clear 3 completed task(s)?".
* Reordering refocuses via `set_timer(0.01, …)` — the same timing hack as initial focus
  (`FOCUS_TIMER_DELAY`); `call_after_refresh`/`await mount` is the supported way.

**Weather**
* In-memory cache is **global, not keyed by coordinates** → after changing city, `use_cache=True`
  can return the previous city's payload for up to 30 min.
* No disk cache ⇒ a network call on every screen mount and every app start; offline = header shows
  the plain "Weather" label, no error state, no "last updated".
* °C hard-coded in the dialog (`{temp:.0f}°C`), no unit switch; `current_units` from the API ignored.
* Only 24 h hourly, sampled every 4 h (6 rows). No daily forecast, no apparent temperature, wind,
  precipitation probability — all available from the same Open-Meteo call.
* A new `httpx.AsyncClient` per request; no retry/backoff, no `User-Agent`, no cancellable timeout
  budget shared between geocode + forecast.
* `get_weather_icon()` lumps drizzle/rain/snow-showers together (`range(51, 68)`); the WMO table in
  the docstring is not fully honoured.

**Pomodoro**
* Counts down with a 1 s `set_interval` ⇒ drifts, and stops when the event loop sleeps/suspends.
  Derive from a monotonic deadline instead.
* All timings are hard-coded constants scattered in `system_header.py` (25/5/15, every 4 cycles) —
  no settings, no persistence across restarts, no session history/stats, no bell
  (`app.bell()`) / desktop notification.
* Dialog polls the parent every 100 ms instead of reacting to a message.
* Docs (`POMODORO_FEATURE.md`) describe a different UI ("Inactive: `[dim]Pomodoro[/]`", left side)
  than the code (`⏹ MM:SS`, right side).

**App / infra**
* `action_show_weather` / `action_show_pomodoro` wrap everything in `except Exception: pass`
  (Pomodoro silently does nothing if no header is present).
* Weather setup logic is duplicated **verbatim** in `app.py` (`_setup_weather_async`,
  `_refresh_and_show_weather`) **and** `widgets/system_header.py` (`_setup_weather_async`,
  `_refresh_and_reopen_forecast`) — ~120 duplicated lines, plus the "every 4th hour" filter
  copy-pasted 3×.
* `logging.FileHandler` with no rotation — `~/.config/terminallysimple/app.log` grows forever.
* No CLI: no `--version`, `--help`, `--notes-dir`, `--no-weather`, `--log-level`.
* Config/tasks/log paths are hard-coded `Path.home()/".config"` ⇒ non-standard on Windows/macOS
  (README claims cross-platform). Use `platformdirs`.
* `config = Config()` at import time creates directories as a side effect of importing — untestable
  and surprising.
* `ruff` config uses the removed top-level `select`/`ignore`/`per-file-ignores` (0.17 warns;
  move under `[tool.ruff.lint]`), plus 474 × W293 (trailing whitespace on blank lines) and 49
  unused imports.
* `mypy` is configured (`python_version = "3.8"`, unsupported) but never run; real typing errors are
  hidden: `old_file_path.rename(...)` where `old_file_path` is `Path | None`, `PomodoroDialog`
  assigning a `Timer` to a `None`-typed attr, incompatible `action_dismiss` overrides.
* `psutil.cpu_percent(interval=None)` returns `0.0` on the first call ⇒ header shows `CPU: 0%` for a
  second (cosmetic, but a one-line prime fixes it).

---

## 5. Architecture & refactoring opportunities

1. **Kill the hand-rolled navigation layer.** `NavigableMixin` + `MenuItem`/`SettingOption`/
   `FileItem` + `FOCUS_INDICATOR` prefixes re-implement focus handling Textual already provides. The
   idiomatic replacements are theme-aware and come with scrolling/mouse parity:
   * main menu → `OptionList` (or `ListView`)
   * settings → `OptionList` (or `Select`/`Switch` per option)
   * task list → `ListView`
   * file browser → `DirectoryTree` (or `OptionList` fed from a `Path`)
   That deletes ~200 lines of `on_focus`/`on_blur`/`refresh`/`set_timer(0.01)` glue.
2. **Services, not widget state.** One `PomodoroService` (monotonic deadline, reactive state) and one
   `WeatherService` (shared httpx client, disk cache) owned by `App`; screens subscribe. Fixes P1-6,
   the duplicate network calls, and makes tests trivial.
3. **Layout by CSS, not string math.** Move the `CSS = """…"""` class attributes into `*.tcss` files
   (`CSS_PATH`); Textual's dev tooling (`textual run --dev`, live CSS reload) only works properly
   there, and it would have made P1-8 obvious.
4. **One storage helper.** `store.py` with `load_json(path, default)`, `save_json_atomic(path,
   data)`, a schema `version` and `migrate()`, used by `Config`, `TaskStorage` and the weather cache.
   Plus `platformdirs` for paths.
5. **One confirm dialog.** It is implemented 4× (`editor.ConfirmDialog`,
   `ConfirmDeleteFileDialog`, `tasks.ConfirmDeleteDialog`, `PomodoroDialog`); keep a single
   `Confirm` modal that returns via `dismiss()`.
6. **Errors belong in the UI.** Replace `except Exception: pass` with narrow exceptions
   (`NoMatches`, `httpx.HTTPError`, `OSError`), `logger.exception` for tracebacks and
   `self.notify(..., severity="error")` for the user.
7. **Type everything, ship `py.typed`**, then flip `disallow_untyped_defs = true` and run `mypy` in
   CI.

---

## 6. Documentation accuracy

`README.md`
* "Press `w` anywhere" / "Press `p` anywhere" — false in the editor (P0-4).
* "Files saved to `notes/` folder" — will change with P0-2.
* "11 Beautiful Themes" — Textual 8 ships 21, hard-coded list drifts.
* "python-3.8+" badge — the code cannot run on 3.8.
* The only install path that works is `pip install -r requirements.txt && python app.py`; the
  `terminallysimple` console script and `pip install .` are broken.

`CONTRIBUTING.md` — clones `https://github.com/yourusername/terminallysimple.git` (placeholder);
asks for `black`/`ruff` while the repo is not ruff-clean; never mentions tests (there are none usable).

`RELEASE_READY.md` — claims "Moved development docs to `docs/`" (no `docs/`), "Moved test files to
`tests/`" (two still in root), references a non-existent `REVIEW_AND_RECOMMENDATIONS.md`, and calls
the release "ready" while `pip install .` fails.

`POMODORO_FEATURE.md`, `WEATHER_KEYBOARD_FEATURE.md` — implementation scratch notes describing a UI
that no longer matches the code; `POMODORO_FEATURE.md` claims "All tests pass" while the last commit
says "STILL NEEDS DEBUGING". Move to `docs/` (or delete); keep `CHANGELOG.md` as the single source of
truth.

`CHANGELOG.md` — `[0.1.0]` dated 2025-10-29 but `pyproject.toml` still `version = "0.1.0"` and no
tag exists; `[Unreleased]` is stale.

Also missing: `SECURITY.md`, a real `docs/`, locally-hosted screenshots (the README depends on an
external imgur album), `.github/pull_request_template.md`, `dependabot.yml`.

---

## 7. Testing & CI — concrete plan

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```
```python
# tests/conftest.py  — must set env BEFORE the app package is imported
import os, pytest
from pathlib import Path

@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
    monkeypatch.chdir(tmp_path)
    yield tmp_path
```
```python
# tests/test_editor.py
import pytest
from textual.widgets import TextArea
from terminallysimple.app import TerminallySimple

async def test_typed_text_survives_quit(isolated_home):
    app = TerminallySimple()
    async with app.run_test() as pilot:
        await pilot.press("1")
        editor = app.screen
        editor.query_one(TextArea).load_text("hello")
        await pilot.pause()
    assert "hello" in Path("notes/.autosave/untitled-autosave.md").read_text()
```

Coverage targets worth having (all currently unverified):
`EditorScreen` save/open/rename/delete + autosave recovery prompt · `TaskStorage` atomicity &
corrupt-file handling · pomodoro tick/complete maths (inject a clock) · weather parsers on **recorded
JSON fixtures** (no network in CI) · theme apply/undo · every screen reachable by keyboard ·
`pytest-textual-snapshot` for the header at 120/80/40 columns.

`.github/workflows/ci.yml` (nothing exists today — no workflow directory at all):

```yaml
name: ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python: ["3.10", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync --all-extras
      - run: uv run ruff check . && uv run ruff format --check .
      - run: uv run mypy src
      - run: uv run pytest --cov --cov-report=term-missing
```

Plus `pre-commit` (ruff, ruff-format, mypy, end-of-file-fixer) and `dependabot.yml`.

---

## 8. Features worth building next (what comparable apps do)

Borrowed from Textual's own docs/examples and from mature Textual apps —
`Textualize/toolong`, `darrenburns/posting`, `davep/hike`, `harlequin`:

**Keyboard & navigation**
* Re-enable the **command palette** (`ENABLE_COMMAND_PALETTE = False` today) and register
  `SystemCommand`s — posting/toolong use it as the discoverability layer; it directly serves the
  "keyboard-first, mouse optional" goal.
* A single `?` help screen with the real keymap (generated from `BINDINGS`), like `toolong`'s `help.py`.
* Configurable/leader-based shortcuts, stored in config (README's requested feature #1).

**Editor**
* `Ctrl+F` find (+ replace), `Ctrl+G` go-to-line, `Ctrl+K` delete line — `TextArea` already exposes
  the primitives.
* Markdown syntax highlighting via `TextArea(language="markdown")` + `textual[syntax]`, and a
  `Markdown` preview split (`hike` is the reference implementation).
* Reopen last file / restore cursor + scroll position; word/char count in the status bar.
* Export to PDF/HTML (`Ctrl+E`) — small, high-value for a notes app.

**Tasks**
* Due dates, priority, tags + filter view (`DataTable` or a `TabbedContent` of Today/All/Done).
* Undo (`Ctrl+Z`) instead of a modal for every delete — much faster to use.
* Recurring tasks and a small "stats" footer (done today / streak).

**Weather**
* Daily forecast tab, `apparent_temperature`, wind, precipitation probability (same API call).
* Units toggle (°C/°F, km/h vs mph) in Settings, plus a `--units` flag.
* On-disk cache + "last updated" + stale-data banner; `--offline` mode.
* Optional geolocation by IP (`https://ipapi.co/json`, opt-in) so first-run needs no typing.

**Pomodoro**
* Durations/auto-start/notifications in Settings; persist the running session across restarts.
* `app.bell()` on completion + OSC-9 desktop notification fallback.
* Daily stats (sessions, focus minutes) written next to tasks.

**Distribution**
* `pipx install terminallysimple` (needs P1-10), `docker run` image, Homebrew tap formula —
  `toolong` and `posting` both ship these and it is the single biggest adoption lever for a TUI.
* `terminallysimple --version`, `--notes-dir`, `--no-weather`, `--log-level`.

---

## 9. Suggested execution order (the answer to "what should we fix first")

**Sprint 1 — stop losing data (P0).** All small, contained diffs, huge user impact:
1. Fix autosave-on-unmount (cache the `TextArea`), save from `App.on_shutdown`, and refuse to quit
   with unsaved changes (P0-1).
2. Move `notes/` to `platformdirs` user documents, migrate old files, `git rm notes/asdasdasd.md`,
   ignore `notes/` (P0-2).
3. Atomic JSON writes + per-record tolerance + `*.bak` for tasks & config (P0-3).
4. Confirm before overwriting an existing note on save (P0-2b).

**Sprint 2 — make the app honest about itself.**
5. Make `w`/`p` (or `ctrl+w`/`ctrl+p`) real *priority* shortcuts, document the true keymap, add a `?`
   help screen (P0-4).
6. Fix the forecast timezone with `zoneinfo`/`current.time` (P0-5).
7. Make theme preview non-destructive; `Esc` must restore (P1-7).
8. Fix the header layout (`Horizontal` + `cell_len`, hide clock below N columns) (P1-8).

**Sprint 3 — make it testable and installable.**
9. Convert `tests/` to real pytest + `pytest-asyncio` + `conftest.py` that isolates `HOME`; delete the
   root-level scripts; add snapshot tests (P1-9).
10. Fix packaging: `src/terminallysimple/`, hatchling, valid deps, `requires-python >=3.10`,
    `textual>=0.86`, replace `pytest-textual` with `pytest-textual-snapshot`, add `__main__.py`,
    `py.typed`, `uv.lock` (P1-10).
11. Add CI: ruff + mypy + pytest on a 3-OS/3-Python matrix, pre-commit, dependabot.

**Sprint 4 — architecture.**
12. Introduce `WeatherService` + `PomodoroService` on `App` (fixes P1-6, duplicate requests, state
    loss on navigation); mount the real widgets and drop the coordinate-hit-test click zones.
13. Collapse the 4 confirm dialogs and the 3 copies of the forecast-filtering code; move CSS to
    `.tcss` files.
14. Replace hand-rolled focus lists with `OptionList`/`ListView`/`DirectoryTree`.

**Sprint 5 — polish & growth.**
15. Settings beyond themes: units (°C/°F), keymap, autosave interval, weather refresh, pomodoro
    durations; command palette back on.
16. Editor: find/replace, markdown highlight/preview, restore last file; Tasks: undo, due dates,
    filter; Weather: daily forecast + disk cache + offline banner; Pomodoro: persist session, bell,
    stats.
17. Docs truth pass (README/CONTRIBUTING/RELEASE_READY/feature notes), `SECURITY.md`, screenshots in
    the repo, `pipx` + Homebrew distribution.

**Cheap wins that can ship any day:** kill the 474 trailing-whitespace / 49 unused-import ruff
findings (`ruff check --fix` + `ruff format`) and move the ruff config under `[tool.ruff.lint]`;
add `RotatingFileHandler`; prime `psutil.cpu_percent`; delete the duplicated weather code in
`app.py`.

