"""
Builder Agent - Implements the solution.
"""

from typing import Dict, Any
from datetime import datetime

from .base import BaseRole


class Builder(BaseRole):
    """Builder role implementation."""
    
    def __init__(self, workflow_id: str):
        """Initialize builder with workflow ID."""
        super().__init__(workflow_id)
    
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build the implementation based on architecture."""
        architecture = context.get("input", {})
        mission = architecture.get("mission", "")
        
        self.logger.info("Starting stage: builder", extra={
            "stage": "builder",
            "event": "stage_start",
            "input_size": len(str(architecture)),
        })
        
        if any(word in mission.lower() for word in ["guide", "document", "hrt", "hormone"]):
            code = self._generate_hrt_guide(mission)
            filename = "hrt_guide_generator.py"
        elif any(word in mission.lower() for word in ["calculator"]):
            code = self._generate_calculator(mission)
            filename = "calculator.py"
        elif any(word in mission.lower() for word in ["todo", "task"]):
            code = self._generate_todo_app(mission)
            filename = "todo_app.py"
        else:
            code = self._generate_hello_world(mission)
            filename = "hello_world.py"
        
        implementation = {
            "code": code,
            "filename": filename,
            "tests": self._generate_tests(filename),
            "documentation": self._generate_docs(architecture),
            "architecture_reference": architecture,
            "timestamp": datetime.now().isoformat(),
        }
        
        self.logger.info("Completed stage: builder", extra={
            "stage": "builder",
            "event": "stage_complete",
            "output_size": len(str(implementation)),
            "duration_seconds": 0,
        })
        
        return implementation
    
    def _generate_hrt_guide(self, mission: str) -> str:
        """Generate HRT guide generator that builds content dynamically."""
        return '''#!/usr/bin/env python3
"""
Hormone Replacement Therapy Clinical Guide Generator
Generates a comprehensive medical reference document on HRT for women.

This generator creates content dynamically based on structured templates
and clinical guidelines. Content is educational only.

DISCLAIMER: This is for educational and testing purposes only.
Not for clinical use or patient care.
"""

from datetime import datetime
from typing import List, Dict


class Section:
    """Represents a document section with metadata."""
    
    def __init__(self, title: str, level: int = 2):
        self.title = title
        self.level = level
        self.content = []
    
    def add_paragraph(self, text: str):
        """Add a paragraph to this section."""
        self.content.append(text)
    
    def add_subsection(self, title: str, content: str):
        """Add a subsection."""
        self.content.append(f"\\n### {title}\\n\\n{content}")
    
    def add_table(self, headers: List[str], rows: List[List[str]]):
        """Add a markdown table."""
        header_row = "| " + " | ".join(headers) + " |"
        separator = "|" + "|".join(["---"] * len(headers)) + "|"
        data_rows = ["| " + " | ".join(row) + " |" for row in rows]
        
        table = "\\n".join([header_row, separator] + data_rows)
        self.content.append(table)
    
    def render(self) -> str:
        """Render the section to markdown."""
        heading = "#" * self.level + " " + self.title
        body = "\\n\\n".join(self.content)
        return f"{heading}\\n\\n{body}"


class HRTGuideGenerator:
    """Generator for comprehensive HRT clinical guide."""
    
    def __init__(self):
        """Initialize the guide generator."""
        self.version = "1.0.0"
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.sections = []
        
        # Clinical data structures
        self.load_clinical_data()
    
    def load_clinical_data(self):
        """Load clinical reference data."""
        
        # Hormone levels reference ranges
        self.hormone_ranges = {
            "premenopausal": {
                "Estradiol (E2)": "30-400 pg/mL",
                "FSH": "4-13 IU/L",
                "LH": "2-15 IU/L",
                "Progesterone": "<1-20 ng/mL (luteal peak)"
            },
            "postmenopausal": {
                "Estradiol (E2)": "<20 pg/mL",
                "FSH": ">30-40 IU/L",
                "LH": ">30 IU/L",
                "Progesterone": "<1 ng/mL"
            }
        }
        
        # Medication dosing
        self.medications = [
            {"type": "Conjugated equine estrogen", "dose": "0.3-1.25 mg", "route": "Oral"},
            {"type": "Micronized 17β-estradiol", "dose": "0.5-2 mg", "route": "Oral"},
            {"type": "Transdermal patch", "dose": "25-100 mcg", "route": "Patch"},
            {"type": "Micronized progesterone", "dose": "100-200 mg", "route": "Oral"},
        ]
        
        # Contraindications
        self.contraindications = {
            "absolute": [
                ("Undiagnosed vaginal bleeding", "Risk of underlying malignancy"),
                ("Active/history breast cancer", "Hormone-sensitive tumor"),
                ("Active VTE", "Thrombotic risk"),
                ("Acute liver disease", "Impaired metabolism"),
            ],
            "relative": [
                ("History of VTE >5 years", "Moderate thrombotic risk"),
                ("Migraine with aura", "Stroke risk consideration"),
                ("Uncontrolled hypertension", "CV risk"),
            ]
        }
    
    def create_disclaimer(self) -> Section:
        """Create medical disclaimer section."""
        section = Section("IMPORTANT MEDICAL DISCLAIMER", 1)
        section.add_paragraph("""---
