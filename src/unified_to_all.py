# Copyright 2025 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""
Unified to All Formats Converter

Converts unified markdown format to all IDE formats (Cursor, Windsurf, Copilot).
Single source of truth for AI coding rules.
"""

from pathlib import Path

from converter import RuleConverter
from formats import CursorFormat, WindsurfFormat, CopilotFormat
from utils import get_version_from_pyproject


def convert_rules(input_path: str, output_dir: str = ".") -> dict[str, list[str]]:
    """
    Convert rule file(s) to all supported IDE formats using RuleConverter.

    Args:
        input_path: Path to a single .md file or folder containing .md files
        output_dir: Output directory (default: current directory)

    Returns:
        Dictionary with 'success' and 'errors' lists:
        {
            "success": ["rule1.md", "rule2.md"],
            "errors": ["rule3.md: error message"]
        }

    Example:
        results = convert_rules("rules/", "/output/path")
        print(f"Converted {len(results['success'])} rules")
    """
    version = get_version_from_pyproject()

    # Specify all formats that should be generated here
    all_formats = [
        CursorFormat(version),
        WindsurfFormat(version),
        CopilotFormat(version),
    ]

    converter = RuleConverter(formats=all_formats)
    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(f"{input_path} does not exist")

    # Determine files to process
    if path.is_file():
        if path.suffix != ".md":
            raise ValueError(f"{input_path} is not a .md file")
        files_to_process = [path]
        print(f"Converting file: {path.name}")
    else:
        files_to_process = list(path.glob("*.md"))
        if not files_to_process:
            raise ValueError(f"No .md files found in {input_path}")
        print(f"Converting {len(files_to_process)} files from: {path.name}")

    # Setup output directory
    output_base = Path(output_dir)
    ide_rules_dir = output_base / "ide_rules"

    results = {"success": [], "errors": []}

    # Process each file
    for md_file in files_to_process:
        try:
            # Convert the file (raises exceptions on error)
            result = converter.convert(md_file)

            # Write each format
            output_files = []
            for format_name, output in result.outputs.items():
                # Construct output path
                output_file = (
                    ide_rules_dir
                    / output.subpath
                    / f"{result.basename}{output.extension}"
                )

                # Create directory if it doesn't exist and write file
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text(output.content, encoding="utf-8")
                output_files.append(output_file.name)

            print(f"Success: {result.filename} → {', '.join(output_files)}")
            results["success"].append(result.filename)

        except FileNotFoundError as e:
            error_msg = f"{md_file.name}: File not found - {e}"
            print(f"Error: {error_msg}")
            results["errors"].append(error_msg)

        except ValueError as e:
            error_msg = f"{md_file.name}: Validation error - {e}"
            print(f"Error: {error_msg}")
            results["errors"].append(error_msg)

        except Exception as e:
            error_msg = f"{md_file.name}: Unexpected error - {e}"
            print(f"Error: {error_msg}")
            results["errors"].append(error_msg)

    # Summary
    print(
        f"\nResults: {len(results['success'])} success, {len(results['errors'])} errors"
    )

    return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python unified_to_all.py <input_file_or_folder> [output_dir]")
        print("Examples:")
        print("  python unified_to_all.py my-rule.md")
        print("  python unified_to_all.py unified_rules/")
        print("  python unified_to_all.py my-rule.md /output/path")
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    results = convert_rules(input_path, output_dir)

    if results["errors"]:
        sys.exit(1)
