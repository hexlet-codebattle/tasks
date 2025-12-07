# 📋 Task Generation Format Specification

You are generating programming tasks in **TOML format**. Follow this specification carefully.

---

## 🎯 Main Fields

### **`name`** *(required)*
- **Type:** `string`
- **Description:** Human-readable task title, only in English and snake_case
- **Example:** `"sum_of_two_numbers"`

### **`description_en`** *(required)*
- **Type:** `string` (Markdown)
- **Description:** Task description in **English**
- **Rendering:** Uses `react-markdown` + `remark-math` + `rehype-katex`
- **Guidelines:**
  - Be concise and clear
  - Avoid unnecessary details, examples, or notes
  - Wrap all mathematical symbols and formulas using LaTeX syntax (`$...$` or `$$...$$`)

### **`description_ru`** *(required)*
- **Type:** `string` (Markdown)
- **Description:** Task description in **Russian**
- **Rendering:** Uses `react-markdown` + `remark-math` + `rehype-katex`
- **Guidelines:** Same as `description_en`

### **`limits`** *(optional)*
- **Type:** `string` (Markdown list)
- **Description:** Constraints on input variables
- **Guidelines:**
  - Use LaTeX for all mathematical expressions
  - Only math symbols allowed (no prose)
  - Wrap symbols with `$...$` notation
- **Example:**
  ```
  - $0 \leq a \leq 30$
  - $1 \leq \text{len}(s) \leq 17$
  ```

