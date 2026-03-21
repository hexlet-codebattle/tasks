# Repository Guidelines

## Source of Truth
- Use `ai/project_structure.md` for task placement and naming rules.
- Use `ai/task_structure.md` for the canonical TOML schema, field semantics, and allowed type signatures.
- Use `ai/task_example.toml` as the formatting and ordering reference when creating or editing tasks.
- If this file conflicts with the `ai/` docs, follow the `ai/` docs.

## Project Structure
- All tasks live under `tasks/`.
- There are 4 task levels: `elementary`, `easy`, `medium`, `hard`.
- Every task must have a unique `name`.
- Every task has a `tags` array of strings.
- The path for each task must be `tasks/<level>/<tags[0]>/<name>.toml`.
- `preview/` contains the local React/Vite preview app.
- Root scripts such as `test_solutions.py`, `check_task_names.py`, and `push_tasks.py` handle validation and publishing.
- `release/` and `release.tar.gz` are generated build artifacts; do not edit them manually.

## Build And Validation
- `make check-names` verifies task-name uniqueness and filename alignment.
- `python test_solutions.py tasks` validates all public tasks by parsing TOML, running `solution`, and checking `[[asserts]]`.
- `make build` runs name checks, rebuilds `release/`, and validates public tasks.
- `make preview` installs preview dependencies and starts the local UI.
- `make build-and-preview` builds first, then starts the preview app.

## Task Authoring Rules
- Required fields: `name`, `description_en`, `description_ru`, `input_signature`, `output_signature`, `asserts`, `examples`, `solution`, `level`, `tags`, `time_to_solve_sec`.
- Optional fields: `limits`, `comment`.
- Keep field order aligned with `ai/task_example.toml`.
- `name` must be English and `snake_case`; the filename must match it exactly.
- `description_en` and `description_ru` are Markdown strings rendered with math support; keep them concise.
- Wrap mathematical notation in LaTeX using `$...$` or `$$...$$`.
- `limits`, when present, should be a Markdown list of constraints using math notation only, without prose.
- `examples` must be a fenced-style assertion block as a string, sorted by line length from shortest to longest.
- `solution` must define `solution(...)`, stay concise, and avoid unnecessary imports or boilerplate.
- `tags` may be empty, but when non-empty the first tag determines the directory name in the task path.

## Signatures And Types
- `input_signature` is an array of arguments, each with `argument_name` and a `type` object.
- `output_signature` is an object containing a `type` object.
- Only use types allowed by `ai/task_structure.md`.
- Primitive names are `string`, `boolean`, `integer`, `float`, `array`, and `hash`.
- Nested container types must follow the documented `nested` structure exactly.

## Tests And Examples
- Put validation cases in `[[asserts]]`.
- Each assert must provide `arguments` in `input_signature` order and an `expected` value.
- Optional assert `comment` values should be short and in English.
- Cover edge cases, extreme values, and algorithmic corner cases.
- Prefer realistic and varied test data over repetitive cases.
- Recommended coverage is about 25-30 asserts per task.
- All string data in asserts should be English.

## Difficulty And Timing
- `elementary`: target a 1-2 line solution.
- `easy`: target a 2-6 line solution.
- `medium`: target a 7-11 line solution.
- `hard`: target a 12+ line solution.
- Set `time_to_solve_sec` consistently with the project guidance documented in `ai/task_structure.md`.

## Style Notes
- Follow existing Python style in repository scripts: 4-space indentation and conventional import ordering.
- If formatting TOML, preserve the aligned style used in `ai/task_example.toml` and repository task files.
- Keep task text concise; avoid extra notes unless they materially clarify the contract.

## Commit And PR Notes
- Use short, imperative commit messages.
- In PRs, list created or changed tasks and note the validation commands you ran.
- Include preview screenshots only for UI changes under `preview/`.
