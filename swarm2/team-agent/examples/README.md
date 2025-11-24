# Team Agent Examples

Collection of example scripts demonstrating Team Agent capabilities.

## Quick Start

### 1. Simple Demo
Run a single mission with minimal output:

```bash
python examples/simple_demo.py
```

### 2. Interactive Demo
Chat-style interface for building multiple applications:

```bash
python examples/interactive_demo.py
```

### 3. Mission Demo (Full Details)
Detailed output with quality metrics:

```bash
# Simple text mission
python examples/mission_demo.py --simple

# YAML mission file
python examples/mission_demo.py --yaml missions/calculator.yaml

# List available missions
python examples/mission_demo.py --list
```

### 4. Batch Processing
Process multiple missions automatically:

```bash
python examples/batch_demo.py
```

### 5. Quick Test
Verify system is working:

```bash
python examples/quick_test.py
```

## Example Missions

### Calculator
```bash
python examples/simple_demo.py
# When prompted: "Build a calculator with add, subtract, multiply, divide"
```

### TODO App
```bash
python examples/interactive_demo.py
# Type: "Create a TODO list application"
```

### File Organizer
```bash
python examples/mission_demo.py --simple
# When prompted: "Build a file organizer that sorts files by extension"
```

## Output Structure

Generated code is saved to:
```
output/
└── wf_YYYYMMDD_HHMMSS/
    ├── <generated_file>.py
    ├── README.md
    └── run.sh
```

## Next Steps

1. Try the interactive demo
2. Create custom mission YAML files
3. Check the output directory for generated code
4. Review workflow tapes in `data/tapes/`