#!/usr/bin/env python3
"""
HRT Guide Generator Script

Generates a comprehensive Hormone Replacement Therapy informational guide.
This is NOT medical advice - for educational purposes only.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from swarms.team_agent.orchestrator import Orchestrator


def generate_hrt_guide():
    """Generate the HRT guide using the team agent workflow."""
    
    mission = """
    Generate a comprehensive 20-page Hormone Replacement Therapy (HRT) 
    informational guide with the following requirements:
    
    1. DISCLAIMERS (Required):
       - Clear statement that this is NOT medical advice
       - Recommendation to consult healthcare providers
       - Statement that this is supplemental educational information only
    
    2. CONTENT SECTIONS:
       - Executive Summary
       - Introduction to HRT
       - Types of Hormone Replacement Therapy
         * Estrogen therapy
         * Combined estrogen-progestogen therapy
         * Testosterone therapy
         * Bioidentical hormones
       - Indications and Uses
         * Menopause symptom management
         * Premature ovarian insufficiency
         * Gender-affirming care overview
         * Post-surgical hormone replacement
       - Benefits and Risks
         * Evidence-based benefits
         * Known risks and contraindications
         * Risk mitigation strategies
       - Administration Methods
         * Oral medications
         * Transdermal patches and gels
         * Injections
         * Implants
       - Monitoring and Follow-up
         * Baseline assessments
         * Ongoing monitoring schedules
         * Lab work recommendations
       - Special Populations
         * Cardiovascular considerations
         * History of cancer
         * Thrombotic risk factors
       - Frequently Asked Questions
       - Glossary of Terms
       - References and Citations
    
    3. CITATION REQUIREMENTS:
       - Cite peer-reviewed sources
       - Include publication dates
       - Reference major medical guidelines (NAMS, Endocrine Society, etc.)
    
    4. FORMAT:
       - Professional medical document styling
       - Clear headings and subheadings
       - Tables for comparison data
       - 20 pages target length
    """
    
    # Create output directory
    output_dir = Path("output/hrt_guide")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize orchestrator
    orchestrator = Orchestrator(output_dir=str(output_dir))
    
    print("=" * 60)
    print("HRT GUIDE GENERATOR")
    print("=" * 60)
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Output directory: {output_dir.absolute()}")
    print()
    
    # Execute the workflow
    result = orchestrator.execute(mission)
    
    print()
    print("=" * 60)
    print("WORKFLOW COMPLETE")
    print("=" * 60)
    print(f"Workflow ID: {result.get('workflow_id', 'N/A')}")
    print(f"Status: {result.get('status', 'N/A')}")
    
    return result, output_dir


def create_pdf_from_markdown(markdown_content: str, output_path: Path) -> bool:
    """
    Convert markdown content to PDF.
    Uses fpdf2 (pure Python, no native dependencies).
    """
    
    # Use fpdf2 - pure Python, no native deps
    try:
        from fpdf import FPDF
        
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Track if we're in a table
        in_table = False
        table_rows = []
        
        for line in markdown_content.split('\n'):
            line = line.rstrip()
            
            # Skip HTML div tags
            if line.strip().startswith('<div') or line.strip().startswith('</div'):
                continue
            
            # Handle headers
            if line.startswith('# '):
                pdf.set_font("Helvetica", 'B', 18)
                pdf.set_text_color(44, 62, 80)
                pdf.cell(0, 12, line[2:], ln=True)
                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Helvetica", size=11)
            elif line.startswith('## '):
                pdf.ln(5)
                pdf.set_font("Helvetica", 'B', 14)
                pdf.set_text_color(52, 73, 94)
                pdf.cell(0, 10, line[3:], ln=True)
                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Helvetica", size=11)
            elif line.startswith('### '):
                pdf.ln(3)
                pdf.set_font("Helvetica", 'B', 12)
                pdf.set_text_color(127, 140, 141)
                pdf.cell(0, 8, line[4:], ln=True)
                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Helvetica", size=11)
            elif line.startswith('**') and line.endswith('**'):
                # Bold line
                pdf.set_font("Helvetica", 'B', 11)
                pdf.multi_cell(0, 6, line.strip('*'))
                pdf.set_font("Helvetica", size=11)
            elif line.startswith('- '):
                # Bullet point
                pdf.cell(10, 6, chr(149))  # bullet character
                pdf.multi_cell(0, 6, line[2:])
            elif line.startswith('*Source:') or line.startswith('*©'):
                # Citation/source - italic and smaller
                pdf.set_font("Helvetica", 'I', 9)
                pdf.set_text_color(100, 100, 100)
                pdf.multi_cell(0, 5, line.strip('*'))
                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Helvetica", size=11)
            elif line.startswith('|') and '|' in line[1:]:
                # Table row
                if not in_table:
                    in_table = True
                    table_rows = []
                # Skip separator rows
                if '---' not in line:
                    cells = [c.strip() for c in line.split('|')[1:-1]]
                    table_rows.append(cells)
            elif in_table and not line.startswith('|'):
                # End of table - render it
                if table_rows:
                    _render_table(pdf, table_rows)
                    table_rows = []
                in_table = False
                if line.strip():
                    pdf.multi_cell(0, 6, line)
            elif line.strip() == '---':
                # Horizontal rule
                pdf.ln(3)
                pdf.set_draw_color(200, 200, 200)
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                pdf.ln(3)
            elif line.strip():
                # Regular text - handle inline formatting
                clean_line = line.replace('**', '').replace('*', '')
                pdf.multi_cell(0, 6, clean_line)
            else:
                pdf.ln(3)
        
        # Handle any remaining table
        if table_rows:
            _render_table(pdf, table_rows)
        
        pdf.output(str(output_path))
        print(f"PDF created: {output_path}")
        return True
        
    except ImportError:
        print("fpdf2 not available. Install with: pip install fpdf2")
        return False
    except Exception as e:
        print(f"PDF creation failed: {e}")
        return False


def _render_table(pdf, rows):
    """Render a table in the PDF."""
    if not rows:
        return
    
    pdf.ln(3)
    
    # Calculate column widths
    num_cols = len(rows[0]) if rows else 0
    if num_cols == 0:
        return
    
    col_width = 180 / num_cols
    
    # Header row
    pdf.set_font("Helvetica", 'B', 10)
    pdf.set_fill_color(52, 152, 219)
    pdf.set_text_color(255, 255, 255)
    
    for cell in rows[0]:
        pdf.cell(col_width, 7, cell[:25], border=1, fill=True)
    pdf.ln()
    
    # Data rows
    pdf.set_font("Helvetica", size=10)
    pdf.set_text_color(0, 0, 0)
    
    for i, row in enumerate(rows[1:]):
        if i % 2 == 0:
            pdf.set_fill_color(242, 242, 242)
        else:
            pdf.set_fill_color(255, 255, 255)
        
        for cell in row:
            pdf.cell(col_width, 6, cell[:25], border=1, fill=True)
        pdf.ln()
    
    pdf.ln(3)


def generate_full_hrt_content() -> str:
    """Generate the full HRT guide content with proper structure."""
    
    content = """
