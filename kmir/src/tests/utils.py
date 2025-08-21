from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    import pytest

# Point to the root tests directory
ROOT_DIR = Path(__file__).parent.parent.parent.parent
TESTS_DIR = ROOT_DIR / 'tests'
RUST_DIR = TESTS_DIR / 'rust'
SMIR_DIR = TESTS_DIR / 'smir'
EXPECTED_DIR = TESTS_DIR / 'expected'


def get_test_files() -> list[tuple[str, Path, Path]]:
    """Get all test files: (test_name, rust_file, smir_file)."""
    smir_files = list(SMIR_DIR.rglob('*.smir.json'))
    if not smir_files:
        return []

    test_files = []
    for smir_file in smir_files:
        # Get relative path from SMIR_DIR to smir_file
        rel_path = smir_file.relative_to(SMIR_DIR)
        # Construct corresponding rust file path
        rust_file = RUST_DIR / rel_path.with_suffix('.rs')

        # Generate test name from rust file path (remove .smir suffix)
        test_name = str(rel_path.with_suffix('')).replace('.smir', '')

        test_files.append((test_name, rust_file, smir_file))

    return test_files


# Test data for parametrization
TEST_FILES = get_test_files()


def filter_test_files(pattern: str) -> list[tuple[str, Path, Path]]:
    """Filter test files by regex pattern on test names.

    Args:
        pattern: Regular expression pattern to match against test names

    Returns:
        Filtered list of (test_name, rust_file, smir_file) tuples

    Example:
        # Get only tests containing 'intrinsic'
        intrinsic_tests = filter_test_files(r'intrinsic')

        # Get only tests starting with 'array'
        array_tests = filter_test_files(r'^array')

        # Get tests with specific pattern
        specific_tests = filter_test_files(r'arithmetic.*unchecked')
    """
    import re

    regex = re.compile(pattern)
    return [(name, rust_file, smir_file) for name, rust_file, smir_file in TEST_FILES if regex.search(name)]


def get_expected_path(request: pytest.FixtureRequest, file_type: Literal['json', 'txt']) -> Path:
    """Generate expected output path for a test using pytest request.

    Creates a path from tests/ to the actual test function being called.
    The test function name is added to the directory path but removed from the filename.
    """
    # Get the test file path relative to the project root
    test_file = Path(request.path)
    project_root = ROOT_DIR

    # Get relative path from project root to test file
    rel_path = test_file.relative_to(project_root)

    # Remove the 'kmir/src/tests/' prefix to get path from tests/ onwards
    if 'kmir/src/tests/' in str(rel_path):
        rel_path = Path(str(rel_path).replace('kmir/src/tests/', ''))

    # Get test node name (function name)
    test_name = request.node.name

    # Parse the test name to extract function name and parameters
    # Format: function_name[parameters] -> function_name and parameters
    if '[' in test_name and test_name.endswith(']'):
        function_name = test_name[: test_name.find('[')]
        parameters = test_name[test_name.find('[') + 1 : test_name.rfind(']')]
        safe_parameters = parameters.replace('/', '_').replace('\\', '_').replace(':', '_')
    else:
        function_name = test_name
        safe_parameters = ''

    # Build the expected directory path: tests/expected/ + relative_path + function_name
    expected_dir = EXPECTED_DIR / rel_path.parent / rel_path.stem / function_name

    # Create directory if it doesn't exist
    expected_dir.mkdir(parents=True, exist_ok=True)

    # Return path with parameters as filename, without function name in filename
    if safe_parameters:
        return expected_dir / f'{safe_parameters}.expected.{file_type}'
    else:
        return expected_dir / f'expected.{file_type}'
