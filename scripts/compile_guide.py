"""
Compiler script for NexSQL Project Interview Guide.
Outputs:
1. PROJECT_INTERVIEW_GUIDE.md
2. PROJECT_INTERVIEW_GUIDE.pdf
"""
import os
import sys
import re
import html
from typing import List, Tuple

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.guide_sections import (
    part1_sections_1_to_5,
    part2_sections_6_to_9,
    part3_sections_10_to_15,
    part4_sections_16_to_20,
    part5_sections_21_to_24,
    part6_section_25_questions,
    part7_sections_26_to_34,
)

import reportlab
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Preformatted,
    PageBreak,
    KeepTogether,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and print 'Page X of Y' page numbers
    along with professional running headers and footers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        # Omit running headers and footers on Cover Page (Page 1)
        if self._pageNumber > 1:
            self.saveState()
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))

            # Running Header
            self.drawString(36, 756, "NexSQL: System Architecture & SDE Interview Defense Guide")
            self.drawRightString(576, 756, "SDE Interview Preparation")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(36, 750, 576, 750)

            # Running Footer
            self.line(36, 42, 576, 42)
            self.drawString(36, 30, "Confidential - Natural Language to SQL Architecture")
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(576, 30, page_text)
            self.restoreState()


def clean_pdf_text(text: str) -> str:
    """
    Normalizes Unicode characters into pure, universal ASCII equivalents
    to prevent solid black boxes (.notdef glyphs) in PDF Type-1 fonts.
    """
    replacements = {
        # Box drawing characters -> ASCII
        '\u2500': '-', '\u2502': '|', '\u251c': '+', '\u2514': '+',
        '\u250c': '+', '\u2510': '+', '\u2518': '+', '\u252c': '+',
        '\u2534': '+', '\u253c': '+', '\u2524': '+', '\u2550': '=',
        '\u2551': '|', '\u2554': '+', '\u2557': '+', '\u255a': '+',
        '\u255d': '+', '\u2560': '+', '\u2563': '+', '\u2566': '+',
        '\u2569': '+', '\u256c': '+',
        # Arrows & pointers -> ASCII
        '\u25bc': 'v', '\u25b2': '^', '\u25ba': '>', '\u25c4': '<',
        '\u2193': 'v', '\u2192': '->', '\u2190': '<-', '\u2191': '^',
        '\u2794': '->', '\u2194': '<->', '\u21c4': '<->',
        # Emojis & status indicators -> Clean text badges
        '\U0001f7e2': '[SAFE]', '\U0001f7e1': '[WARN]', '\U0001f534': '[RISK]',
        '\U0001f535': '[INFO]', '\u274c': '[X]', '\u2713': '[V]',
        '\u2714': '[V]', '\U0001f3af': '[TARGET]', '\U0001f4d1': '[DOC]',
        # Typography & Punctuation
        '\u2014': ' -- ', '\u2013': '-', '\u201c': '"', '\u201d': '"',
        '\u2018': "'", '\u2019': "'", '\u2026': '...',
        '\u2022': '-', '\xb5': 'u', '\u2248': '~', '\u2265': '>=',
        '\u2264': '<=', '\u2260': '!=', '\xd7': '*', '\xb1': '+/-',
        # LaTeX symbols
        '\\longrightarrow': '->', '\\rightarrow': '->', '\\approx': '~',
        '\\times': '*', '\\ge': '>=', '\\le': '<=', '\\%': '%',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)

    # Clean any remaining LaTeX formatting
    text = re.sub(r'\\text\{([^}]+)\}', r'\1', text)
    text = re.sub(r'\$([^$]+)\$', r'\1', text)

    # Ensure no unmapped high-unicode characters escape
    cleaned = []
    for c in text:
        if ord(c) < 128:
            cleaned.append(c)
        else:
            cleaned.append(' ')
    return ''.join(cleaned)