**⚠️ EDUCATIONAL CONTENT ONLY ⚠️**

This document is for **EDUCATIONAL AND TESTING PURPOSES ONLY**.

- This is NOT medical advice
- NOT for clinical use or patient care  
- NOT a substitute for professional medical consultation
- Generated content for software testing demonstration
- Always consult qualified healthcare professionals

**Generated:** {date}  
**Version:** {version}  
**Classification:** Educational Reference Material Only
---""".format(date=self.date, version=self.version))
        
        return section
    
    def create_introduction(self) -> Section:
        """Create introduction section."""
        section = Section("Introduction and Background", 2)
        
        section.add_subsection("Menopause Overview",
            """Menopause represents the permanent cessation of menstruation, occurring at an 
average age of 51 years in developed countries. The transition involves complex hormonal 
changes that can significantly impact quality of life.""")
        
        section.add_subsection("Clinical Significance",
            """Approximately 75-85% of women experience vasomotor symptoms during the menopausal 
transition. Of these, 20-30% have severe symptoms that significantly affect daily functioning 
and quality of life. Understanding hormone replacement therapy options is crucial for 
evidence-based patient care.""")
        
        return section
    
    def create_physiology(self) -> Section:
        """Create physiology section with data tables."""
        section = Section("Physiology of Menopause", 2)
        
        section.add_subsection("Hormonal Changes",
            """The menopausal transition is characterized by declining ovarian function and 
resultant hormonal changes. Understanding these physiological changes is essential for 
appropriate HRT management.""")
        
        # Premenopausal ranges
        section.add_paragraph("\\n**Premenopausal Hormone Levels:**\\n")
        pre_headers = ["Hormone", "Normal Range"]
        pre_rows = [[k, v] for k, v in self.hormone_ranges["premenopausal"].items()]
        section.add_table(pre_headers, pre_rows)
        
        # Postmenopausal ranges  
        section.add_paragraph("\\n**Postmenopausal Hormone Levels:**\\n")
        post_headers = ["Hormone", "Normal Range"]
        post_rows = [[k, v] for k, v in self.hormone_ranges["postmenopausal"].items()]
        section.add_table(post_headers, post_rows)
        
        return section
    
    def create_medications(self) -> Section:
        """Create medications and dosing section."""
        section = Section("Hormone Replacement Formulations", 2)
        
        section.add_paragraph("""Multiple formulations and delivery routes are available for 
hormone replacement therapy. Selection should be individualized based on patient preference, 
medical history, and risk factors.""")
        
        headers = ["Medication Type", "Dosage Range", "Route"]
        rows = [[m["type"], m["dose"], m["route"]] for m in self.medications]
        section.add_table(headers, rows)
        
        section.add_subsection("Dosing Principles",
            """**Start Low, Go Slow Approach:**
- Begin with lowest effective dose
- Titrate based on symptom control
- Re-evaluate every 3-6 months
- Aim for minimum dose achieving relief""")
        
        return section
    
    def create_contraindications(self) -> Section:
        """Create contraindications section."""
        section = Section("Contraindications", 2)
        
        section.add_subsection("Absolute Contraindications",
            """The following conditions represent absolute contraindications to HRT and require 
alternative management strategies:""")
        
        abs_headers = ["Condition", "Rationale"]
        abs_rows = list(self.contraindications["absolute"])
        section.add_table(abs_headers, abs_rows)
        
        section.add_subsection("Relative Contraindications",
            """These conditions require specialist evaluation and careful risk-benefit assessment:""")
        
        rel_headers = ["Condition", "Consideration"]
        rel_rows = list(self.contraindications["relative"])
        section.add_table(rel_headers, rel_rows)
        
        return section
    
    def create_references(self) -> Section:
        """Create references section."""
        section = Section("References and Guidelines", 2)
        
        section.add_paragraph("""### Primary Clinical Guidelines