# Hormone Replacement Therapy (HRT)
## A Comprehensive Informational Guide

---

<div class="disclaimer">

## ⚠️ IMPORTANT DISCLAIMERS

**THIS DOCUMENT IS NOT MEDICAL ADVICE**

This guide is provided for **educational and informational purposes only**. It is not intended to be a substitute for professional medical advice, diagnosis, or treatment.

- **Always seek the advice of your physician** or other qualified health provider with any questions you may have regarding a medical condition or treatment.
- **Never disregard professional medical advice** or delay in seeking it because of something you have read in this guide.
- **Individual responses to hormone therapy vary significantly.** What works for one person may not be appropriate for another.
- **This guide does not establish a doctor-patient relationship.**

If you think you may have a medical emergency, call your doctor or emergency services immediately.

</div>

---

## Table of Contents

1. Executive Summary
2. Introduction to Hormone Replacement Therapy
3. Types of Hormone Replacement Therapy
4. Indications and Clinical Uses
5. Benefits of HRT
6. Risks and Contraindications
7. Administration Methods
8. Monitoring and Follow-up Care
9. Special Populations and Considerations
10. Frequently Asked Questions
11. Glossary of Terms
12. References and Citations

---

## 1. Executive Summary

Hormone Replacement Therapy (HRT) refers to medical treatment that supplements or replaces hormones that the body is no longer producing in sufficient quantities. This guide provides an overview of HRT options, their uses, benefits, risks, and monitoring requirements.