def get_full_markdown() -> str:
    header = """# NexSQL: Comprehensive System Architecture & SDE Interview Defense Guide
**An Exhaustive Technical Blueprint, Codebase Audit, System Design, Scalability Analysis, and Interview Defense Manual**

- **Project Name**: NexSQL (Natural Language to Enterprise SQL Engine)
- **Primary Stack**: Python 3.10+, FastAPI, Uvicorn, SQLite (`enterprise.db`), Groq SDK (Llama 3.1 8B Instant), `sqlglot` AST Parser, HTML5/CSS3/JavaScript, Chart.js
- **Scope**: 22 Normalized Relational Tables, 2,460 Seeded Enterprise Records, 105 Evaluation Benchmark Queries
- **Document Purpose**: Complete technical breakdown of the existing implementation, production scalability architecture, and full preparation to defend this project in any Software Development Engineer (SDE I/II/Senior) interview.

---

## Guide Conventions & Classification Framework

To ensure 100% technical integrity and avoid exaggerating production capabilities during technical interviews, every technical concept in this document is explicitly labeled using one of three strict classifications:

1. **`CURRENT IMPLEMENTATION`**:
   Reflects code, configurations, data models, or mechanisms that **actually exist and run in this repository today**.
2. **`RECOMMENDED IMPROVEMENT`**:
   Architectural additions, optimizations, or technologies that do not currently exist in the code, but represent the **logical next step for production scale or enterprise hardening**.
3. **`INTERVIEW CONCEPT`**:
   General computer science, system design, or distributed systems knowledge that interviewers frequently test when discussing systems of this archetype.

---
"""
    parts = [
        part1_sections_1_to_5.get_content(),
        part2_sections_6_to_9.get_content(),
        part3_sections_10_to_15.get_content(),
        part4_sections_16_to_20.get_content(),
        part5_sections_21_to_24.get_content(),
        part6_section_25_questions.get_content(),
        part7_sections_26_to_34.get_content(),
    ]

    return header + "\n\n" + "\n\n---\n\n".join(parts) + "\n"


def format_inline_markdown(text: str) -> str:
    """
    Converts inline markdown (*italic*, **bold**, `code`, [link](url))
    into ReportLab XML tags (<i>, <b>, <font>, <a>).
    Safely cleans Unicode black boxes, escapes XML entities, and handles inline code.
    """
    # 1. Clean unicode characters that turn into black boxes
    text = clean_pdf_text(text)

    # 2. Protect HTML break tags
    text = re.sub(r'<br\s*/?>', '___BR_TOKEN___', text, flags=re.IGNORECASE)

    # 3. Extract inline code tokens to placeholders to avoid regex tag collisions
    code_tokens = []
    def repl_code(m):
        code_tokens.append(m.group(1))
        return f"___CODE_TOKEN_{len(code_tokens)-1}___"

    text = re.sub(r'`([^`\n]+?)`', repl_code, text)

    # 4. Escape XML entities
    text = html.escape(text)

    # 5. Bold: **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)

    # 6. Italic: *text* (avoiding empty or multiline strings)
    text = re.sub(r'(?<!\*)\*([^*\n]+?)\*(?!\*)', r'<i>\1</i>', text)

    # 7. Markdown links: [text](url)
    def repl_link(m):
        label = m.group(1)
        url = m.group(2)
        if url.startswith("http://") or url.startswith("https://"):
            return f'<a href="{url}" color="#0284c7"><u>{label}</u></a>'
        return f'<b>{label}</b>'

    text = re.sub(r'\[([^\]\n]+?)\]\(([^)\n]+?)\)', repl_link, text)

    # 8. Restore line break tokens as ReportLab <br/>
    text = text.replace('___BR_TOKEN___', '<br/>')

    # 9. Restore code tokens with proper XML escaping
    for idx, c_val in enumerate(code_tokens):
        escaped_c = html.escape(c_val)
        text = text.replace(
            f"___CODE_TOKEN_{idx}___",
            f'<font name="Courier" color="#991b1b"><b>{escaped_c}</b></font>'
        )

    return text


