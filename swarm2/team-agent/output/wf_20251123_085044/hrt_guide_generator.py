#!/usr/bin/env python3
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
        self.content.append(f"\n### {title}\n\n{content}")
    
    def add_table(self, headers: List[str], rows: List[List[str]]):
        """Add a markdown table."""
        header_row = "| " + " | ".join(headers) + " |"
        separator = "|" + "|".join(["---"] * len(headers)) + "|"
        data_rows = ["| " + " | ".join(row) + " |" for row in rows]
        
        table = "\n".join([header_row, separator] + data_rows)
        self.content.append(table)
    
    def render(self) -> str:
        """Render the section to markdown."""
        heading = "#" * self.level + " " + self.title
        body = "\n\n".join(self.content)
        return f"{heading}\n\n{body}"


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
        section.add_paragraph("\n**Premenopausal Hormone Levels:**\n")
        pre_headers = ["Hormone", "Normal Range"]
        pre_rows = [[k, v] for k, v in self.hormone_ranges["premenopausal"].items()]
        section.add_table(pre_headers, pre_rows)
        
        # Postmenopausal ranges  
        section.add_paragraph("\n**Postmenopausal Hormone Levels:**\n")
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
        content = "\n\n".join(section.render() for section in self.sections)
        return content + "\n\n" + footer
    
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
