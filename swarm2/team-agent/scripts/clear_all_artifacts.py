#!/usr/bin/env python3
"""
Clear all artifacts to start fresh.
"""
import shutil
from pathlib import Path

def clear_artifacts():
    """Clear all artifacts from team_output directory."""
    output_dir = Path(__file__).parent.parent / "team_output"

    if output_dir.exists():
        print(f"Clearing artifacts from {output_dir}")
        count = 0
        for item in output_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
                print(f"  ✓ Removed: {item.name}")
                count += 1
        print(f"\n✅ Cleared {count} workflow directories")
    else:
        print("team_output directory doesn't exist")


if __name__ == "__main__":
    print("=" * 60)
    print("CLEARING ALL ARTIFACTS")
    print("=" * 60)
    print()

    clear_artifacts()

    print()
    print("=" * 60)
    print("✅ ALL ARTIFACTS CLEARED")
    print("=" * 60)
    print("\nYou can now run fresh missions!")
    print("\nNote: Restart the backend to clear in-memory missions/workflows.")