def make_para(raw_text: str, style, bulletText=None) -> Paragraph:
    """
    Creates a ReportLab Paragraph safely. If any tag syntax error occurs,
    completely strips tags and renders clean escaped plain text so compilation never crashes.
    """
    formatted = format_inline_markdown(raw_text)
    try:
        return Paragraph(formatted, style, bulletText=bulletText)
    except Exception:
        clean_plain = html.escape(re.sub(r'<[^>]+>', '', raw_text))
        return Paragraph(clean_plain, style, bulletText=bulletText)


def wrap_code_lines(code: str, max_chars: int = 85) -> str:
    """
    Wraps long lines in code blocks so they don't get clipped on PDF pages.
    """
    code = clean_pdf_text(code)
    wrapped_lines = []
    for line in code.split('\n'):
        if len(line) <= max_chars:
            wrapped_lines.append(line)
        else:
            cur = line
            while len(cur) > max_chars:
                split_idx = cur.rfind(' ', 0, max_chars)
                if split_idx == -1 or split_idx < max_chars // 2:
                    split_idx = max_chars
                wrapped_lines.append(cur[:split_idx])
                cur = "  " + cur[split_idx:].lstrip()
            if cur:
                wrapped_lines.append(cur)
    return '\n'.join(wrapped_lines)


