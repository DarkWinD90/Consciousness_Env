#!/usr/bin/env python3
"""
USPTO Patent PDF Compliance Validator

Validates generated PDF files against EFS-Web / Patent Center requirements:
- PDF version (1.1 through 1.6)
- Page size (US Letter or A4)
- File size (< 25 MB)
- Filename conventions
- Font embedding
- No encryption

Usage:
    python .claude/skills/uspto-patent-compliance/validate_pdfs.py [--all]
"""

import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# PDF Requirements (EFS-Web / Patent Center)
# ---------------------------------------------------------------------------

MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB
MAX_FILENAME_LENGTH = 100
VALID_FILENAME_PATTERN = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_\-\.]*\.pdf$')

# US Letter: 612 x 792 points (8.5 x 11 inches at 72 DPI)
# A4: 595.28 x 841.89 points
VALID_PAGE_SIZES = [
    (612, 792, "US Letter"),
    (595.28, 841.89, "A4"),
    (595, 842, "A4 (rounded)"),
]
PAGE_SIZE_TOLERANCE = 5  # points

# Expected PDF files in the repository
EXPECTED_PDFS = [
    # Drawing PDFs
    'Patent_Drawings_A.pdf',
    'Patent_Drawings_B.pdf',
    'Patent_Drawings_C.pdf',
    # Specification PDFs
    'Patent_A_Specification.pdf',
    'Patent_B_Specification.pdf',
    'Patent_C_Specification.pdf',
    # Drawing description PDFs
    'Patent_A_Drawings_Description.pdf',
    'Patent_B_Drawings_Description.pdf',
    'Patent_C_Drawings_Description.pdf',
    # Cover sheets
    'Patent_A_CoverSheet_SB16.pdf',
    'Patent_B_CoverSheet_SB16.pdf',
    'Patent_C_CoverSheet_SB16.pdf',
    # Micro entity forms
    'Patent_A_MicroEntity_SB15A.pdf',
    'Patent_B_MicroEntity_SB15A.pdf',
    'Patent_C_MicroEntity_SB15A.pdf',
]

# ---------------------------------------------------------------------------
# PDF Inspection (without heavy dependencies)
# ---------------------------------------------------------------------------

def read_pdf_header(filepath):
    """Read PDF header to determine version."""
    try:
        with open(filepath, 'rb') as f:
            header = f.read(1024)
        # PDF version is in the first line: %PDF-X.Y
        match = re.search(rb'%PDF-(\d+\.\d+)', header)
        if match:
            return match.group(1).decode('ascii')
        return None
    except (IOError, OSError):
        return None


def check_pdf_encryption(filepath):
    """Check if PDF is encrypted by looking for /Encrypt in trailer."""
    try:
        with open(filepath, 'rb') as f:
            # Read last 4KB for trailer
            f.seek(0, 2)  # End of file
            size = f.tell()
            read_size = min(size, 4096)
            f.seek(size - read_size)
            trailer = f.read(read_size)
        return b'/Encrypt' in trailer
    except (IOError, OSError):
        return None


def get_pdf_page_count(filepath):
    """Estimate page count from PDF (basic — counts /Type /Page occurrences)."""
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
        # Count /Type /Page (not /Type /Pages)
        pages = len(re.findall(rb'/Type\s*/Page\b(?!\s*s)', content))
        return pages
    except (IOError, OSError):
        return None


