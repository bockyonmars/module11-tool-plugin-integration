"""
Module 11: Tool & Plugin Integration

An AI-style document insight agent that uses separate tools to:
1. Read text or PDF files.
2. Extract structured insights.
3. Calculate document statistics.
4. Export JSON and Markdown results.

PDF extraction uses pypdf.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List


BASE_DIR = Path(__file__).resolve().parent
SAMPLE_DOCS_DIR = BASE_DIR / "data" / "sample_docs"
OUTPUT_DIR = BASE_DIR / "output"


class DocumentReaderTool:
    """Tool for reading TXT and PDF documents."""

    @staticmethod
    def read_text(path: Path) -> str:
        return path.read_text(encoding="utf-8", errors="replace")

    @staticmethod
    def read_pdf(path: Path) -> str:
        try:
            from pypdf import PdfReader
        except ImportError as error:
            raise ImportError("Install PDF support with: pip install -r requirements.txt") from error

        reader = PdfReader(str(path))
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        return "\n".join(pages).strip()

    def read(self, path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix == ".txt":
            return self.read_text(path)
        if suffix == ".pdf":
            return self.read_pdf(path)
        raise ValueError(f"Unsupported file type: {suffix}")


class CalculatorTool:
    """Tool for calculating simple document statistics."""

    @staticmethod
    def word_count(text: str) -> int:
        return len(re.findall(r"[a-zA-Z0-9$-]+", text))

    @staticmethod
    def sentence_count(text: str) -> int:
        return len([s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()])

    @staticmethod
    def estimated_reading_minutes(text: str, words_per_minute: int = 200) -> float:
        return round(CalculatorTool.word_count(text) / words_per_minute, 2)


class InsightExtractorTool:
    """Tool for extracting structured insights from document text."""

    @staticmethod
    def extract_title(text: str, path: Path) -> str:
        for line in text.splitlines():
            clean = line.strip()
            if clean:
                return clean[:80]
        return path.stem.replace("_", " ").title()

    @staticmethod
    def extract_dates(text: str) -> List[str]:
        patterns = [
            r"\b\d{4}-\d{2}-\d{2}\b",
            r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
        ]
        dates = []
        for pattern in patterns:
            dates.extend(re.findall(pattern, text))
        return sorted(set(dates))

    @staticmethod
    def extract_money(text: str) -> List[str]:
        return sorted(set(re.findall(r"\$\s?\d[\d,]*(?:\.\d{2})?", text)))

    @staticmethod
    def extract_priority(text: str) -> str:
        match = re.search(r"\bPriority:\s*(Low|Medium|High|Critical)\b", text, re.I)
        return match.group(1).title() if match else "Not specified"

    @staticmethod
    def extract_owner(text: str) -> str:
        match = re.search(r"\b(?:Owner|Vendor):\s*([^\n]+)", text, re.I)
        return match.group(1).strip() if match else "Not specified"

    @staticmethod
    def extract_bullets_after_heading(text: str, heading: str) -> List[str]:
        lines = text.splitlines()
        results = []
        capture = False

        for line in lines:
            stripped = line.strip()
            if re.match(rf"^{heading}:?$", stripped, re.I):
                capture = True
                continue

            if capture and re.match(r"^[A-Z][A-Za-z ]+:$", stripped):
                break

            if capture and stripped.startswith("-"):
                results.append(stripped.lstrip("- ").strip())

        return results

    @staticmethod
    def key_points(text: str, limit: int = 4) -> List[str]:
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 30]
        return sentences[:limit]


class DocumentInsightAgent:
    """Agent that coordinates reader, calculator, and extractor tools."""

    def __init__(self) -> None:
        self.reader = DocumentReaderTool()
        self.calculator = CalculatorTool()
        self.extractor = InsightExtractorTool()

    def analyze(self, path: Path) -> Dict:
        text = self.reader.read(path)

        risks = self.extractor.extract_bullets_after_heading(text, "Risks")
        actions = (
            self.extractor.extract_bullets_after_heading(text, "Actions")
            or self.extractor.extract_bullets_after_heading(text, "Recommended Actions")
        )

        return {
            "file_name": path.name,
            "file_type": path.suffix.lower().replace(".", ""),
            "title": self.extractor.extract_title(text, path),
            "owner_or_vendor": self.extractor.extract_owner(text),
            "priority": self.extractor.extract_priority(text),
            "dates": self.extractor.extract_dates(text),
            "money_values": self.extractor.extract_money(text),
            "word_count": self.calculator.word_count(text),
            "sentence_count": self.calculator.sentence_count(text),
            "estimated_reading_minutes": self.calculator.estimated_reading_minutes(text),
            "key_points": self.extractor.key_points(text),
            "risks": risks,
            "action_items": actions,
        }


def create_markdown_report(results: List[Dict]) -> str:
    lines = ["# Module 11 Structured Insight Report", ""]

    for result in results:
        lines.extend([
            f"## {result['title']}",
            "",
            f"- File: `{result['file_name']}`",
            f"- Type: {result['file_type']}",
            f"- Owner/Vendor: {result['owner_or_vendor']}",
            f"- Priority: {result['priority']}",
            f"- Dates: {', '.join(result['dates']) if result['dates'] else 'None found'}",
            f"- Money values: {', '.join(result['money_values']) if result['money_values'] else 'None found'}",
            f"- Word count: {result['word_count']}",
            f"- Estimated reading time: {result['estimated_reading_minutes']} minutes",
            "",
            "### Key Points",
            "",
        ])

        for point in result["key_points"]:
            lines.append(f"- {point}")

        lines.extend(["", "### Risks", ""])
        for risk in result["risks"] or ["No explicit risks found."]:
            lines.append(f"- {risk}")

        lines.extend(["", "### Action Items", ""])
        for action in result["action_items"] or ["No explicit action items found."]:
            lines.append(f"- {action}")

        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def run_demo() -> None:
    agent = DocumentInsightAgent()
    paths = sorted(
        list(SAMPLE_DOCS_DIR.glob("*.txt")) + list(SAMPLE_DOCS_DIR.glob("*.pdf"))
    )

    if not paths:
        raise FileNotFoundError(f"No sample documents found in {SAMPLE_DOCS_DIR}")

    results = [agent.analyze(path) for path in paths]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUT_DIR / "insights.json"
    report_path = OUTPUT_DIR / "insights_report.md"

    json_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    report_path.write_text(create_markdown_report(results), encoding="utf-8")

    print(f"Analyzed {len(results)} documents.")
    print(f"Saved structured JSON to: {json_path}")
    print(f"Saved Markdown report to: {report_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Module 11 document insight agent")
    parser.add_argument("--path", help="Analyze one TXT or PDF file")
    parser.add_argument("--demo", action="store_true", help="Analyze all sample docs")
    args = parser.parse_args()

    agent = DocumentInsightAgent()

    if args.path:
        result = agent.analyze(Path(args.path))
        print(json.dumps(result, indent=2))
    else:
        run_demo()


if __name__ == "__main__":
    main()
