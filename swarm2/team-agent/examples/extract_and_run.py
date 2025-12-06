"""
Extract generated code from workflow tapes and execute it.
"""

import json
import sys
from pathlib import Path
from typing import Optional


def find_latest_tape() -> Optional[Path]:
    """Find the most recent workflow tape."""
    tape_dir = Path("data/tapes")
    if not tape_dir.exists():
        print(f"❌ Tape directory not found: {tape_dir}")
        return None
    
    tapes = sorted(tape_dir.glob("wf_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return tapes[0] if tapes else None


def extract_code_from_tape(tape_path: Path) -> Optional[str]:
    """Extract generated code from tape."""
    try:
        with open(tape_path) as f:
            tape = json.load(f)
        
        # Navigate to builder output
        builder_output = tape.get("stages", {}).get("builder", {}).get("output", {})
        code = builder_output.get("code", "")
        
        if not code:
            print("❌ No code found in tape")
            return None
        
        return code
    
    except Exception as e:
        print(f"❌ Error reading tape: {e}")
        return None


def save_code(code: str, filename: str = "generated_code.py") -> Path:
    """Save extracted code to file."""
    output_path = Path(filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(code)
    
    return output_path


def main():
    """Extract and optionally run the generated code."""
    print("=" * 60)
    print("  Code Extractor & Runner")
    print("=" * 60)
    print()
    
    # Find latest tape
    print("🔍 Finding latest workflow tape...")
    tape_path = find_latest_tape()
    
    if not tape_path:
        print("❌ No workflow tapes found!")
        print("   Run a mission first with: python examples/mission_demo.py")
        sys.exit(1)
    
    print(f"✓ Found: {tape_path.name}")
    print()
    
    # Extract code
    print("📄 Extracting generated code...")
    code = extract_code_from_tape(tape_path)
    
    if not code:
        sys.exit(1)
    
    print(f"✓ Extracted {len(code)} characters")
    print(f"  Lines: {len(code.splitlines())}")
    print()
    
    # Determine filename from tape
    with open(tape_path) as f:
        tape = json.load(f)
    
    mission = tape.get("mission", "")
    
    # Determine output filename based on mission
    if "hormone" in mission.lower() or "hrt" in mission.lower():
        filename = "hrt_guide_generator.py"
    elif "calculator" in mission.lower():
        filename = "calculator.py"
    elif "todo" in mission.lower():
        filename = "todo.py"
    else:
        filename = "main.py"
    
    # Save code
    print(f"💾 Saving to: {filename}")
    output_path = save_code(code, filename)
    print(f"✓ Saved!")
    print()
    
    # Ask to run
    response = input(f"▶️  Run {filename} now? (y/n): ").strip().lower()
    
    if response == 'y':
        print()
        print("=" * 60)
        print(f"  Running: {filename}")
        print("=" * 60)
        print()
        
        import subprocess
        result = subprocess.run([sys.executable, str(output_path)])
        
        print()
        print("=" * 60)
        print(f"  Exit code: {result.returncode}")
        print("=" * 60)
    else:
        print()
        print(f"ℹ️  To run later: python {filename}")
    
    print()
    print("✅ Done!")


if __name__ == "__main__":
    main()