# Tasks

A comprehensive collection of programming tasks with a web-based preview system for browsing and testing solutions.

Built for [Codebattle](https://codebattle.hexlet.io).

## Overview

This project contains programming tasks organized by difficulty levels (easy, elementary, medium, hard) across various categories including algorithms, data structures, mathematics, and standard library problems. Each task is defined in TOML format with detailed descriptions, examples, and automated tests.

## Features

- **Task Management**: 100+ programming tasks in TOML format
- **Automated Testing**: Python-based test runner with comprehensive assertions
- **Web Preview**: React-based interface for browsing tasks with mathematical rendering
- **Multi-language Support**: English and Russian descriptions
- **Difficulty Levels**: Easy, Elementary, Medium, Hard
- **Categories**: Algorithms, Arrays, Graph, Math, Regex, Stdlib, Strings

## Dependencies

### Python Dependencies
```bash
pip install -r requirements.txt
```

### Node.js Dependencies (Dev Preview)
```bash
cd preview && pnpm install
```

### Tool Versions
- Node.js 24.11.0
- Rust 1.90.0
- Python 3.x

## Quick Start

### 1. Install Dependencies
```bash
# Python dependencies
pip install -r requirements.txt

# Node.js dependencies for preview
cd preview && pnpm install
```

### 2. Build Tasks
```bash
make build
```
This converts TOML task files to JSON format in the `release/` directory.

### 3. Start Preview Server
```bash
make preview
```
Opens a web interface at http://localhost:5173 showing all tasks with descriptions, examples, and solutions.

### 4. Combined Build and Preview
```bash
make build-and-preview
```

## Project Structure

```
tasks/
├── Makefile                # Build and preview commands
├── requirements.txt        # Python dependencies
├── test_solutions.py       # Test runner for task solutions
├── tasks/                  # Task definitions in TOML
│   ├── easy/               # Easy difficulty tasks
│   ├── elementary/         # Elementary difficulty tasks
│   ├── medium/             # Medium difficulty tasks
│   └── hard/               # Hard difficulty tasks
├── preview/                # Web preview application
│   ├── src/main.jsx       # React application
│   ├── vite.config.js     # Vite configuration
│   ├── server.mjs         # Express server
│   └── package.json       # Node.js dependencies
└── release/               # Generated JSON task files
```

## Task Format

Each task is defined in TOML format with the following structure:

```toml
level = "easy"
name = "example_task"
tags = ["arrays", "algorithms"]
time_to_solve_sec = 300

description_en = """
Task description in English with LaTeX math support.
"""

description_ru = """
Описание задачи на русском языке.
"""

solution = """
def solution(arg1, arg2):
    # Reference implementation
    return result
"""

examples = """
solution(1, 2) == 3
"""

[[input_signature]]
argument_name = "arg1"
[input_signature.type]
name = "integer"

[output_signature.type]
name = "integer"

[[asserts]]
arguments = [1, 2]
expected = 3
comment = "Basic test case"
```

## Available Commands

- `make build` - Convert TOML tasks to JSON format
- `make preview` - Start web preview server
- `make build-and-preview` - Build tasks then start preview
- `make release` - Create release archive

## Web Preview Features

The React-based preview interface provides:

- **Task Browsing**: View all tasks sorted by difficulty and name
- **Mathematical Rendering**: LaTeX support for mathematical expressions
- **Code Highlighting**: Syntax highlighting for solutions and examples
- **Responsive Design**: Mobile-friendly interface
- **Search & Filter**: Easy navigation through task collection
- **Multi-language Display**: Side-by-side English/Russian descriptions

## Testing

Tasks are automatically tested using the Python test runner:

```bash
python test_solutions.py tasks
```

The test runner:
- Parses TOML task definitions
- Executes provided solutions against test cases
- Validates input/output signatures
- Reports pass/fail status with detailed output

## Contributing

1. Add new tasks as `.toml` files in appropriate difficulty directories
2. Follow the established task format with complete metadata
3. Include comprehensive test cases with edge cases
4. Provide both English and Russian descriptions
5. Run `make build` to generate JSON files
6. Test with `make build-and-preview` to verify web display

## License

See LICENSE file for details.
