import os
from pathlib import Path

# ========== CONFIG ==========
OUTPUT_FILE = "REPO_DUMP_FOR_REVIEW.txt"

INCLUDE_EXTENSIONS = {".py", ".md", ".json"}
EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    "venv",
    ".venv",
    "env",
    ".env",
    "node_modules",
    "assets",
    "data",
    "build",
    "dist"
}

MAX_FILE_SIZE_KB = 500  # safety cap
# ============================


def should_skip_dir(dirname: str) -> bool:
    return dirname in EXCLUDE_DIRS


def dump_repo(root: Path):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("===== REPO DUMP FOR REVIEW =====\n\n")
        out.write(f"Root directory: {root.resolve()}\n\n")

        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if not should_skip_dir(d)]

            for filename in sorted(filenames):
                ext = Path(filename).suffix
                if ext not in INCLUDE_EXTENSIONS:
                    continue

                filepath = Path(dirpath) / filename
                relpath = filepath.relative_to(root)

                size_kb = filepath.stat().st_size / 1024
                if size_kb > MAX_FILE_SIZE_KB:
                    out.write(f"\n### {relpath} (SKIPPED - too large: {size_kb:.1f} KB)\n\n")
                    continue

                out.write(f"\n### FILE: {relpath}\n")
                out.write("-" * 60 + "\n")

                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        out.write(f.read())
                except Exception as e:
                    out.write(f"[ERROR READING FILE: {e}]\n")

                out.write("\n" + "=" * 60 + "\n")

    print(f"\n✓ Repo dumped to {OUTPUT_FILE}")


if __name__ == "__main__":
    dump_repo(Path("."))