def build_pdf_from_markdown(md_content: str, output_path: str):
    """
    Parses full markdown document into ReportLab Platypus flowables and renders PDF.
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=48,
        bottomMargin=48,
    )

    styles = getSampleStyleSheet()

    # Define custom cohesive styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#0f172a'),
        alignment=0,
        spaceAfter=10,
    )
    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True,
    )
    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True,
    )
    h3_style = ParagraphStyle(
        'H3',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True,
    )
    h4_style = ParagraphStyle(
        'H4',
        parent=styles['Heading4'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#0284c7'),
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True,
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=5,
    )
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#1e293b'),
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=3,
    )
    code_style = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=6.5,
        leading=8.5,
        textColor=colors.HexColor('#0f172a'),
        backColor=colors.HexColor('#f8fafc'),
        borderColor=colors.HexColor('#cbd5e1'),
        borderWidth=0.5,
        borderPadding=5,
        spaceBefore=4,
        spaceAfter=4,
    )
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#1e293b'),
    )
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
    )

    story = []

    # --- COVER PAGE ---
    cover_data = [
        [
            Paragraph(
                "<b><font size='26' color='#0f172a'>NexSQL</font></b><br/>"
                "<b><font size='13' color='#2563eb'>Enterprise Natural Language to SQL Architecture & Defense</font></b><br/><br/>"
                "<font size='10' color='#334155'><b>Senior Software Engineer / SDE Interview Guide & System Audit</b></font><br/>"
                "<font size='8' color='#64748b'>Comprehensive Codebase Breakdown | AST Security | 1M-User Scalability | 102 Interview Q&As</font>",
                title_style
            )
        ]
    ]
    cover_table = Table(cover_data, colWidths=[540])
    cover_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f1f5f9')),
        ('PADDING', (0,0), (-1,-1), 16),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 10))

    # Official Resume Points Callout Box
    resume_box_data = [
        [
            Paragraph(
                "<b>OFFICIAL CANDIDATE RESUME BULLET POINTS</b><br/><br/>"
                "- <b>Achieved sub-second SQL translation using Groq API with Llama 3.1 8B, enabling real-time queries across 20+ database tables</b><br/>"
                "- <b>Validated and executed LLM-generated SQL with 95%+ query validity, maintaining integrity across complex relational schemas</b><br/>"
                "- <b>Enabled non-technical users to query 1000+ records without SQL, simplifying access to structured enterprise data</b><br/>"
                "- <b>Achieved ~80% execution accuracy across 100+ test queries using prompt engineering and metadata mapping for complex joins</b>",
                body_style
            )
        ]
    ]
    resume_table = Table(resume_box_data, colWidths=[540])
    resume_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0fdf4')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#86efac')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(resume_table)
    story.append(Spacer(1, 10))

    meta_data = [
        [Paragraph("<b>Component</b>", table_header_style), Paragraph("<b>Specification / Architecture</b>", table_header_style)],
        [Paragraph("<b>Core Stack</b>", table_cell_style), Paragraph("Python 3.10+, FastAPI (ASGI), Uvicorn, SQLite (`enterprise.db`), Groq SDK (Llama 3.1 8B Instant)", table_cell_style)],
        [Paragraph("<b>AST Validation</b>", table_cell_style), Paragraph("`sqlglot` recursive syntax tree validation, dialect transpilation, read-only enforcement", table_cell_style)],
        [Paragraph("<b>Database Scope</b>", table_cell_style), Paragraph("22 normalized tables (3NF), 4 domains, 12 indexes, 2,460 seeded enterprise records", table_cell_style)],
        [Paragraph("<b>Evaluation Benchmark</b>", table_cell_style), Paragraph("105 automated benchmark test cases (Simple, Medium, Complex), measuring syntax & execution validity", table_cell_style)],
        [Paragraph("<b>Frontend UI</b>", table_cell_style), Paragraph("Vanilla HTML5, Glassmorphism CSS3, Vanilla ES6 JavaScript, Dynamic Chart.js visualizations", table_cell_style)],
        [Paragraph("<b>Engineering Scope</b>", table_cell_style), Paragraph("Production scalability, Redis caching, RabbitMQ/Kafka, Docker, CI/CD, 102 Interview Q&As", table_cell_style)],
    ]
    meta_table = Table(meta_data, colWidths=[130, 410])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('PADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    framework_data = [
        [
            Paragraph(
                "<b>GUIDE DEFENSE FRAMEWORK: STRICT TRUTHFULNESS & CLASSIFICATION</b><br/><br/>"
                "- <b>CURRENT IMPLEMENTATION</b>: Technology, configuration, or mechanism actively present in this codebase.<br/>"
                "- <b>RECOMMENDED IMPROVEMENT</b>: Production-grade architectural enhancement proposed for enterprise scaling.<br/>"
                "- <b>INTERVIEW CONCEPT</b>: Core computer science, distributed systems, or database concept tested in SDE interviews.",
                body_style
            )
        ]
    ]
    framework_table = Table(framework_data, colWidths=[540])
    framework_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#eff6ff')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#93c5fd')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(framework_table)
    story.append(Spacer(1, 15))

    # Table of Contents Summary Grid
    toc_data = [
        [Paragraph("<b>Table of Contents Overview (34 Complete Sections)</b>", table_header_style), Paragraph("", table_header_style)],
        [Paragraph("<b>1. Executive Summary & Problem</b>", table_cell_style), Paragraph("<b>18. Big-O Performance & Profiling</b>", table_cell_style)],
        [Paragraph("<b>2. Interview Pitch Answers (30s, 1m, 2m)</b>", table_cell_style), Paragraph("<b>19. System Design for 1M Users</b>", table_cell_style)],
        [Paragraph("<b>3. System Architecture & Production Scale</b>", table_cell_style), Paragraph("<b>20. Monolith vs Microservices</b>", table_cell_style)],
        [Paragraph("<b>4. Codebase Map & Top 20 Functions</b>", table_cell_style), Paragraph("<b>21. Cloud Deployment Architecture</b>", table_cell_style)],
        [Paragraph("<b>5. 5 End-to-End Execution Flows</b>", table_cell_style), Paragraph("<b>22. Observability (Logs, Metrics, Traces)</b>", table_cell_style)],
        [Paragraph("<b>6. Technology Deep Dive & Trade-offs</b>", table_cell_style), Paragraph("<b>23. Testing Pyramid & Benchmark Suites</b>", table_cell_style)],
        [Paragraph("<b>7. Database Deep Dive (22 Tables)</b>", table_cell_style), Paragraph("<b>24. Design Patterns & Principles</b>", table_cell_style)],
        [Paragraph("<b>8. REST API & Endpoint Contracts</b>", table_cell_style), Paragraph("<b>25. 102 Project Interview Questions</b>", table_cell_style)],
        [Paragraph("<b>9. Scalability Analysis (10 to 1M Users)</b>", table_cell_style), Paragraph("<b>26. 'Why Did You Choose X?' Defenses</b>", table_cell_style)],
        [Paragraph("<b>10. Redis Architecture & Caching</b>", table_cell_style), Paragraph("<b>27. Resume Defense & Cross-Examination</b>", table_cell_style)],
        [Paragraph("<b>11. RabbitMQ Asynchronous Queues</b>", table_cell_style), Paragraph("<b>28. 'What Would You Improve?' (P0, P1, P2)</b>", table_cell_style)],
        [Paragraph("<b>12. Apache Kafka Event Streaming</b>", table_cell_style), Paragraph("<b>29. 30 Mock Interview Questions</b>", table_cell_style)],
        [Paragraph("<b>13. Sync vs Async Execution & GIL</b>", table_cell_style), Paragraph("<b>30. Three-Tier Learning Roadmap</b>", table_cell_style)],
        [Paragraph("<b>14. Load Balancing & Failover</b>", table_cell_style), Paragraph("<b>31. External Resources & Verified URLs</b>", table_cell_style)],
        [Paragraph("<b>15. CI/CD Pipeline & Zero-Downtime</b>", table_cell_style), Paragraph("<b>32. 15-Minute Rapid Revision Sheet</b>", table_cell_style)],
        [Paragraph("<b>16. Comprehensive Security Audit</b>", table_cell_style), Paragraph("<b>33. Final Readiness Checklist</b>", table_cell_style)],
        [Paragraph("<b>17. Failure Scenarios & Reliability</b>", table_cell_style), Paragraph("<b>34. The 10 Things I Must Know Cold</b>", table_cell_style)],
    ]
    toc_table = Table(toc_data, colWidths=[270, 270])
    toc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('PADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    story.append(toc_table)

    story.append(PageBreak())

    # --- BODY CONTENT PARSING ---
    lines = md_content.split('\n')
    i = 0
    total_lines = len(lines)

    in_code_block = False
    code_block_lines = []

    table_lines = []

    while i < total_lines:
        line = lines[i]

        # Handle Code Block Start/End
        if line.strip().startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_block_lines = []
                i += 1
                continue
            else:
                in_code_block = False
                code_text = '\n'.join(code_block_lines)
                code_text = wrap_code_lines(code_text, max_chars=85)
                escaped_code = html.escape(code_text)
                
                # Render code block directly so it can split across pages cleanly
                pre = Preformatted(escaped_code, code_style)
                story.append(pre)
                story.append(Spacer(1, 4))
                i += 1
                continue

        if in_code_block:
            code_block_lines.append(line)
            i += 1
            continue

        stripped = line.strip()

        # Handle Empty Lines
        if not stripped:
            i += 1
            continue

        # Handle Markdown Tables (| ... |)
        if stripped.startswith('|') and stripped.endswith('|'):
            table_lines.append(stripped)
            # Check if next line is also part of table
            if i + 1 < total_lines and lines[i+1].strip().startswith('|') and lines[i+1].strip().endswith('|'):
                i += 1
                continue
            else:
                # End of table, process collected table lines
                parsed_table_data = []
                for tline in table_lines:
                    cells = [c.strip() for c in tline.strip('|').split('|')]
                    # Check if separator row (--- | ---)
                    if all(re.match(r'^:?-+:?$', c) for c in cells):
                        continue
                    row_paragraphs = []
                    is_header_row = len(parsed_table_data) == 0
                    for cell in cells:
                        c_style = table_header_style if is_header_row else table_cell_style
                        row_paragraphs.append(make_para(cell, c_style))
                    parsed_table_data.append(row_paragraphs)

                if parsed_table_data:
                    num_cols = max(len(r) for r in parsed_table_data)
                    # Normalize row lengths
                    for r in parsed_table_data:
                        while len(r) < num_cols:
                            r.append(make_para("", table_cell_style))

                    # Calculate col widths to sum to 540pt
                    if num_cols == 2:
                        col_widths = [150, 390]
                    elif num_cols == 3:
                        col_widths = [110, 160, 270]
                    elif num_cols == 4:
                        col_widths = [90, 130, 150, 170]
                    elif num_cols == 5:
                        col_widths = [70, 110, 110, 120, 130]
                    else:
                        col_widths = [540 / num_cols] * num_cols

                    t = Table(parsed_table_data, colWidths=col_widths)
                    t.setStyle(TableStyle([
                        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
                        ('PADDING', (0,0), (-1,-1), 4),
                        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
                        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
                    ]))
                    story.append(t)
                    story.append(Spacer(1, 4))

                table_lines = []
                i += 1
                continue

        # Handle Blockquotes / Alerts (> ...)
        if stripped.startswith('>'):
            quote_text = stripped.lstrip('>').strip()
            # Collect multiple quote lines
            while i + 1 < total_lines and lines[i+1].strip().startswith('>'):
                i += 1
                quote_text += " " + lines[i].strip().lstrip('>').strip()

            q_para = make_para(quote_text, body_style)
            q_table = Table([[q_para]], colWidths=[540])
            q_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
                ('LEFTPADDING', (0,0), (-1,-1), 10),
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
                ('LINEBEFORE', (0,0), (0,-1), 3, colors.HexColor('#2563eb')),
                ('PADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(q_table)
            story.append(Spacer(1, 4))
            i += 1
            continue

        # Handle Horizontal Rule (---)
        if stripped == '---':
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e2e8f0'), spaceBefore=6, spaceAfter=6))
            i += 1
            continue

        # Handle Headings
        if stripped.startswith('# '):
            # Major numbered section: insert page break before
            if re.match(r'^# \d+\.', stripped):
                story.append(PageBreak())
            story.append(make_para(stripped[2:], h1_style))
            i += 1
            continue

        if stripped.startswith('## '):
            story.append(make_para(stripped[3:], h2_style))
            i += 1
            continue

        if stripped.startswith('### '):
            story.append(make_para(stripped[4:], h3_style))
            i += 1
            continue

        if stripped.startswith('#### '):
            story.append(make_para(stripped[5:], h4_style))
            i += 1
            continue

        # Handle Bullet Points (- or *)
        if stripped.startswith('- ') or stripped.startswith('* '):
            item_text = stripped[2:]
            story.append(make_para(item_text, bullet_style, bulletText='-'))
            i += 1
            continue

        # Handle Numbered Lists (1. ...) -> Use markdown bold **num.** so format_inline_markdown handles it safely
        num_match = re.match(r'^(\d+)\.\s+(.+)$', stripped)
        if num_match:
            num = num_match.group(1)
            item_text = num_match.group(2)
            story.append(make_para(f"**{num}.** {item_text}", bullet_style))
            i += 1
            continue

        # Standard Paragraph
        story.append(make_para(stripped, body_style))
        i += 1

    print("Building PDF with ReportLab Platypus...")
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF built successfully: {output_path}")


def main():
    print("=== NEXSQL INTERVIEW GUIDE COMPILER ===")
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    md_output_path = os.path.join(root_dir, "PROJECT_INTERVIEW_GUIDE.md")
    pdf_output_path = os.path.join(root_dir, "PROJECT_INTERVIEW_GUIDE.pdf")

    print("1. Assembling Markdown from 7 modular parts...")
    full_md = get_full_markdown()
    with open(md_output_path, "w", encoding="utf-8") as f:
        f.write(full_md)
    print(f"   Markdown saved: {md_output_path} ({len(full_md)} chars, {len(full_md.split())} words)")

    print("2. Compiling PDF using ReportLab Platypus & NumberedCanvas...")
    build_pdf_from_markdown(full_md, pdf_output_path)
    
    # Verify file existence and sizes
    md_size = os.path.getsize(md_output_path)
    pdf_size = os.path.getsize(pdf_output_path)
    print("=== COMPILATION COMPLETE ===")
    print(f"Markdown: {md_output_path} ({md_size:,} bytes)")
    print(f"PDF:      {pdf_output_path} ({pdf_size:,} bytes)")


if __name__ == "__main__":
    main()