**Key Points:**
- HRT is used primarily to manage symptoms of menopause, hormone deficiencies, and in gender-affirming care
- Multiple formulations and delivery methods are available
- Treatment should be individualized based on patient history, symptoms, and risk factors
- Regular monitoring is essential for safe, effective therapy
- Ongoing research continues to refine our understanding of HRT benefits and risks

---

## 2. Introduction to Hormone Replacement Therapy

### 2.1 What is HRT?

Hormone Replacement Therapy encompasses treatments that provide exogenous hormones to supplement or replace endogenous hormone production. The primary hormones involved include:

- **Estrogens** (estradiol, estrone, estriol)
- **Progestogens** (progesterone, progestins)
- **Androgens** (testosterone, DHEA)

### 2.2 Historical Context

HRT has evolved significantly since its introduction in the 1940s:

| Decade | Development |
|--------|-------------|
| 1940s | Introduction of conjugated equine estrogens |
| 1970s | Recognition of endometrial cancer risk with unopposed estrogen |
| 1980s | Addition of progestogens for endometrial protection |
| 2002 | WHI study publication changes prescribing patterns |
| 2010s+ | Refined understanding of timing, formulation, and individualization |

*Source: Stuenkel CA, et al. Treatment of Symptoms of the Menopause. J Clin Endocrinol Metab. 2015;100(11):3975-4011.*

### 2.3 Physiology of Hormone Decline

The decline in hormone production varies by cause:

**Menopause:**
- Average age of onset: 51 years
- Characterized by 12 consecutive months without menstruation
- Estradiol levels decline by 85-90%
- FSH levels rise significantly

**Premature Ovarian Insufficiency:**
- Occurs before age 40
- Affects approximately 1% of women
- May be idiopathic, genetic, autoimmune, or iatrogenic

*Source: NAMS. The 2022 Hormone Therapy Position Statement. Menopause. 2022;29(7):767-794.*

---

## 3. Types of Hormone Replacement Therapy

### 3.1 Estrogen Therapy (ET)

Estrogen-only therapy is appropriate for individuals without a uterus.

**Common Formulations:**

| Type | Examples | Notes |
|------|----------|-------|
| Conjugated Equine Estrogens | Premarin | Derived from pregnant mare urine |
| 17β-Estradiol | Estrace, Climara | Bioidentical to human estrogen |
| Ethinyl Estradiol | Various | More potent, typically in contraceptives |
| Estetrol (E4) | Newer formulation | Selective estrogen activity |

### 3.2 Combined Estrogen-Progestogen Therapy (EPT)

Required for individuals with an intact uterus to prevent endometrial hyperplasia.

**Regimens:**

- **Continuous Combined:** Daily estrogen + progestogen
- **Cyclic/Sequential:** Daily estrogen + progestogen 12-14 days/month
- **Long-Cycle:** Progestogen every 3 months (less common)

**Progestogen Options:**

| Category | Examples | Characteristics |
|----------|----------|-----------------|
| Progesterone | Prometrium (micronized) | Bioidentical, favorable lipid effects |
| Progestins | MPA, norethindrone | Synthetic, various metabolic effects |
| Combination | Bazedoxifene + CEE | Tissue-selective complex |

*Source: Endocrine Society Clinical Practice Guideline. Treatment of Symptoms of the Menopause. 2015.*

### 3.3 Testosterone Therapy

May be considered for:
- Hypoactive sexual desire disorder (HSDD)
- Well-being in some individuals
- Gender-affirming care (masculinizing therapy)

