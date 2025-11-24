#!/bin/bash
# Team Agent Quick Start

echo "🚀 Team Agent Quick Start"
echo "=========================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Run tests
echo ""
echo "Running tests..."
python3 examples/run_capability_tests.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
    echo ""
    echo "Try it out:"
    echo "  python3 -c \"from swarms.team_agent.orchestrator import Orchestrator; o = Orchestrator(); print(o.execute('Generate hormone replacement therapy guide'))\""
else
    echo ""
    echo "❌ Tests failed. Check output above."
    exit 1
fi
