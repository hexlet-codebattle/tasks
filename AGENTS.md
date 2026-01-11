# Repository Guidelines

## Project Structure & Module Organization
- `tasks/` stores public tasks as `.toml` by difficulty (`elementary/`, `easy/`, `medium/`, `hard/`).
- Each task file path must be `tasks/<level>/<tags[0]>/<name>.toml` (and the same layout in `private/`).
- `preview/` contains the React/Vite web preview (`preview/src/`, `preview/server.mjs`).
- Root-level Python scripts (`test_solutions.py`, `check_task_names.py`, `push_tasks.py`) automate validation and publishing.
- `release/` is generated output (JSON artifacts); `release.tar.gz` is a packaged release.

## Build, Test, and Development Commands
- `make build` runs name checks then validates tasks and emits JSON to `release/`.
- `make preview` installs preview deps and runs the local UI at `http://localhost:5173`.
- `make build-and-preview` builds tasks and launches the preview app.
- `python test_solutions.py tasks` runs the task solution test runner directly.
- `make check-names` checks TOML `name` uniqueness and filename alignment.

## Coding Style & Naming Conventions
- `name` is required, English, and `snake_case`; file names must match `name` exactly and be unique case-insensitively.
- Follow the task spec in `ai/task_structure.md` and the sample `ai/task_example.toml` for field order.
- If formatting TOML, use Taplo settings from `taplo.toml` (aligned entries and key reordering).
- For Python scripts, match existing 4-space indentation and import ordering.

## Testing Guidelines
- Task validation is executed via `test_solutions.py`; it parses TOML, runs `solution`, and verifies `[[asserts]]`.
- Test cases live in each task file under `[[asserts]]`; include edge cases, extreme values, and failure-prone inputs.
- Aim for 25–30 asserts per task; all string data in asserts must be English.
- Keep `examples` as assertion lines sorted by string length (shortest first).
- When adding tasks, run `make build` or `python test_solutions.py tasks` before submitting.

## Task Format Essentials
- Required fields: `name`, `description_en`, `description_ru`, `input_signature`, `output_signature`, `asserts`, `examples`, `solution`, `level`, `tags`, `time_to_solve_sec`.
- `description_*` uses Markdown with LaTeX (`$...$`/`$$...$$`); keep text concise.
- `level` maps to expected solution length: elementary (1–2 lines), easy (2–6), medium (7–11), hard (12+).
- `time_to_solve_sec` follows project guidance (elementary 100–200, easy 200–300, medium 300–600, hard 600–90 as specified).
- Use only allowed types from `ai/task_structure.md` for signatures.

## Commit & Pull Request Guidelines
- Recent history uses short, imperative summaries (e.g., “Fix env”). Keep messages concise and action-oriented.
- PRs should describe the change, list new/updated tasks, and note any command output used for validation.
- Include preview screenshots only when UI changes are made under `preview/`.

## Configuration & Release Notes
- Python dependencies live in `requirements.txt`; preview uses `pnpm` in `preview/`.
- Generated files in `release/` are build artifacts; do not hand-edit them.