**Important Considerations:**
- No FDA-approved testosterone products for women in the US
- Off-label use with careful monitoring
- Global consensus statement supports use for HSDD

*Source: Davis SR, et al. Global Consensus Position Statement on the Use of Testosterone Therapy for Women. J Clin Endocrinol Metab. 2019;104(10):4660-4666.*

### 3.4 Bioidentical Hormones

**Definition:** Hormones that are chemically identical to those produced by the human body.

**FDA-Approved Bioidentical Options:**
- 17β-estradiol (various forms)
- Micronized progesterone (Prometrium)

<div class="warning">

**Caution Regarding Compounded Bioidentical Hormones:**

The Endocrine Society, NAMS, and ACOG advise caution with custom-compounded hormone preparations due to:
- Variable potency and purity
- Lack of FDA oversight
- Unsubstantiated claims of safety advantages
- Limited pharmacokinetic data

*Source: NAMS. The 2022 Hormone Therapy Position Statement.*

</div>

---

## 4. Indications and Clinical Uses

### 4.1 Vasomotor Symptoms (VMS)

Hot flashes and night sweats are the most common indication for HRT.

**Efficacy Data:**
- HRT reduces VMS frequency by 75-95%
- Improvement typically seen within 4 weeks
- Low-dose options effective for many patients

*Source: Maclennan AH, et al. Oral oestrogen and combined oestrogen/progestogen therapy versus placebo for hot flushes. Cochrane Database Syst Rev. 2004.*

### 4.2 Genitourinary Syndrome of Menopause (GSM)

Includes:
- Vaginal dryness and atrophy
- Dyspareunia
- Urinary symptoms

**Treatment Options:**
- Local (vaginal) estrogen: First-line for isolated GSM
- Systemic HRT: Addresses GSM plus other symptoms
- DHEA vaginal inserts (Intrarosa)
- Ospemifene (Osphena): Non-estrogen option

### 4.3 Bone Health

**Osteoporosis Prevention:**
- HRT is FDA-approved for osteoporosis prevention
- Reduces fracture risk by 20-40%
- Benefits persist only during use

*Source: Rossouw JE, et al. Postmenopausal hormone therapy and risk of cardiovascular disease by age and years since menopause. JAMA. 2007;297(13):1465-1477.*

### 4.4 Premature Ovarian Insufficiency (POI)

**Recommendations:**
- HRT recommended until average age of menopause (~51)
- Higher doses may be needed than standard menopausal HRT
- Important for bone, cardiovascular, and cognitive health

### 4.5 Gender-Affirming Hormone Therapy

<div class="disclaimer">

**Note:** Gender-affirming care is a specialized field requiring providers with specific expertise. This section provides general educational information only.

</div>

**Feminizing Therapy:**
- Estrogen (estradiol)
- Anti-androgens (spironolactone, cyproterone acetate, GnRH agonists)
- Progesterone (role debated)

**Masculinizing Therapy:**
- Testosterone (various formulations)

*Source: Hembree WC, et al. Endocrine Treatment of Gender-Dysphoric/Gender-Incongruent Persons: An Endocrine Society Clinical Practice Guideline. J Clin Endocrinol Metab. 2017;102(11):3869-3903.*

---

## 5. Benefits of HRT

### 5.1 Symptom Relief

| Symptom | Efficacy | Evidence Level |
|---------|----------|----------------|
| Hot flashes | 75-95% reduction | High |
| Night sweats | 75-95% reduction | High |
| Vaginal dryness | 80-90% improvement | High |
| Sleep disturbance | Moderate improvement | Moderate |
| Mood symptoms | Variable improvement | Moderate |

### 5.2 Bone Health Benefits

- 20-40% reduction in vertebral fractures
- 20-40% reduction in hip fractures
- Benefits require ongoing therapy

### 5.3 Cardiovascular Considerations

**The "Timing Hypothesis":**

Evidence suggests cardiovascular effects depend on when HRT is initiated:

| Timing | Effect |
|--------|--------|
| Within 10 years of menopause | Potential cardioprotective effects |
| < 60 years old | Favorable benefit-risk profile |
| > 10 years post-menopause | Increased cardiovascular risk |
| > 60 years old | Less favorable benefit-risk profile |

