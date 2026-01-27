import os
from pathlib import Path

OUTPUT_FILE = "REPO_SNAPSHOT_FOR_REVIEW.txt"

INCLUDE_EXTENSIONS = {".py", ".md", ".txt"}
INCLUDE_DIRS = {"phases", "tests", "appendices", "docs"}
EXCLUDE_DIRS = {".git", "__pycache__", "venv", ".venv", "env", "node_modules", "assets", "data", "build", "dist"}

MAX_FILE_SIZE_KB = 400

def dump_repo(root: Path):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("===== REPO SNAPSHOT FOR TECHNICAL REVIEW =====\n\n")
        out.write(f"Root: {root.resolve()}\n\n")

        for dirpath, dirnames, filenames in os.walk(root):
            rel = Path(dirpath).relative_to(root)

            # only walk selected top-level dirs
            if rel.parts and rel.parts[0] not in INCLUDE_DIRS:
                dirnames[:] = []
                continue

            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

            for filename in sorted(filenames):
                ext = Path(filename).suffix.lower()
                if ext not in INCLUDE_EXTENSIONS:
                    continue

                filepath = Path(dirpath) / filename
                size_kb = filepath.stat().st_size / 1024
                if size_kb > MAX_FILE_SIZE_KB:
                    continue

                out.write(f"\n### FILE: {filepath.relative_to(root)}\n")
                out.write("-" * 70 + "\n")
                try:
                    out.write(filepath.read_text(encoding="utf-8", errors="replace"))
                except Exception as e:
                    out.write(f"[ERROR READING FILE: {e}]\n")
                out.write("\n" + "=" * 70 + "\n")

    print(f"✓ Snapshot written to {OUTPUT_FILE}")

if __name__ == "__main__":
    dump_repo(Path("."))