### **`input_signature`** *(required)*
- **Type:** Array of objects
- **Description:** Describes each argument of the `solution` function
- **Structure:**
  - `argument_name` — parameter identifier
  - `type` — type object (see [Type System](#-type-system))

### **`output_signature`** *(required)*
- **Type:** Object
- **Description:** Describes the return type of the `solution` function
- **Structure:** Contains a `type` object

### **`asserts`** *(required)*
- **Type:** Array of test case objects
- **Description:** Test cases to validate the solution
- **Structure:**
  - `arguments` — array of input values (must match `input_signature` order)
  - `expected` — the expected output value
  - `comment` *(optional)* — brief explanation of test intent
- **Requirements:**
  - ✅ Cover edge cases
  - ✅ Include extreme input values
  - ✅ Validate algorithm correctness thoroughly
  - ✅ All string data must be in **English**
  - ✅ Use realistic, diverse, and relevant data (avoid repetition)
  - 📊 **Recommended:** 25–30 tests for comprehensive coverage

### **`examples`** *(required)*
- **Type:** `string`
- **Description:** Usage examples showing function calls and expected results
- **Format:** Fenced code block with assertions
- **Example:**
  ```
  solution(0, 0) == 0
  solution(1, 2) == 3
  solution(-5, 7) == 2
  ```

### **`solution`** *(required)*
- **Type:** `string` (Python code)
- **Description:** Reference implementation
- **Guidelines:**
  - Define a `solution` function
  - Be as concise as possible
  - Use short variable names
  - Minimize lines of code
  - Avoid unnecessary imports (e.g., `defaultdict`, `setdefault` unless essential)
  - Prefer simple constructs

### **`level`** *(required)*
- **Type:** `string`
- **Description:** Difficulty classification based on code length
- **Values:**
  - `"elementary"` → 1–2 lines of code
  - `"easy"` → 2–6 lines of code
  - `"medium"` → 7–11 lines of code
  - `"hard"` → 12+ lines of code

### **`tags`** *(required)*
- **Type:** Array of strings
- **Description:** Category labels (may be empty)
- **Example:** `["math", "strings", "arrays"]`

### **`time_to_solve_sec`** *(required)*
- **Type:** `number`
- **Description:** Recommended solving time in seconds for average users
- **Example:** `60`

### **`comment`** *(optional)*
- **Type:** `string`
- **Description:** Additional author notes

---

## 📝 Task Description Example

```markdown
description_en = """
You're given a one-dimensional street as a string `s` made from the characters:
`"C"` (charging station), `"B"` (bike), and `"."` (empty).

Each second, a bike can move `1` position left or right.

Every `"B"` goes to its **nearest** `"C"` along a shortest path (time equals the absolute distance).

Return the **sum** of times for all bikes.

There is at least one `"C"`. If there are no `"B"`, return `0`.
"""
```

---

## 🔧 Type System

A **type object** contains:
- `name` — type identifier (`string`, `array`, `integer`, `boolean`, `float`, `hash`)
- `nested` *(optional)* — nested type description (for containers like arrays or hashes)

### Examples

**Simple type:**
```json
{"name": "integer"}
```

**Array of strings:**
```json
{"name": "array", "nested": {"name": "string"}}
```

**2D array of integers:**
```json
{"name": "array", "nested": {"name": "array", "nested": {"name": "integer"}}}
```

---

## 📋 Examples

### Input Signature Example
```json
[
  {"argument_name": "names", "type": {"name": "array", "nested": {"name": "string"}}},
  {"argument_name": "interests", "type": {"name": "array", "nested": {"name": "array", "nested": {"name": "string"}}}}
]
```

### Output Signature Example
```json
{"type": {"name": "array", "nested": {"name": "array", "nested": {"name": "string"}}}}
```

### Test Case Example
```json
{
  "arguments": [["Alice", "Bob"], [["reading"], ["reading"]]],
  "expected": [["Alice", "Bob"]],
  "comment": "A pair with one common interest"
}
```

### Limits Example
```
limits = """
- $0 \\leq a \\leq 30$
- $0 \\leq \\text{len}(\\text{login}) \\leq 30$
- $0 \\leq \\text{len}(\\text{taken\\_logins}) \\leq 10^4$
- $\\text{login} \\in \\{A{-}Z, a{-}z, 0{-}9, \\_\\}^*$
"""
```

---

## ✅ Allowed Type Signatures

### Primitive Types
```json
{"type": {"name": "string"}}
{"type": {"name": "boolean"}}
{"type": {"name": "integer"}}
{"type": {"name": "float"}}
```

### Arrays
```json
{"type": {"name": "array", "nested": {"name": "string"}}}
{"type": {"name": "array", "nested": {"name": "boolean"}}}
{"type": {"name": "array", "nested": {"name": "integer"}}}
{"type": {"name": "array", "nested": {"name": "float"}}}
```

### 2D Arrays
```json
{"type": {"name": "array", "nested": {"name": "array", "nested": {"name": "string"}}}}
{"type": {"name": "array", "nested": {"name": "array", "nested": {"name": "boolean"}}}}
{"type": {"name": "array", "nested": {"name": "array", "nested": {"name": "integer"}}}}
```

### Arrays with Hashes
```json
{"type": {"name": "array", "nested": {"name": "hash", "nested": {"name": "string"}}}}
{"type": {"name": "array", "nested": {"name": "hash", "nested": {"name": "boolean"}}}}
{"type": {"name": "array", "nested": {"name": "hash", "nested": {"name": "integer"}}}}
```

### 3D Arrays
```json
{"type": {"name": "array", "nested": {"name": "array", "nested": {"name": "array", "nested": {"name": "string"}}}}}
{"type": {"name": "array", "nested": {"name": "array", "nested": {"name": "array", "nested": {"name": "integer"}}}}}
{"type": {"name": "array", "nested": {"name": "array", "nested": {"name": "array", "nested": {"name": "boolean"}}}}}
```

### Complex Nested Types
```json
{"type": {"name": "array", "nested": {"name": "array", "nested": {"name": "hash", "nested": {"name": "string"}}}}}
{"type": {"name": "array", "nested": {"name": "array", "nested": {"name": "hash", "nested": {"name": "integer"}}}}}
{"type": {"name": "array", "nested": {"name": "array", "nested": {"name": "hash", "nested": {"name": "boolean"}}}}}
{"type": {"name": "array", "nested": {"name": "hash", "nested": {"name": "hash", "nested": {"name": "string"}}}}}
{"type": {"name": "array", "nested": {"name": "hash", "nested": {"name": "hash", "nested": {"name": "integer"}}}}}
{"type": {"name": "array", "nested": {"name": "hash", "nested": {"name": "hash", "nested": {"name": "boolean"}}}}}
{"type": {"name": "array", "nested": {"name": "hash", "nested": {"name": "array", "nested": {"name": "string"}}}}}
{"type": {"name": "array", "nested": {"name": "hash", "nested": {"name": "array", "nested": {"name": "integer"}}}}}
{"type": {"name": "array", "nested": {"name": "hash", "nested": {"name": "array", "nested": {"name": "boolean"}}}}}
```

### Deeply Nested Types
```json
{"type": {"name": "array", "nested": {"name": "hash", "nested": {"name": "hash", "nested": {"name": "hash", "nested": {"name": "array", "nested": {"name": "string"}}}}}}}
{"type": {"name": "array", "nested": {"name": "hash", "nested": {"name": "hash", "nested": {"name": "hash", "nested": {"name": "array", "nested": {"name": "integer"}}}}}}}
{"type": {"name": "array", "nested": {"name": "hash", "nested": {"name": "hash", "nested": {"name": "hash", "nested": {"name": "array", "nested": {"name": "boolean"}}}}}}}
```

### Hash Types
```json
{"type": {"name": "hash", "nested": {"name": "string"}}}
{"type": {"name": "hash", "nested": {"name": "boolean"}}}
{"type": {"name": "hash", "nested": {"name": "integer"}}}
{"type": {"name": "hash", "nested": {"name": "float"}}}
{"type": {"name": "hash", "nested": {"name": "hash", "nested": {"name": "string"}}}}
{"type": {"name": "hash", "nested": {"name": "hash", "nested": {"name": "integer"}}}}
{"type": {"name": "hash", "nested": {"name": "hash", "nested": {"name": "boolean"}}}}
```

---

## 📦 Complete TOML Example

```toml
level             = "elementary"
name              = "Sum of Two Numbers"
tags              = ["math"]
time_to_solve_sec = 15

description_en = """
Given two integers `a` and `b`, return their sum.
"""

description_ru = """
Даны два целых числа `a` и `b`. Верните их сумму.
"""

limits = """
- $0 \\leq a \\leq 30$
- $0 \\leq b \\leq 30$
"""

solution = """
def solution(a: int, b: int) -> int:
    return a + b
"""

examples = """
solution(0, 0) == 0
solution(1, 2) == 3
solution(-5, 7) == 2
"""

[[input_signature]]
argument_name = "a"
[input_signature.type]
name = "integer"

[[input_signature]]
argument_name = "b"
[input_signature.type]
name = "integer"

[output_signature.type]
name = "integer"

[[asserts]]
arguments = [1, 2]
comment   = "Simple positive numbers"
expected  = 3

[[asserts]]
arguments = [-5, 7]
comment   = "Negative and positive number"
expected  = 2

[[asserts]]
arguments = [0, 0]
comment   = "Both zeros"
expected  = 0

# ... continue with ~27 more test cases for comprehensive coverage
```

---

## 📌 Important Notes

- ⚠️ **All fields are required** unless explicitly marked as *(optional)*
- 📄 The TOML file must represent **a single task object**
- 🧪 Include **25–30 tests** for thorough validation
- 🌍 All test data must use **English** for strings
- 🎯 Keep descriptions concise and mathematical notation consistent