*Source: Hodis HN, Mack WJ. The timing hypothesis and hormone replacement therapy: a paradigm shift in the primary prevention of coronary heart disease in women. J Clin Endocrinol Metab. 2013;98(8):3236-3246.*

### 5.4 Quality of Life

Multiple studies demonstrate improvements in:
- Overall quality of life measures
- Sexual function
- Sleep quality
- Cognitive symptoms (brain fog)

---

## 6. Risks and Contraindications

### 6.1 Venous Thromboembolism (VTE)

**Risk Factors:**
- Baseline risk increases with age
- Oral estrogen increases risk 2-3 fold
- Transdermal estrogen: neutral or lower risk

**Risk by Formulation:**

| Route | Relative Risk | Notes |
|-------|---------------|-------|
| Oral estrogen | 2-3x increased | Hepatic first-pass effect |
| Transdermal estrogen | Minimal increase | Preferred for higher-risk patients |
| Micronized progesterone | Lower risk | vs. synthetic progestins |

*Source: Canonico M, et al. Hormone therapy and venous thromboembolism among postmenopausal women. Circulation. 2007;115(7):840-845.*

### 6.2 Breast Cancer

**Current Understanding:**

- EPT: Small increased risk with >5 years of use
- ET (estrogen alone): No increase or small decrease in risk
- Risk returns to baseline within 3-5 years of stopping

**Absolute Risk Context:**
- Attributable risk: <1 additional case per 1,000 women per year
- Similar to risk from obesity, alcohol use, or sedentary lifestyle

*Source: Collaborative Group on Hormonal Factors in Breast Cancer. Type and timing of menopausal hormone therapy and breast cancer risk. Lancet. 2019;394(10204):1159-1168.*

### 6.3 Stroke

- Small increased risk with oral HRT
- Risk primarily in older women
- Transdermal estrogen may have neutral effect

### 6.4 Contraindications

**Absolute Contraindications:**
- Undiagnosed abnormal uterine bleeding
- Known or suspected breast cancer
- Active or recent VTE or stroke
- Active liver disease
- Known thrombophilic disorder

**Relative Contraindications:**
- Elevated triglycerides (for oral estrogen)
- Active gallbladder disease
- Migraine with aura
- History of VTE

---

## 7. Administration Methods

### 7.1 Oral Preparations

**Advantages:**
- Convenient, familiar route
- Wide range of products
- Generally lower cost

**Disadvantages:**
- Hepatic first-pass metabolism
- Increased VTE risk
- Effect on triglycerides and clotting factors

### 7.2 Transdermal Preparations

**Patches:**
- Changed once or twice weekly
- Steady hormone levels
- Lower VTE risk

**Gels and Sprays:**
- Applied daily
- Flexible dosing
- Site rotation important

### 7.3 Vaginal Preparations

**Options:**
- Creams (Premarin, Estrace)
- Tablets (Vagifem)
- Rings (Estring, Femring)
- DHEA insert (Intrarosa)

**Indications:**
- Preferred for isolated GSM symptoms
- Minimal systemic absorption with low-dose preparations

### 7.4 Injections and Pellets

**Injections:**
- Estradiol valerate, estradiol cypionate
- Variable levels between injections

**Pellets:**
- Subcutaneous implantation
- Long-acting (3-6 months)
- Less commonly used

---

## 8. Monitoring and Follow-up Care

### 8.1 Baseline Assessment

**Required Evaluations:**
- Complete medical history
- Physical examination including breast and pelvic exam
- Blood pressure measurement
- Mammogram (per screening guidelines)
- Assessment of cardiovascular risk factors

**Consider:**
- Baseline lipid panel
- Blood glucose or HbA1c
- Thyroid function tests
- Liver function tests

### 8.2 Follow-up Schedule

| Timepoint | Assessment |
|-----------|------------|
| 3 months | Symptom response, side effects, blood pressure |
| 6 months | Comprehensive review, adjust dose if needed |
| 12 months | Annual review, mammogram, reassess continuation |
| Ongoing | Annual reassessment of benefits vs. risks |