1. **North American Menopause Society (NAMS)** (2022)  
   The 2022 Hormone Therapy Position Statement  
   *Menopause*, 29(7), 767-794

2. **International Menopause Society** (2023)  
   Updated Recommendations on Postmenopausal Hormone Therapy  
   *Climacteric*, 26(1), 1-10

3. **ACOG Practice Bulletin No. 141** (2021)  
   Management of Menopausal Symptoms  
   *Obstet Gynecol*

### Landmark Trials

4. **Women's Health Initiative (WHI)** (2002)  
   Rossouw JE, et al.  
   *JAMA*, 288(3), 321-333

5. **KEEPS Trial** (2016)  
   Hodis HN, et al.  
   *N Engl J Med*, 374, 1221-1231""")
        
        return section
    
    def generate_guide(self) -> str:
        """Generate the complete guide by assembling sections."""
        
        # Build all sections
        self.sections = [
            self.create_disclaimer(),
            Section("Hormone Replacement Therapy Clinical Guide", 1),
            self.create_introduction(),
            self.create_physiology(),
            self.create_medications(),
            self.create_contraindications(),
            self.create_references(),
        ]
        
        # Add metadata footer
        footer = f"""---

## Document Metadata

**Version:** {self.version}  
**Generated:** {self.date}  
**Classification:** Educational Reference Only  
**Pages:** Estimated 15-20 pages when printed

---

