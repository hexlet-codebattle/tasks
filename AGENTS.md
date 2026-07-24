# Repository Guidelines

## Source of Truth
- Use `ai/project_structure.md` for task placement and naming rules.
- Use `ai/task_structure.md` for the canonical TOML schema, field semantics, and allowed type signatures.
- Use `ai/task_example.toml` as the formatting and ordering reference when creating or editing tasks.
- If this file conflicts with the `ai/` docs, follow the `ai/` docs.

## Project Structure
- Public tasks live under `tasks/`; hidden/private tasks live under `private/`.
- There are 4 task levels: `elementary`, `easy`, `medium`, `hard`.
- Every task must have a unique `name`.
- Every task has a `tags` array of strings.
- Public task paths must be `tasks/<level>/<tags[0]>/<name>.toml`.
- Private task paths must be `private/<level>/<tags[0]>/<name>.toml`.
- Public pack definitions live in `task_packs/`; private pack definitions live in `private/task_packs/`.
- `preview/` contains the local React/Vite preview app.
- Root scripts such as `test_solutions.py`, `check_task_names.py`, and `push_tasks.py` handle validation and publishing.
- `release/` and `release.tar.gz` are generated build artifacts; do not edit them manually.

## Build And Validation
- `make check-names` verifies task-name uniqueness and filename alignment.
- `make check-limits` verifies `base_score` and `time_to_solve_sec` do not exceed the maximum allowed for each level.
- `python3 test_solutions.py tasks` validates all public tasks by parsing TOML, running `solution`, and checking `[[asserts]]`.
- `python3 test_solutions.py private` validates private tasks without first clearing `release/`.
- `make build` runs name and limit checks, rebuilds `release/`, and validates public tasks.
- `make build-private` clears `release/` and rebuilds it from private tasks only. Run `make check-names` and `make check-limits` separately before it.
- `make preview` installs preview dependencies and starts the local UI.
- `make build-and-preview` always builds public tasks. To preview private tasks, run `make build-private` followed by `make preview`.
- With pnpm 11, keep `allowBuilds.esbuild: true` in `preview/pnpm-workspace.yaml`; never commit the local `.pnpm-store/`.
- Before publishing, verify that the JSON files currently in `release/` exactly match the intended task pack; never rely on artifacts left by an earlier build.

## Task Authoring Rules
- Required fields: `base_score`, `name`, `description_en`, `description_ru`, `input_signature`, `output_signature`, `asserts`, `examples`, `solution`, `level`, `tags`, `time_to_solve_sec`.
- Optional fields: `limits`, `comment`.
- Keep field order aligned with `ai/task_example.toml`.
- `name` must be English and `snake_case`; the filename must match it exactly.
- `description_en` and `description_ru` are Markdown strings rendered with math support; keep them concise.
- English and Russian descriptions must define the same complete contract. State units, strict versus inclusive boundaries, output ordering, tie-breaks, empty/impossible behavior, and movement or scoring rules whenever relevant.
- Do not rely on domain knowledge for rules that affect the answer. For example, explicitly state point awards, allowed movement directions, interval semantics, and whether equality is allowed.
- Describe the goal rather than prescribing the intended algorithm unless reproducing a specified procedure is itself the task.
- Wrap mathematical notation in LaTeX using `$...$` or `$$...$$`.
- `limits`, when present, should be a Markdown list of constraints using math notation only, without prose.
- Choose limits from the task's actual data model and story scale, not arbitrary powers of ten. They must still make the reference algorithm safe.
- Every assert input must satisfy the published limits, and the test set should exercise meaningful boundary values. If limits change, re-audit existing asserts.
- Backslashes in LaTeX inside TOML basic multiline strings must be escaped, for example `\\leq` in the file source.
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
- Include cases for every documented tie-break and sentinel result such as empty output, `0`, or `-1`.
- For generated cases, independently verify expected values and keep a few small hand-checkable examples.

## Task Packs
- A pack JSON contains `name` and an ordered `task_names` array.
- Every listed name must resolve to exactly one TOML task, and every task intended for the pack must be listed exactly once.
- Order tasks by the intended participant progression, normally from easier to harder unless the pack specifies otherwise.
- Validate requested level counts and the exact sum of `time_to_solve_sec` programmatically rather than by inspection.
- Keep planning Markdown separate from pack JSON; publishing scripts read JSON files only.
- For hidden production delivery, keep both tasks and pack JSON under `private/`. Do not leave a copy of the private pack in public `task_packs/`, where it could be included in a public pack push.

## Private Build And Publishing Safety
- Hidden/private work is not authorized for network publication merely because it has been built. Never push unless the user explicitly requests it.
- Safe validation order: `make check-names`, `make check-limits`, then `make build-private`.
- After the private build, compare the names and count in `release/` with `private/task_packs/<pack>.json`.
- `make push-private` publishes tasks from the current `release/` with hidden visibility.
- `make push-packs-private` publishes pack definitions from `private/task_packs/` with hidden visibility.
- Publish tasks before their pack so every referenced task already exists.
- Do not run public push targets for private content.

## Difficulty And Timing
- `elementary`: target a 1-2 line solution.
- `easy`: target a 2-6 line solution.
- `medium`: target a 7-11 line solution.
- `hard`: target a 12+ line solution.
- Maximum `base_score` by level: `elementary` 50, `easy` 100, `medium` 150, `hard` 250.
- Maximum `time_to_solve_sec` by level: `elementary` 150, `easy` 300, `medium` 450, `hard` 900.
- Set `base_score` and `time_to_solve_sec` consistently with the project guidance documented in `ai/task_structure.md`.

## Style Notes
- Follow existing Python style in repository scripts: 4-space indentation and conventional import ordering.
- If formatting TOML, preserve the aligned style used in `ai/task_example.toml` and repository task files.
- Keep task text concise; avoid extra notes unless they materially clarify the contract.

## Commit And PR Notes
- Use short, imperative commit messages.
- In PRs, list created or changed tasks and note the validation commands you ran.
- Include preview screenshots only for UI changes under `preview/`.