### 8.3 Laboratory Monitoring

**Routine Labs:**
- Generally not required for monitoring standard HRT
- Consider lipid panel if using oral estrogen
- Hormone levels: not routinely needed; may guide dosing in some cases

### 8.4 Duration of Therapy

**Current Recommendations:**
- Individualized based on ongoing symptom burden and risk profile
- No arbitrary time limits
- Annual reassessment recommended
- Use lowest effective dose

*Source: NAMS. The 2022 Hormone Therapy Position Statement.*

---

## 9. Special Populations and Considerations

### 9.1 Cardiovascular Disease History

**Considerations:**
- Avoid initiating HRT in women with established CVD
- If already on HRT at time of CVD event, discontinuation recommended
- Transdermal route preferred if benefits outweigh risks

### 9.2 History of Breast Cancer

**General Guidance:**
- Systemic HRT generally contraindicated
- Low-dose vaginal estrogen may be considered for severe GSM
- Shared decision-making essential
- Non-hormonal alternatives available

### 9.3 History of VTE

**Risk Mitigation:**
- Transdermal estrogen preferred (if HRT used)
- Avoid oral estrogen
- Consider thrombophilia evaluation
- Micronized progesterone over synthetic progestins

### 9.4 Elevated Triglycerides

- Oral estrogen can increase triglycerides
- Transdermal estrogen is triglyceride-neutral
- Use transdermal route if triglycerides >300 mg/dL

### 9.5 Gallbladder Disease

- Oral estrogen increases gallbladder disease risk
- Transdermal route preferred

---

## 10. Frequently Asked Questions

**Q: Is HRT safe?**
A: For most healthy women under 60 or within 10 years of menopause, the benefits of HRT typically outweigh the risks. Individual assessment is essential.

**Q: How long can I take HRT?**
A: There is no mandatory time limit. Duration should be individualized based on ongoing symptoms, benefits, and risks, with annual reassessment.

**Q: Will HRT cause weight gain?**
A: HRT does not cause weight gain. Menopause itself is associated with changes in body composition; HRT may actually help maintain lean body mass.

**Q: Are bioidentical hormones safer?**
A: FDA-approved bioidentical hormones (like estradiol and micronized progesterone) have the same safety profile as other FDA-approved options. Custom-compounded preparations lack FDA oversight and are not proven safer.

**Q: Can I use HRT if I have a family history of breast cancer?**
A: Family history alone is not a contraindication. Risk assessment tools can help quantify individual risk. Shared decision-making with your healthcare provider is important.

**Q: What are alternatives to HRT?**
A: Non-hormonal options include:
- SSRIs/SNRIs (paroxetine, venlafaxine)
- Gabapentin
- Fezolinetant (NK3 receptor antagonist)
- Cognitive behavioral therapy
- Lifestyle modifications

---

## 11. Glossary of Terms

| Term | Definition |
|------|------------|
| **Bioidentical** | Chemically identical to hormones produced by the human body |
| **Conjugated Equine Estrogens (CEE)** | Mixture of estrogens derived from pregnant mare urine |
| **Endometrial Hyperplasia** | Abnormal thickening of the uterine lining |
| **Estradiol (E2)** | The primary estrogen produced by the ovaries |
| **FSH** | Follicle Stimulating Hormone; elevated in menopause |
| **GSM** | Genitourinary Syndrome of Menopause |
| **HRT** | Hormone Replacement Therapy |
| **Micronized** | Processed into small particles for better absorption |
| **POI** | Premature Ovarian Insufficiency |
| **Progestogen** | Umbrella term for progesterone and progestins |
| **Transdermal** | Absorbed through the skin |
| **VMS** | Vasomotor Symptoms (hot flashes, night sweats) |
| **VTE** | Venous Thromboembolism |

---

## 12. References and Citations