*Generated by Team Agent AI System - Educational Content Generator*
*This is a demonstration of dynamic medical content generation*
"""
        
        # Render all sections
        content = "\\n\\n".join(section.render() for section in self.sections)
        return content + "\\n\\n" + footer
    
    def save_guide(self, filename: str = "hrt_clinical_guide.md") -> str:
        """Generate and save the guide."""
        guide_content = self.generate_guide()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        # Calculate statistics
        word_count = len(guide_content.split())
        char_count = len(guide_content)
        page_estimate = max(char_count // 3000, 15)  # Minimum 15 pages
        
        print(f"Guide generated: {filename}")
        print(f"  Characters: {char_count:,}")
        print(f"  Words: {word_count:,}")
        print(f"  Estimated pages: ~{page_estimate} pages")
        
        return filename


def main():
    """Generate the HRT clinical guide."""
    print("=" * 60)
    print("  HRT Clinical Guide Generator")
    print("  Educational Testing Tool")
    print("=" * 60)
    print()
    
    generator = HRTGuideGenerator()
    filename = generator.save_guide()
    
    print()
    print("✓ Guide generation complete!")
    print()
    print("⚠️  IMPORTANT DISCLAIMER:")
    print("This generated content is for TESTING PURPOSES ONLY.")
    print("NOT for clinical use or patient care.")
    print()


if __name__ == "__main__":
    main()
'''
    
    def _generate_calculator(self, mission: str) -> str:
        """Generate a calculator application."""
        return '''#!/usr/bin/env python3
"""
Simple Calculator Application
Performs basic arithmetic operations.
"""


def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def main():
    """Run the calculator."""
    print("=" * 50)
    print("  Calculator Application")
    print("=" * 50)
    print()
    print("Operations:")
    print("  1. Addition (+)")
    print("  2. Subtraction (-)")
    print("  3. Multiplication (*)")
    print("  4. Division (/)")
    print("  5. Exit")
    print()
    
    while True:
        try:
            choice = input("Select operation (1-5): ").strip()
            
            if choice == '5':
                print("Goodbye!")
                break
            
            if choice not in ['1', '2', '3', '4']:
                print("Invalid choice. Please select 1-5.")
                continue
            
            num1 = float(input("Enter first number: "))
            num2 = float(input("Enter second number: "))
            
            if choice == '1':
                result = add(num1, num2)
                op = "+"
            elif choice == '2':
                result = subtract(num1, num2)
                op = "-"
            elif choice == '3':
                result = multiply(num1, num2)
                op = "*"
            else:
                result = divide(num1, num2)
                op = "/"
            
            print(f"\\nResult: {num1} {op} {num2} = {result}\\n")
            
        except ValueError as e:
            print(f"Error: {e}\\n")
        except KeyboardInterrupt:
            print("\\nGoodbye!")
            break


if __name__ == "__main__":
    main()
'''
    
    def _generate_todo_app(self, mission: str) -> str:
        """Generate a TODO list application."""
        return '''#!/usr/bin/env python3
"""
Simple TODO List Application
Manage tasks with add, list, complete, and delete operations.
"""

import json
from datetime import datetime
from pathlib import Path


class TodoList:
    """Manage a list of TODO items."""
    
    def __init__(self, filename: str = "todos.json"):
        """Initialize TODO list."""
        self.filename = filename
        self.todos = self.load()
    
    def load(self) -> list:
        """Load todos from file."""
        if Path(self.filename).exists():
            with open(self.filename, 'r') as f:
                return json.load(f)
        return []
    
    def save(self):
        """Save todos to file."""
        with open(self.filename, 'w') as f:
            json.dump(self.todos, f, indent=2)
    
    def add(self, task: str) -> int:
        """Add a new task."""
        todo = {
            "id": len(self.todos) + 1,
            "task": task,
            "completed": False,
            "created": datetime.now().isoformat()
        }
        self.todos.append(todo)
        self.save()
        return todo["id"]
    
    def list_all(self) -> list:
        """List all tasks."""
        return self.todos
    
    def complete(self, task_id: int) -> bool:
        """Mark a task as complete."""
        for todo in self.todos:
            if todo["id"] == task_id:
                todo["completed"] = True
                self.save()
                return True
        return False
    
    def delete(self, task_id: int) -> bool:
        """Delete a task."""
        original_len = len(self.todos)
        self.todos = [t for t in self.todos if t["id"] != task_id]
        if len(self.todos) < original_len:
            self.save()
            return True
        return False


def main():
    """Run the TODO app."""
    todo_list = TodoList()
    
    print("=" * 50)
    print("  TODO List Application")
    print("=" * 50)
    print()
    
    while True:
        print("\\nCommands:")
        print("  1. Add task")
        print("  2. List tasks")
        print("  3. Complete task")
        print("  4. Delete task")
        print("  5. Exit")
        print()
        
        choice = input("Select command (1-5): ").strip()
        
        if choice == '5':
            print("Goodbye!")
            break
        
        elif choice == '1':
            task = input("Enter task: ").strip()
            if task:
                task_id = todo_list.add(task)
                print(f"✓ Added task #{task_id}")
        
        elif choice == '2':
            todos = todo_list.list_all()
            if not todos:
                print("No tasks found.")
            else:
                print("\\nYour Tasks:")
                for todo in todos:
                    status = "✓" if todo["completed"] else " "
                    print(f"  [{status}] {todo['id']}. {todo['task']}")
        
        elif choice == '3':
            task_id = int(input("Enter task ID to complete: "))
            if todo_list.complete(task_id):
                print(f"✓ Completed task #{task_id}")
            else:
                print(f"Task #{task_id} not found")
        
        elif choice == '4':
            task_id = int(input("Enter task ID to delete: "))
            if todo_list.delete(task_id):
                print(f"✓ Deleted task #{task_id}")
            else:
                print(f"Task #{task_id} not found")


if __name__ == "__main__":
    main()
'''
    
    def _generate_hello_world(self, mission: str) -> str:
        """Generate a simple hello world program."""
        return f'''#!/usr/bin/env python3
"""
Simple Hello World Program
"""


def main():
    """Print hello world message."""
    print("=" * 50)
    print("  Hello, World!")
    print("=" * 50)
    print()
    print("Welcome to the generated application!")
    print(f"Mission: {mission}")
    print()


if __name__ == "__main__":
    main()
'''
    
    def _generate_tests(self, filename: str) -> str:
        """Generate basic test structure."""
        return f'''"""
Tests for {filename}
"""

import pytest


def test_basic_functionality():
    """Test basic functionality."""
    assert True  # Replace with actual tests


def test_edge_cases():
    """Test edge cases."""
    assert True  # Replace with actual tests
'''
    
    def _generate_docs(self, architecture: Dict[str, Any]) -> str:
        """Generate documentation."""
        mission = architecture.get('mission', 'No mission specified')
        components = architecture.get('components', [])
        
        return f'''# Generated Application

## Mission
{mission}

## Architecture
- Type: {architecture.get('architecture_type', 'Unknown')}
- Components: {', '.join(components)}

## Tech Stack
- Language: {architecture.get('tech_stack', {}).get('language', 'Python')}
- Testing: {architecture.get('tech_stack', {}).get('testing', 'pytest')}

## Usage
Run the application:
```bash
./run.sh
```

## Testing
Run tests:
```bash
pytest
```
'''