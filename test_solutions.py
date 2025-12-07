import argparse
import difflib
import json
import os
import sys
from dataclasses import dataclass
from typing import Any, Callable, Dict, List

import tomli
from termcolor import colored


@dataclass
class TestCase:
    arguments: List[Any]
    expected: Any


@dataclass
class TestResult:
    passed: bool
    actual: Any
    expected: Any
    arguments: List[Any]


class TestRunner:
    ALLOWED_SIGNATURES = [
        {"type": {"name": "string"}},
        {"type": {"name": "boolean"}},
        {"type": {"name": "integer"}},
        {"type": {"name": "float"}},
        {"type": {"name": "array", "nested": {"name": "string"}}},
        {"type": {"name": "array", "nested": {"name": "boolean"}}},
        {"type": {"name": "array", "nested": {"name": "integer"}}},
        {"type": {"name": "array", "nested": {"name": "float"}}},
        {"type": {"name": "array", "nested": {"name": "array", "nested": {"name": "string"}}}},
        {"type": {"name": "array", "nested": {"name": "array", "nested": {"name": "boolean"}}}},
        {"type": {"name": "array", "nested": {"name": "array", "nested": {"name": "integer"}}}},
        {"type": {"name": "array", "nested": {"name": "hash", "nested": {"name": "string"}}}},
        {"type": {"name": "array", "nested": {"name": "hash", "nested": {"name": "boolean"}}}},
        {"type": {"name": "array", "nested": {"name": "hash", "nested": {"name": "integer"}}}},
        {"type": {"name": "array", "nested": {"name": "array", "nested": {"name": "array", "nested": {"name": "string"}}}}},
        {"type": {"name": "array", "nested": {"name": "array", "nested": {"name": "array", "nested": {"name": "integer"}}}}},
        {"type": {"name": "array", "nested": {"name": "array", "nested": {"name": "array", "nested": {"name": "boolean"}}}}},
        {"type": {"name": "array", "nested": {"name": "array", "nested": {"name": "hash", "nested": {"name": "string"}}}}},
        {"type": {"name": "array", "nested": {"name": "array", "nested": {"name": "hash", "nested": {"name": "integer"}}}}},
        {"type": {"name": "array", "nested": {"name": "array", "nested": {"name": "hash", "nested": {"name": "boolean"}}}}},
        {"type": {"name": "array", "nested": {"name": "hash", "nested": {"name": "hash", "nested": {"name": "string"}}}}},
        {"type": {"name": "array", "nested": {"name": "hash", "nested": {"name": "hash", "nested": {"name": "integer"}}}}},
        {"type": {"name": "array", "nested": {"name": "hash", "nested": {"name": "hash", "nested": {"name": "boolean"}}}}},
        {"type": {"name": "array", "nested": {"name": "hash", "nested": {"name": "array", "nested": {"name": "string"}}}}},
        {"type": {"name": "array", "nested": {"name": "hash", "nested": {"name": "array", "nested": {"name": "integer"}}}}},
        {"type": {"name": "array", "nested": {"name": "hash", "nested": {"name": "array", "nested": {"name": "boolean"}}}}},
        {
            "type": {
                "name": "array",
                "nested": {
                    "name": "hash",
                    "nested": {"name": "hash", "nested": {"name": "hash", "nested": {"name": "array", "nested": {"name": "string"}}}},
                },
            }
        },
        {
            "type": {
                "name": "array",
                "nested": {
                    "name": "hash",
                    "nested": {"name": "hash", "nested": {"name": "hash", "nested": {"name": "array", "nested": {"name": "integer"}}}},
                },
            }
        },
        {
            "type": {
                "name": "array",
                "nested": {
                    "name": "hash",
                    "nested": {"name": "hash", "nested": {"name": "hash", "nested": {"name": "array", "nested": {"name": "boolean"}}}},
                },
            }
        },
        {"type": {"name": "hash", "nested": {"name": "string"}}},
        {"type": {"name": "hash", "nested": {"name": "boolean"}}},
        {"type": {"name": "hash", "nested": {"name": "integer"}}},
        {"type": {"name": "hash", "nested": {"name": "float"}}},
        {"type": {"name": "hash", "nested": {"name": "hash", "nested": {"name": "string"}}}},
        {"type": {"name": "hash", "nested": {"name": "hash", "nested": {"name": "integer"}}}},
        {"type": {"name": "hash", "nested": {"name": "hash", "nested": {"name": "boolean"}}}},
    ]

    def __init__(self, toml_dir_or_file: str, skip_assert_count: bool = False):
        self.toml_path = os.path.abspath(toml_dir_or_file)
        self.is_file = os.path.isfile(self.toml_path)
        self.skip_assert_count = skip_assert_count
        self.toml_data_cache: Dict[str, Dict[str, Any]] = {}

    def validate_signature(self, signature: Dict[str, Any], signature_type: str) -> None:
        """Validate that a signature is in the allowed list"""
        if signature not in self.ALLOWED_SIGNATURES:
            raise ValueError(f"Invalid {signature_type}: {signature} is not in the allowed signatures list")

    def signature_to_str(self, sig: Dict[str, Any]) -> str:
        t = sig.get("type", sig)
        name = t.get("name")
        if name in ("string", "boolean", "integer", "float"):
            return name
        if name == "array":
            return f"array<{self.signature_to_str({'type': t['nested']})}>"
        if name == "hash":
            return f"hash<{self.signature_to_str({'type': t['nested']})}>"
        return str(sig)

    def _is_int(self, v: Any) -> bool:
        # In Python, bool is a subclass of int; exclude bool for "integer"
        return isinstance(v, int) and not isinstance(v, bool)

    def _is_float(self, v: Any) -> bool:
        # Keep float strict (change to isinstance(v, (int, float)) & not bool for looser behavior)
        return isinstance(v, float)

    def _coerce_for_typecheck(self, v: Any) -> Any:
        """
        If v is a JSON string representing a list/dict, return the parsed container;
        otherwise return v unchanged. Mirrors comparison behavior in _try_json_container use.
        """
        j = self._try_json_container(v)
        return j if j is not None else v

    def type_matches(self, sig: Dict[str, Any], value: Any, path: str = "value") -> tuple[bool, str | None]:
        """
        Recursively check that 'value' matches 'sig'. Returns (ok, error_message_or_None).
        """
        t = sig.get("type", sig)
        name = t.get("name")
        v = self._coerce_for_typecheck(value)

        if name == "string":
            ok = isinstance(v, str)
            return (ok, None if ok else f"{path} expected string, got {type(v).__name__}")
        if name == "boolean":
            ok = isinstance(v, bool)
            return (ok, None if ok else f"{path} expected boolean, got {type(v).__name__}")
        if name == "integer":
            ok = self._is_int(v)
            return (ok, None if ok else f"{path} expected integer, got {type(v).__name__}")
        if name == "float":
            ok = self._is_float(v)
            return (ok, None if ok else f"{path} expected float, got {type(v).__name__}")

        if name == "array":
            if not isinstance(v, list):
                return (False, f"{path} expected array/list, got {type(v).__name__}")
            nested = {"type": t["nested"]}
            for i, item in enumerate(v):
                ok, err = self.type_matches(nested, item, f"{path}[{i}]")
                if not ok:
                    return (False, err)
            return (True, None)

        if name == "hash":
            if not isinstance(v, dict):
                return (False, f"{path} expected hash/dict, got {type(v).__name__}")
            nested = {"type": t["nested"]}
            for k, item in v.items():
                ok, err = self.type_matches(nested, item, f"{path}.{k}")
                if not ok:
                    return (False, err)
            return (True, None)

        return (False, f"{path} has unknown signature: {sig}")

    def load_toml_data(self, toml_path: str) -> tuple[List[TestCase], str, str]:
        with open(toml_path, "rb") as f:
            data = tomli.load(f)

        self.toml_data_cache[toml_path] = data

        task_name = data.get("name", os.path.basename(toml_path))

        if "input_signature" in data:
            input_sigs = data["input_signature"]
            if isinstance(input_sigs, list):
                for sig in input_sigs:
                    if "type" in sig:
                        self.validate_signature({"type": sig["type"]}, "input_signature")
            else:
                self.validate_signature(data["input_signature"], "input_signature")

        if "output_signature" in data:
            self.validate_signature(data["output_signature"], "output_signature")

        test_cases: List[TestCase] = []
        for assert_data in data.get("asserts", []):
            test_cases.append(TestCase(arguments=assert_data["arguments"], expected=assert_data["expected"]))

        # Pre-validate assert arguments/expected against signatures for early, clear errors
        try:
            display_name = toml_path if self.is_file else os.path.relpath(toml_path, self.toml_path)
            self.check_assert_types(data, display_name)
        except Exception:
            raise

        # Align threshold & message to 30
        if not self.skip_assert_count and len(test_cases) < 30:
            print(colored(f"WARNING: Task '{task_name}' has only {len(test_cases)} asserts (less than 30)", "yellow"))
            if len(test_cases) == 0:
                raise ValueError("NO ASSERTS FOUND")

        solution_code = data.get("solution", "")
        if not solution_code:
            raise ValueError("THERE IS NO SOLUTION")

        return test_cases, solution_code, task_name

    def create_solution_function(self, solution_code: str) -> Callable:
        namespace: Dict[str, Any] = {}
        try:
            exec(solution_code, namespace)
            if "solution" not in namespace or not callable(namespace["solution"]):
                raise ValueError("Solution code does not define a 'solution' function")
            return namespace["solution"]
        except SyntaxError as e:
            raise ValueError(f"SYNTAX ERROR: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to create solution function: {str(e)}")

    def normalize_output(self, value: Any) -> Any:
        """Normalize output to handle case-sensitivity in dictionaries"""
        if isinstance(value, dict):
            return {k.lower(): self.normalize_output(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self.normalize_output(x) for x in value]
        elif isinstance(value, str):
            return value.lower()
        return value

    def values_equal(self, actual: Any, expected: Any) -> bool:
        """Compare values with normalization for case-insensitive comparison"""
        if actual == expected:
            return True

        if isinstance(actual, str) and isinstance(expected, str):
            if actual.isdigit() and expected.isdigit():
                return actual == expected

        return self.normalize_output(actual) == self.normalize_output(expected)

    def find_difference(self, actual: Any, expected: Any, path: str = "") -> List[str]:
        """Find and return detailed differences between actual and expected values"""
        differences: List[str] = []

        if isinstance(expected, list) and isinstance(actual, list):
            if len(expected) != len(actual):
                differences.append(f"{path} → different number of elements: expected {len(expected)}, got {len(actual)}")

            min_len = min(len(expected), len(actual))
            for i in range(min_len):
                new_path = f"{path}[{i}]"
                if not self.values_equal(actual[i], expected[i]):
                    if isinstance(expected[i], (list, dict)) and isinstance(actual[i], (list, dict)):
                        differences.extend(self.find_difference(actual[i], expected[i], new_path))
                    else:
                        differences.append(f"{new_path} → expected {expected[i]}, got {actual[i]}")

            for i in range(min_len, len(actual)):
                differences.append(f"{path}[{i}] → extra element: {actual[i]}")

            for i in range(min_len, len(expected)):
                differences.append(f"{path}[{i}] → missing element: {expected[i]}")

        elif isinstance(expected, dict) and isinstance(actual, dict):
            for key in expected:
                if key not in actual:
                    differences.append(f"{path}.{key} → missing key")
                elif not self.values_equal(actual[key], expected[key]):
                    if isinstance(expected[key], (list, dict)) and isinstance(actual[key], (list, dict)):
                        differences.extend(self.find_difference(actual[key], expected[key], f"{path}.{key}"))
                    else:
                        differences.append(f"{path}.{key} → expected {expected[key]}, got {actual[key]}")

            for key in actual:
                if key not in expected:
                    differences.append(f"{path}.{key} → extra key: {actual[key]}")
        else:
            if not self.values_equal(actual, expected):
                differences.append(f"{path} → expected {expected}, got {actual}")

        return differences

    def format_value(self, value, indent=0, color=None):
        """Format a value for display, handling nested structures"""
        result = ""
        if isinstance(value, list):
            if not value:
                result = "[]"
            else:
                lines = ["["]
                for item in value:
                    lines.append(f"{'  ' * (indent + 1)}{self.format_value(item, indent + 1)},")
                lines.append(f"{'  ' * indent}]")
                result = "\n".join(lines)
        elif isinstance(value, dict):
            if not value:
                result = "{}"
            else:
                lines = ["{"]
                for k, v in value.items():
                    lines.append(f"{'  ' * (indent + 1)}{k}: {self.format_value(v, indent + 1)},")
                lines.append(f"{'  ' * indent}}}")
                result = "\n".join(lines)
        elif isinstance(value, str):
            result = f'"{value}"'
        else:
            result = str(value)

        if color:
            return colored(result, color)
        return result

    @staticmethod
    def _try_json_container(v: Any):
        """
        Try to parse JSON and only return objects that are dict/list.
        Returns None if parsing fails or if the value is a primitive.
        """
        if not isinstance(v, str):
            return None
        try:
            obj = json.loads(v)
            return obj if isinstance(obj, (dict, list)) else None
        except Exception:
            return None

    def check_assert_types(self, data: Dict[str, Any], display_name: str):
        """
        Validate that:
          - each assert.arguments match input_signature
          - each assert.expected matches output_signature
          - every integer in arguments/expected is within 32-bit C++ int bounds
            (lower bound inclusive, upper bound exclusive): [-2147483648, 2147483647)
        """
        input_sig = data.get("input_signature")
        output_sig = data.get("output_signature")
        asserts = data.get("asserts", [])

        if output_sig is None:
            raise ValueError("Missing output_signature")

        INT32_MIN = -2147483648
        INT32_MAX_EXCLUSIVE = 2147483647  # must be strictly less than this

        def check_int_bounds(sig: Dict[str, Any], value: Any, path: str = "value"):
            """
            Recursively ensure that any field typed as 'integer' is within
            [-2147483648, 2147483647). Mirrors the structure of `sig`.
            """
            t = sig.get("type", sig)
            name = t.get("name")
            v = self._coerce_for_typecheck(value)

            if name == "integer":
                if self._is_int(v):
                    if not (INT32_MIN <= v < INT32_MAX_EXCLUSIVE):
                        raise ValueError(f"{path}: integer {v} is out of C++ 32-bit int range [{INT32_MIN}, {INT32_MAX_EXCLUSIVE})")
                # If it's not an int, type_matches() will raise elsewhere.
                return

            if name == "array":
                if isinstance(v, list):
                    nested = {"type": t["nested"]}
                    for i, item in enumerate(v):
                        check_int_bounds(nested, item, f"{path}[{i}]")
                return

            if name == "hash":
                if isinstance(v, dict):
                    nested = {"type": t["nested"]}
                    for k, item in v.items():
                        check_int_bounds(nested, item, f"{path}.{k}")
                return

            # For non-integer primitives ('string','boolean','float') do nothing.

        for idx, a in enumerate(asserts, start=1):
            args = a.get("arguments", [])
            expected = a.get("expected")

            # Check arguments vs input_signature
            if input_sig is None:
                # If no input_signature is provided, assume 0-arg function
                if len(args) != 0:
                    raise ValueError(f"[{display_name}] Assert #{idx}: has {len(args)} argument(s) but no input_signature is defined")
            elif isinstance(input_sig, list):
                if len(args) != len(input_sig):
                    raise ValueError(
                        f"[{display_name}] Assert #{idx}: expected {len(input_sig)} argument(s) per input_signature, got {len(args)}"
                    )
                for i, (arg, sig) in enumerate(zip(args, input_sig), start=1):
                    ok, err = self.type_matches({"type": sig["type"]}, arg, f"arguments[{i - 1}]")
                    if not ok:
                        want = self.signature_to_str({"type": sig["type"]})
                        raise ValueError(f"[{display_name}] Assert #{idx}: argument {i} type mismatch: {err} (wanted {want})")
                    # Enforce int bounds for this argument according to its signature
                    check_int_bounds({"type": sig["type"]}, arg, f"arguments[{i - 1}]")
            else:
                # Single input_signature
                if len(args) != 1:
                    raise ValueError(f"[{display_name}] Assert #{idx}: expected 1 argument per input_signature, got {len(args)}")
                ok, err = self.type_matches(input_sig, args[0], "arguments[0]")
                if not ok:
                    want = self.signature_to_str(input_sig)
                    raise ValueError(f"[{display_name}] Assert #{idx}: argument 1 type mismatch: {err} (wanted {want})")
                check_int_bounds(input_sig, args[0], "arguments[0]")

            # Check expected vs output_signature
            ok, err = self.type_matches(output_sig, expected, "expected")
            if not ok:
                want = self.signature_to_str(output_sig)
                raise ValueError(f"[{display_name}] Assert #{idx}: expected value type mismatch: {err} (wanted {want})")
            # Enforce int bounds for expected value according to output signature
            check_int_bounds(output_sig, expected, "expected")

    def run_tests(self) -> Dict[str, tuple[List[TestResult], str]]:
        """
        Returns a dict keyed by display path (relative to the provided directory if a directory was given,
        otherwise the absolute file path), mapping to (test_results, task_name).
        """
        results: Dict[str, tuple[List[TestResult], str]] = {}
        has_errors = False

        # Build list of .toml files (recursively for directories)
        if self.is_file:
            files_to_process = [self.toml_path]
        else:
            files_to_process = []
            for root, _, files in os.walk(self.toml_path):
                for f in files:
                    if f.endswith(".toml"):
                        files_to_process.append(os.path.join(root, f))

        for toml_path in files_to_process:
            # Display name: relative path for dirs (prevents collisions), absolute if single file
            display_name = toml_path if self.is_file else os.path.relpath(toml_path, self.toml_path)

            try:
                test_cases, solution_code, task_name = self.load_toml_data(toml_path)
                solution_func = self.create_solution_function(solution_code)

                # Grab signatures for runtime output checking
                data = self.toml_data_cache[toml_path]
                output_sig = data.get("output_signature")

                test_results: List[TestResult] = []
                for case in test_cases:
                    try:
                        actual = solution_func(*case.arguments)

                        exp_obj = self._try_json_container(case.expected)
                        act_obj = self._try_json_container(actual)

                        if exp_obj is not None and act_obj is not None:
                            passed = self.values_equal(act_obj, exp_obj)
                        else:
                            passed = self.values_equal(actual, case.expected)

                        # Enforce runtime output type vs signature
                        if output_sig is not None:
                            ok, err = self.type_matches(output_sig, actual, "actual")
                            if not ok:
                                passed = False
                                actual = f"TYPE ERROR: {err} ; value={self.format_value(actual)}"

                        test_results.append(TestResult(passed=passed, actual=actual, expected=case.expected, arguments=case.arguments))
                    except Exception as e:
                        test_results.append(TestResult(passed=False, actual=str(e), expected=case.expected, arguments=case.arguments))

                results[display_name] = (test_results, task_name)

            except Exception as e:
                has_errors = True
                print(colored(f"\nResults for {display_name}:", "yellow"))
                print("-" * 70)
                error_msg = str(e)
                print(colored(error_msg, "red"))
                print(colored(f"ERROR: Failed to execute solution for {display_name}", "red", attrs=["bold"]))
                if "Solution code does not define a 'solution' function" in error_msg or "THERE IS NO SOLUTION" in error_msg:
                    print(colored("Critical error: 'solution' function not found in code", "red", attrs=["bold"]))
                    sys.exit(1)

        if has_errors:
            sys.exit(1)

        return results

    def create_release_folder(self, results: Dict[str, tuple[List[TestResult], str]]):
        """Create release folder with JSON tasks if all tests pass. Mirrors directory structure."""
        release_dir = "release"
        os.makedirs(release_dir, exist_ok=True)

        for display_name in results.keys():
            # Reconstruct the absolute toml_path
            if self.is_file:
                toml_path = self.toml_path
                rel_dir = ""
                base_name = os.path.basename(toml_path)
            else:
                toml_path = os.path.join(self.toml_path, display_name)
                rel_dir = os.path.dirname(display_name)
                base_name = os.path.basename(display_name)

            if toml_path in self.toml_data_cache:
                data = self.toml_data_cache[toml_path]

                json_data = {"name": data.get("name", os.path.basename(base_name)), "asserts": data.get("asserts", [])}

                for key in data:
                    if key not in ["name", "asserts"]:
                        json_data[key] = data[key]

                # Ensure subdirectory in release mirrors the source layout
                out_dir = os.path.join(release_dir, rel_dir)
                os.makedirs(out_dir, exist_ok=True)

                json_filename = os.path.splitext(base_name)[0] + ".json"
                json_path = os.path.join(out_dir, json_filename)

                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)

        print(colored(f"\n📦 Created release folder with {len(results)} JSON task files", "green", attrs=["bold"]))

    def print_results(self, results: Dict[str, tuple[List[TestResult], str]], verbose: bool = False):
        total_tests = 0
        total_passed = 0
        total_failed = 0

        failed_tasks: Dict[str, Dict[str, Any]] = {}
        # task -> display_name -> list[(index, TestResult)]
        failed_test_details: Dict[str, Dict[str, List[tuple[int, TestResult]]]] = {}

        # Per-file summaries
        for display_name, (test_results, task_name) in sorted(results.items()):
            print(f"\n{colored('Task:', 'white', attrs=['bold'])} {colored(task_name, 'cyan', attrs=['bold'])}")
            print(f"\n{colored('Results for', 'white', attrs=['bold'])} {colored(display_name, 'cyan', attrs=['bold'])}")
            print(colored("═" * 80, "blue"))

            passed = sum(1 for r in test_results if r.passed)
            total = len(test_results)

            total_tests += total
            total_passed += passed
            failed_in_file = total - passed
            total_failed += failed_in_file

            if failed_in_file > 0:
                if task_name not in failed_tasks:
                    failed_tasks[task_name] = {"total": 0, "failed": 0, "files": []}
                failed_tasks[task_name]["total"] += total
                failed_tasks[task_name]["failed"] += failed_in_file
                failed_tasks[task_name]["files"].append(display_name)

            pass_rate = passed / total * 100 if total > 0 else 0
            if passed == total:
                status = colored("✅ ALL TESTS PASSED", "green", attrs=["bold"])
            else:
                status = colored(f"❌ TESTS FAILED: {failed_in_file}", "red", attrs=["bold"])

            print(f"{status} ({passed}/{total} tests, {pass_rate:.1f}%)")

            # Per-test output (verbose mode prints everything here)
            for i, result in enumerate(test_results, 1):
                if verbose:
                    print("\n" + colored("─" * 80, "blue"))
                    # 👇 Task + file for every test in verbose mode
                    print(
                        f"{colored('Task:', 'white', attrs=['bold'])} {colored(task_name, 'cyan', attrs=['bold'])}  "
                        f"{colored('File:', 'white', attrs=['bold'])} {colored(display_name, 'cyan')}"
                    )
                    print(f"Test #{i}: {'✅ PASSED' if result.passed else colored('❌ TEST FAILED', 'red', attrs=['bold'])}")

                    print(colored("\n📥 Arguments:", "cyan", attrs=["bold"]))
                    if not isinstance(result.arguments, (list, tuple)):
                        print(f"  Argument: {self.format_value(result.arguments)}")
                    else:
                        for j, arg in enumerate(result.arguments):
                            print(f"  Argument {j + 1}: {self.format_value(arg)}")

                    print(colored("\n✓ Expected result:", "green", attrs=["bold"]))
                    print(f"  {self.format_value(result.expected, color='green')}")

                    print(colored("\n⨯ Actual result:", "red", attrs=["bold"]))
                    print(f"  {self.format_value(result.actual, color='red')}")

                    if not result.passed:
                        differences = self.find_difference(result.actual, result.expected)
                        if differences:
                            print(colored("\n🔍 Difference details:", "yellow", attrs=["bold"]))
                            for diff in differences:
                                print(f"  • {diff}")

                        expected_str = self.format_value(result.expected)
                        actual_str = self.format_value(result.actual)
                        if isinstance(result.expected, (int, float, str, bool)) and isinstance(result.actual, (int, float, str, bool)):
                            if str(expected_str) != str(actual_str):
                                print(colored("\n📊 Comparison:", "magenta", attrs=["bold"]))
                                diff = difflib.ndiff([str(expected_str)], [str(actual_str)])
                                print("  " + "\n  ".join(diff))
                else:
                    # non-verbose: collect only failed tests for later detailed print
                    if not result.passed:
                        failed_test_details.setdefault(task_name, {}).setdefault(display_name, []).append((i, result))

        # Overall summary
        if total_tests > 0:
            print("\n" + colored("Overall results:", "white", attrs=["bold"]))
            print(colored("═" * 80, "blue"))
            print(f"Total tests: {total_tests}")
            print(f"Passed tests: {colored(total_passed, 'green' if total_passed == total_tests else 'yellow')}")
            if total_failed > 0:
                print(f"Failed tests: {colored(total_failed, 'red')}")
            print(
                f"Success rate: {colored(f'{total_passed / total_tests * 100:.1f}%', 'green' if total_passed == total_tests else 'yellow')}"
            )

            if total_passed == total_tests:
                print(colored("\n✨ All tests passed successfully! ✨", "green", attrs=["bold"]))
                self.create_release_folder(results)
                return  # no exit with error

            # Some tests failed
            print(colored(f"\n❌ {total_failed} tests failed", "red", attrs=["bold"]))

            if failed_tasks:
                print("\n" + colored("Summary of tasks with failed tests:", "yellow", attrs=["bold"]))
                print(colored("═" * 80, "blue"))
                for task, stats in failed_tasks.items():
                    fail_rate = stats["failed"] / stats["total"] * 100
                    print(
                        f"{colored(task, 'cyan')} - failed {colored(stats['failed'], 'red')} of {stats['total']} tests ({fail_rate:.1f}%)"
                    )
                    print(f"  Files: {', '.join(stats['files'])}")

            # Detailed failures for non-verbose mode (verbose already printed them)
            if not verbose and failed_test_details:
                print("\n" + colored("Detailed failed tests (grouped by task and file):", "white", attrs=["bold"]))
                print(colored("═" * 80, "blue"))

                for task, files in failed_test_details.items():
                    for display_name, tests in files.items():
                        for index, result in tests:
                            print("\n" + colored("─" * 80, "blue"))
                            # 👇 Task + file for every failed test
                            print(
                                f"{colored('Task:', 'white', attrs=['bold'])} {colored(task, 'cyan', attrs=['bold'])}  "
                                f"{colored('File:', 'white', attrs=['bold'])} {colored(display_name, 'cyan')}"
                            )
                            print(colored(f"Test #{index}: ❌ TEST FAILED", "red", attrs=["bold"]))

                            print(colored("\n📥 Arguments:", "cyan", attrs=["bold"]))
                            if not isinstance(result.arguments, (list, tuple)):
                                print(f"  Argument: {self.format_value(result.arguments)}")
                            else:
                                for j, arg in enumerate(result.arguments):
                                    print(f"  Argument {j + 1}: {self.format_value(arg)}")

                            print(colored("\n✓ Expected result:", "green", attrs=["bold"]))
                            print(f"  {self.format_value(result.expected, color='green')}")

                            print(colored("\n⨯ Actual result:", "red", attrs=["bold"]))
                            print(f"  {self.format_value(result.actual, color='red')}")

                            differences = self.find_difference(result.actual, result.expected)
                            if differences:
                                print(colored("\n🔍 Difference details:", "yellow", attrs=["bold"]))
                                for diff in differences:
                                    print(f"  • {diff}")

                            expected_str = self.format_value(result.expected)
                            actual_str = self.format_value(result.actual)
                            if isinstance(result.expected, (int, float, str, bool)) and isinstance(result.actual, (int, float, str, bool)):
                                if str(expected_str) != str(actual_str):
                                    print(colored("\n📊 Comparison:", "magenta", attrs=["bold"]))
                                    diff = difflib.ndiff([str(expected_str)], [str(actual_str)])
                                    print("  " + "\n  ".join(diff))

            # Non-zero exit code when there are failing tests
            sys.exit(1)
        total_tests = 0
        total_passed = 0
        total_failed = 0
        task_name = "Unknown"

        failed_tasks: Dict[str, Dict[str, Any]] = {}
        # task -> display_name -> list[(index, TestResult)]
        failed_test_details: Dict[str, Dict[str, List[tuple[int, TestResult]]]] = {}

        for display_name, (test_results, current_task_name) in sorted(results.items()):
            task_name = current_task_name
            print(f"\n{colored('Task:', 'white', attrs=['bold'])} {colored(task_name, 'cyan', attrs=['bold'])}")
            print(f"\n{colored('Results for', 'white', attrs=['bold'])} {colored(display_name, 'cyan', attrs=['bold'])}")
            print(colored("═" * 80, "blue"))

            passed = sum(1 for r in test_results if r.passed)
            total = len(test_results)

            total_tests += total
            total_passed += passed
            failed_in_file = total - passed
            total_failed += failed_in_file

            if failed_in_file > 0:
                if task_name not in failed_tasks:
                    failed_tasks[task_name] = {"total": 0, "failed": 0, "files": []}
                failed_tasks[task_name]["total"] += total
                failed_tasks[task_name]["failed"] += failed_in_file
                failed_tasks[task_name]["files"].append(display_name)

            pass_rate = passed / total * 100 if total > 0 else 0
            if passed == total:
                status = colored("✅ ALL TESTS PASSED", "green", attrs=["bold"])
            else:
                status = colored(f"❌ TESTS FAILED: {failed_in_file}", "red", attrs=["bold"])

            print(f"{status} ({passed}/{total} tests, {pass_rate:.1f}%)")

            # Collect / print test details
            for i, result in enumerate(test_results, 1):
                if verbose:
                    # old behavior: print everything (or only failures) inline
                    if result.passed and not verbose:
                        continue
                    print("\n" + colored("─" * 80, "blue"))
                    print(f"Test #{i}: {'✅ PASSED' if result.passed else colored('❌ TEST FAILED', 'red', attrs=['bold'])}")

                    print(colored("\n📥 Arguments:", "cyan", attrs=["bold"]))
                    if not isinstance(result.arguments, (list, tuple)):
                        print(f"  Argument: {self.format_value(result.arguments)}")
                    else:
                        for j, arg in enumerate(result.arguments):
                            print(f"  Argument {j + 1}: {self.format_value(arg)}")

                    print(colored("\n✓ Expected result:", "green", attrs=["bold"]))
                    print(f"  {self.format_value(result.expected, color='green')}")

                    print(colored("\n⨯ Actual result:", "red", attrs=["bold"]))
                    print(f"  {self.format_value(result.actual, color='red')}")

                    if not result.passed:
                        differences = self.find_difference(result.actual, result.expected)
                        if differences:
                            print(colored("\n🔍 Difference details:", "yellow", attrs=["bold"]))
                            for diff in differences:
                                print(f"  • {diff}")

                        expected_str = self.format_value(result.expected)
                        actual_str = self.format_value(result.actual)
                        if isinstance(result.expected, (int, float, str, bool)) and isinstance(result.actual, (int, float, str, bool)):
                            if str(expected_str) != str(actual_str):
                                print(colored("\n📊 Comparison:", "magenta", attrs=["bold"]))
                                diff = difflib.ndiff([str(expected_str)], [str(actual_str)])
                                print("  " + "\n  ".join(diff))
                else:
                    # non-verbose: just collect failed tests for end-of-output printing
                    if not result.passed:
                        failed_test_details.setdefault(task_name, {}).setdefault(display_name, []).append((i, result))

        if total_tests > 0:
            print("\n" + colored("Overall results:", "white", attrs=["bold"]))
            print(colored("═" * 80, "blue"))
            print(f"Total tests: {total_tests}")
            print(f"Passed tests: {colored(total_passed, 'green' if total_passed == total_tests else 'yellow')}")
            if total_failed > 0:
                print(f"Failed tests: {colored(total_failed, 'red')}")
            print(
                f"Success rate: {colored(f'{total_passed / total_tests * 100:.1f}%', 'green' if total_passed == total_tests else 'yellow')}"
            )

            if total_passed == total_tests:
                print(colored("\n✨ All tests passed successfully! ✨", "green", attrs=["bold"]))
                self.create_release_folder(results)
            else:
                print(colored(f"\n❌ {total_failed} tests failed", "red", attrs=["bold"]))

                if failed_tasks:
                    print("\n" + colored("Summary of tasks with failed tests:", "yellow", attrs=["bold"]))
                    print(colored("═" * 80, "blue"))
                    for task, stats in failed_tasks.items():
                        fail_rate = stats["failed"] / stats["total"] * 100
                        print(
                            f"{colored(task, 'cyan')} - failed {colored(stats['failed'], 'red')} "
                            f"of {stats['total']} tests ({fail_rate:.1f}%)"
                        )
                        print(f"  Files: {', '.join(stats['files'])}")

                # Now print all failed test details at the very end (non-verbose mode)
                if not verbose and failed_test_details:
                    print("\n" + colored("Detailed failed tests (grouped by task and file):", "white", attrs=["bold"]))
                    print(colored("═" * 80, "blue"))

                    for task, files in failed_test_details.items():
                        # 👇 Task name printed right after "asserts info" header
                        print(f"\n{colored('Task:', 'white', attrs=['bold'])} {colored(task, 'cyan', attrs=['bold'])}")
                        for display_name, tests in files.items():
                            print(f"\n{colored('File:', 'white', attrs=['bold'])} {colored(display_name, 'cyan')}")
                            for index, result in tests:
                                print("\n" + colored("─" * 80, "blue"))
                                print(colored(f"Test #{index}: ❌ TEST FAILED", "red", attrs=["bold"]))

                                print(colored("\n📥 Arguments:", "cyan", attrs=["bold"]))
                                if not isinstance(result.arguments, (list, tuple)):
                                    print(f"  Argument: {self.format_value(result.arguments)}")
                                else:
                                    for j, arg in enumerate(result.arguments):
                                        print(f"  Argument {j + 1}: {self.format_value(arg)}")

                                print(colored("\n✓ Expected result:", "green", attrs=["bold"]))
                                print(f"  {self.format_value(result.expected, color='green')}")

                                print(colored("\n⨯ Actual result:", "red", attrs=["bold"]))
                                print(f"  {self.format_value(result.actual, color='red')}")

                                differences = self.find_difference(result.actual, result.expected)
                                if differences:
                                    print(colored("\n🔍 Difference details:", "yellow", attrs=["bold"]))
                                    for diff in differences:
                                        print(f"  • {diff}")

                                expected_str = self.format_value(result.expected)
                                actual_str = self.format_value(result.actual)
                                if isinstance(result.expected, (int, float, str, bool)) and isinstance(
                                    result.actual, (int, float, str, bool)
                                ):
                                    if str(expected_str) != str(actual_str):
                                        print(colored("\n📊 Comparison:", "magenta", attrs=["bold"]))
                                        diff = difflib.ndiff([str(expected_str)], [str(actual_str)])
                                        print("  " + "\n  ".join(diff))

                sys.exit(1)
            print("\n" + colored("Overall results:", "white", attrs=["bold"]))
            print(colored("═" * 80, "blue"))
            print(f"Total tests: {total_tests}")
            print(f"Passed tests: {colored(total_passed, 'green' if total_passed == total_tests else 'yellow')}")
            if total_failed > 0:
                print(f"Failed tests: {colored(total_failed, 'red')}")
            print(
                f"Success rate: {colored(f'{total_passed / total_tests * 100:.1f}%', 'green' if total_passed == total_tests else 'yellow')}"
            )

            if total_passed == total_tests:
                print(colored("\n✨ All tests passed successfully! ✨", "green", attrs=["bold"]))
                self.create_release_folder(results)
            else:
                print(colored(f"\n❌ {total_failed} tests failed", "red", attrs=["bold"]))

                if failed_tasks:
                    print("\n" + colored("Summary of tasks with failed tests:", "yellow", attrs=["bold"]))
                    print(colored("═" * 80, "blue"))
                    for task, stats in failed_tasks.items():
                        fail_rate = stats["failed"] / stats["total"] * 100
                        print(
                            f"{colored(task, 'cyan')} - failed {colored(stats['failed'], 'red')} "
                            f"of {stats['total']} tests ({fail_rate:.1f}%)"
                        )
                        print(f"  Files: {', '.join(stats['files'])}")

                # Now print all failed test details at the very end (non-verbose mode)
                if not verbose and failed_test_details:
                    print("\n" + colored("Detailed failed tests (grouped by task and file):", "white", attrs=["bold"]))
                    print(colored("═" * 80, "blue"))

                    for task, files in failed_test_details.items():
                        print(f"\n{colored('Task:', 'white', attrs=['bold'])} {colored(task, 'cyan', attrs=['bold'])}")
                        for display_name, tests in files.items():
                            print(f"\n{colored('File:', 'white', attrs=['bold'])} {colored(display_name, 'cyan')}")
                            for index, result in tests:
                                print("\n" + colored("─" * 80, "blue"))
                                print(colored(f"Test #{index}: ❌ TEST FAILED", "red", attrs=["bold"]))

                                print(colored("\n📥 Arguments:", "cyan", attrs=["bold"]))
                                if not isinstance(result.arguments, (list, tuple)):
                                    print(f"  Argument: {self.format_value(result.arguments)}")
                                else:
                                    for j, arg in enumerate(result.arguments):
                                        print(f"  Argument {j + 1}: {self.format_value(arg)}")

                                print(colored("\n✓ Expected result:", "green", attrs=["bold"]))
                                print(f"  {self.format_value(result.expected, color='green')}")

                                print(colored("\n⨯ Actual result:", "red", attrs=["bold"]))
                                print(f"  {self.format_value(result.actual, color='red')}")

                                differences = self.find_difference(result.actual, result.expected)
                                if differences:
                                    print(colored("\n🔍 Difference details:", "yellow", attrs=["bold"]))
                                    for diff in differences:
                                        print(f"  • {diff}")

                                expected_str = self.format_value(result.expected)
                                actual_str = self.format_value(result.actual)
                                if isinstance(result.expected, (int, float, str, bool)) and isinstance(
                                    result.actual, (int, float, str, bool)
                                ):
                                    if str(expected_str) != str(actual_str):
                                        print(colored("\n📊 Comparison:", "magenta", attrs=["bold"]))
                                        diff = difflib.ndiff([str(expected_str)], [str(actual_str)])
                                        print("  " + "\n  ".join(diff))

                sys.exit(1)
            print("\n" + colored("Overall results:", "white", attrs=["bold"]))
            print(colored("═" * 80, "blue"))
            print(f"Total tests: {total_tests}")
            print(f"Passed tests: {colored(total_passed, 'green' if total_passed == total_tests else 'yellow')}")
            if total_failed > 0:
                print(f"Failed tests: {colored(total_failed, 'red')}")
            print(
                f"Success rate: {colored(f'{total_passed / total_tests * 100:.1f}%', 'green' if total_passed == total_tests else 'yellow')}"
            )

            if total_passed == total_tests:
                print(colored("\n✨ All tests passed successfully! ✨", "green", attrs=["bold"]))
                self.create_release_folder(results)
            else:
                print(colored(f"\n❌ {total_failed} tests failed", "red", attrs=["bold"]))

                if failed_tasks:
                    print("\n" + colored("Summary of tasks with failed tests:", "yellow", attrs=["bold"]))
                    print(colored("═" * 80, "blue"))
                    for task, stats in failed_tasks.items():
                        fail_rate = stats["failed"] / stats["total"] * 100
                        print(
                            f"{colored(task, 'cyan')} - failed {colored(stats['failed'], 'red')} of {stats['total']} tests ({fail_rate:.1f}%)"
                        )
                        print(f"  Files: {', '.join(stats['files'])}")

                # Now print all failed test details at the very end (non-verbose mode)
                if not verbose and failed_test_details:
                    print("\n" + colored("Detailed failed tests (grouped by task and file):", "white", attrs=["bold"]))
                    print(colored("═" * 80, "blue"))

                    for task, files in failed_test_details.items():
                        for display_name, tests in files.items():
                            for index, result in tests:
                                # 👇 print task + file for every failed test
                                print("\n" + colored("─" * 80, "blue"))
                                print(
                                    f"{colored('Task:', 'white', attrs=['bold'])} {colored(task, 'cyan', attrs=['bold'])}  "
                                    f"{colored('File:', 'white', attrs=['bold'])} {colored(display_name, 'cyan')}"
                                )
                                print(colored(f"Test #{index}: ❌ TEST FAILED", "red", attrs=["bold"]))

                                print(colored("\n📥 Arguments:", "cyan", attrs=["bold"]))
                                if not isinstance(result.arguments, (list, tuple)):
                                    print(f"  Argument: {self.format_value(result.arguments)}")
                                else:
                                    for j, arg in enumerate(result.arguments):
                                        print(f"  Argument {j + 1}: {self.format_value(arg)}")

                                print(colored("\n✓ Expected result:", "green", attrs=["bold"]))
                                print(f"  {self.format_value(result.expected, color='green')}")

                                print(colored("\n⨯ Actual result:", "red", attrs=["bold"]))
                                print(f"  {self.format_value(result.actual, color='red')}")

                                differences = self.find_difference(result.actual, result.expected)
                                if differences:
                                    print(colored("\n🔍 Difference details:", "yellow", attrs=["bold"]))
                                    for diff in differences:
                                        print(f"  • {diff}")

                                expected_str = self.format_value(result.expected)
                                actual_str = self.format_value(result.actual)
                                if isinstance(result.expected, (int, float, str, bool)) and isinstance(
                                    result.actual, (int, float, str, bool)
                                ):
                                    if str(expected_str) != str(actual_str):
                                        print(colored("\n📊 Comparison:", "magenta", attrs=["bold"]))
                                        diff = difflib.ndiff([str(expected_str)], [str(actual_str)])
                                        print("  " + "\n  ".join(diff))
                    print("\n" + colored("Detailed failed tests (grouped by task and file):", "white", attrs=["bold"]))
                    print(colored("═" * 80, "blue"))

                    for task, files in failed_test_details.items():
                        print(f"\n{colored('Task:', 'white', attrs=['bold'])} {colored(task, 'cyan', attrs=['bold'])}")
                        for display_name, tests in files.items():
                            print(f"\n{colored('File:', 'white', attrs=['bold'])} {colored(display_name, 'cyan')}")
                            for index, result in tests:
                                print("\n" + colored("─" * 80, "blue"))
                                print(colored(f"Test #{index}: ❌ TEST FAILED", "red", attrs=["bold"]))

                                print(colored("\n📥 Arguments:", "cyan", attrs=["bold"]))
                                if not isinstance(result.arguments, (list, tuple)):
                                    print(f"  Argument: {self.format_value(result.arguments)}")
                                else:
                                    for j, arg in enumerate(result.arguments):
                                        print(f"  Argument {j + 1}: {self.format_value(arg)}")

                                print(colored("\n✓ Expected result:", "green", attrs=["bold"]))
                                print(f"  {self.format_value(result.expected, color='green')}")

                                print(colored("\n⨯ Actual result:", "red", attrs=["bold"]))
                                print(f"  {self.format_value(result.actual, color='red')}")

                                differences = self.find_difference(result.actual, result.expected)
                                if differences:
                                    print(colored("\n🔍 Difference details:", "yellow", attrs=["bold"]))
                                    for diff in differences:
                                        print(f"  • {diff}")

                                expected_str = self.format_value(result.expected)
                                actual_str = self.format_value(result.actual)
                                if isinstance(result.expected, (int, float, str, bool)) and isinstance(
                                    result.actual, (int, float, str, bool)
                                ):
                                    if str(expected_str) != str(actual_str):
                                        print(colored("\n📊 Comparison:", "magenta", attrs=["bold"]))
                                        diff = difflib.ndiff([str(expected_str)], [str(actual_str)])
                                        print("  " + "\n  ".join(diff))

                print(f"\n{colored('Task:', 'white', attrs=['bold'])} {colored(task_name, 'cyan', attrs=['bold'])}")
                sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Run tests for solutions in TOML files")
    parser.add_argument("path", help="Path to TOML file or directory with TOML test files")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed results for all tests")
    parser.add_argument("--skip-assert-count", "-s", action="store_true", help="Skip check for minimum number of tests (30)")
    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' does not exist")
        sys.exit(1)

    runner = TestRunner(args.path, skip_assert_count=args.skip_assert_count)
    results = runner.run_tests()
    runner.print_results(results, verbose=args.verbose)


if __name__ == "__main__":
    main()