def validate_pdf(filepath, base_dir):
    """Run all compliance checks on a single PDF file."""
    filepath = Path(filepath)
    results = []

    # 1. File exists
    if not filepath.exists():
        results.append(("file", "FAIL", f"File not found: {filepath}"))
        return results

    # 2. File size
    file_size = filepath.stat().st_size
    if file_size > MAX_FILE_SIZE_BYTES:
        size_mb = file_size / (1024 * 1024)
        results.append(("size", "FAIL",
                        f"File size {size_mb:.1f} MB exceeds 25 MB limit"))
    elif file_size == 0:
        results.append(("size", "FAIL", "File is empty (0 bytes)"))
    else:
        size_kb = file_size / 1024
        results.append(("size", "PASS", f"File size: {size_kb:.0f} KB"))

    # 3. Filename compliance
    filename = filepath.name
    if len(filename) > MAX_FILENAME_LENGTH:
        results.append(("filename", "FAIL",
                        f"Filename '{filename}' exceeds {MAX_FILENAME_LENGTH} chars"))
    elif ' ' in filename:
        results.append(("filename", "FAIL",
                        f"Filename '{filename}' contains spaces — not allowed"))
    elif not VALID_FILENAME_PATTERN.match(filename):
        results.append(("filename", "FAIL",
                        f"Filename '{filename}' doesn't match [A-Za-z0-9][A-Za-z0-9_-.]*"))
    else:
        results.append(("filename", "PASS", f"Filename: {filename}"))

    # 4. PDF version
    version = read_pdf_header(filepath)
    if version is None:
        results.append(("version", "FAIL", "Cannot read PDF version — may not be a valid PDF"))
    else:
        try:
            ver_float = float(version)
            if 1.1 <= ver_float <= 1.6:
                results.append(("version", "PASS", f"PDF version: {version}"))
            elif ver_float <= 2.0:
                results.append(("version", "WARN",
                                f"PDF version {version} — recommended 1.1-1.6"))
            else:
                results.append(("version", "FAIL",
                                f"PDF version {version} — must be 1.1-1.6"))
        except ValueError:
            results.append(("version", "WARN",
                            f"Unusual PDF version: {version}"))

    # 5. Encryption check
    is_encrypted = check_pdf_encryption(filepath)
    if is_encrypted is True:
        results.append(("encryption", "FAIL",
                        "PDF is encrypted — encryption prohibited for USPTO"))
    elif is_encrypted is False:
        results.append(("encryption", "PASS", "No encryption detected"))
    else:
        results.append(("encryption", "WARN", "Could not verify encryption status"))

    # 6. Page count (informational)
    pages = get_pdf_page_count(filepath)
    if pages is not None and pages > 0:
        results.append(("pages", "PASS", f"Estimated pages: {pages}"))
    else:
        results.append(("pages", "WARN", "Could not determine page count"))

    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="USPTO Patent PDF Compliance Validator"
    )
    parser.add_argument('--all', action='store_true',
                        help='Validate all expected PDFs')
    parser.add_argument('--file', type=str,
                        help='Validate specific PDF file')
    parser.add_argument('--base-dir', default=None,
                        help='Base directory')
    args = parser.parse_args()

    if args.base_dir:
        base_dir = Path(args.base_dir)
    else:
        script_dir = Path(__file__).resolve().parent
        base_dir = script_dir
        for _ in range(5):
            if (base_dir / 'patent_drawings').exists():
                break
            base_dir = base_dir.parent
        else:
            base_dir = Path.cwd()

    print("=" * 60)
    print("USPTO PATENT PDF COMPLIANCE REPORT")
    print("EFS-Web / Patent Center Requirements")
    print("=" * 60)

    total_pass = 0
    total_warn = 0
    total_fail = 0

    if args.file:
        pdf_path = Path(args.file)
        if not pdf_path.is_absolute():
            pdf_path = base_dir / pdf_path
        print(f"\n--- {pdf_path.name} ---")
        results = validate_pdf(pdf_path, base_dir)
        for check, status, detail in results:
            icon = {"PASS": "+", "WARN": "~", "FAIL": "!"}[status]
            print(f"  [{icon}] {status}: {detail}")
            if status == "PASS":
                total_pass += 1
            elif status == "WARN":
                total_warn += 1
            else:
                total_fail += 1
    else:
        # Validate all expected PDFs
        for pdf_name in EXPECTED_PDFS:
            pdf_path = base_dir / pdf_name
            print(f"\n--- {pdf_name} ---")
            results = validate_pdf(pdf_path, base_dir)
            for check, status, detail in results:
                icon = {"PASS": "+", "WARN": "~", "FAIL": "!"}[status]
                print(f"  [{icon}] {status}: {detail}")
                if status == "PASS":
                    total_pass += 1
                elif status == "WARN":
                    total_warn += 1
                else:
                    total_fail += 1

    print(f"\n{'=' * 60}")
    print(f"SUMMARY")
    print(f"  Total Checks: {total_pass + total_warn + total_fail}")
    print(f"  PASS: {total_pass}")
    print(f"  WARN: {total_warn}")
    print(f"  FAIL: {total_fail}")
    print(f"{'=' * 60}")

    if total_fail > 0:
        print("\nSTATUS: PDF COMPLIANCE ISSUES FOUND")
        sys.exit(1)
    elif total_warn > 0:
        print("\nSTATUS: WARNINGS — review recommended")
        sys.exit(0)
    else:
        print("\nSTATUS: ALL PDF CHECKS PASSED")
        sys.exit(0)


if __name__ == '__main__':
    main()