1. Stuenkel CA, Davis SR, Gompel A, et al. Treatment of Symptoms of the Menopause: An Endocrine Society Clinical Practice Guideline. *J Clin Endocrinol Metab*. 2015;100(11):3975-4011. doi:10.1210/jc.2015-2236

2. The NAMS 2022 Hormone Therapy Position Statement Advisory Panel. The 2022 Hormone Therapy Position Statement of The North American Menopause Society. *Menopause*. 2022;29(7):767-794. doi:10.1097/GME.0000000000002028

3. Rossouw JE, Prentice RL, Manson JE, et al. Postmenopausal hormone therapy and risk of cardiovascular disease by age and years since menopause. *JAMA*. 2007;297(13):1465-1477. doi:10.1001/jama.297.13.1465

4. Hodis HN, Mack WJ. The timing hypothesis and hormone replacement therapy: a paradigm shift in the primary prevention of coronary heart disease in women. *J Clin Endocrinol Metab*. 2013;98(8):3236-3246. doi:10.1210/jc.2013-1750

5. Canonico M, Plu-Bureau G, Lowe GD, Scarabin PY. Hormone therapy and venous thromboembolism among postmenopausal women: impact of the route of estrogen administration and progestogens: the ESTHER study. *Circulation*. 2007;115(7):840-845. doi:10.1161/CIRCULATIONAHA.106.642280

6. Collaborative Group on Hormonal Factors in Breast Cancer. Type and timing of menopausal hormone therapy and breast cancer risk: individual participant meta-analysis of the worldwide epidemiological evidence. *Lancet*. 2019;394(10204):1159-1168. doi:10.1016/S0140-6736(19)31709-X

7. Davis SR, Baber R, Panay N, et al. Global Consensus Position Statement on the Use of Testosterone Therapy for Women. *J Clin Endocrinol Metab*. 2019;104(10):4660-4666. doi:10.1210/jc.2019-01603

8. Hembree WC, Cohen-Kettenis PT, Gooren L, et al. Endocrine Treatment of Gender-Dysphoric/Gender-Incongruent Persons: An Endocrine Society Clinical Practice Guideline. *J Clin Endocrinol Metab*. 2017;102(11):3869-3903. doi:10.1210/jc.2017-01658

9. Maclennan AH, Broadbent JL, Lester S, Moore V. Oral oestrogen and combined oestrogen/progestogen therapy versus placebo for hot flushes. *Cochrane Database Syst Rev*. 2004;(4):CD002978. doi:10.1002/14651858.CD002978.pub2

10. American College of Obstetricians and Gynecologists. ACOG Practice Bulletin No. 141: Management of Menopausal Symptoms. *Obstet Gynecol*. 2014;123(1):202-216. (Reaffirmed 2018)

---

## Document Information

**Version:** 1.0  
**Generated:** {datetime.now().strftime("%B %d, %Y")}  
**Document Type:** Educational Reference Guide  
**Classification:** For Informational Purposes Only  

<div class="warning">

**FINAL REMINDER**

This document is provided for **educational purposes only** and does not constitute medical advice. Always consult with a qualified healthcare provider before starting, stopping, or modifying any hormone therapy regimen. Your healthcare provider can assess your individual health history, risk factors, and symptoms to determine the most appropriate treatment plan for you.

</div>

---

*© 2024 - This document may be freely distributed for educational purposes with attribution.*
"""
    
    return content


if __name__ == "__main__":
    # Generate the content
    print("Generating HRT Guide content...")
    content = generate_full_hrt_content()
    
    # Create output directory
    output_dir = Path("output/hrt_guide")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save markdown
    md_path = output_dir / "hrt_guide.md"
    with open(md_path, 'w') as f:
        f.write(content)
    print(f"Markdown saved: {md_path}")
    
    # Try to create PDF
    pdf_path = output_dir / "hrt_guide.pdf"
    pdf_created = create_pdf_from_markdown(content, pdf_path)
    
    if not pdf_created:
        print("\nTo install PDF support:")
        print("  pip install weasyprint markdown")
        print("  # or")
        print("  pip install fpdf2")
    
    print(f"\nOutput directory: {output_dir.absolute()}")
    print("Done!")