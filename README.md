# Module 11: Tool & Plugin Integration

## Project Overview

This project demonstrates an AI-style agent that integrates multiple tools to read documents and extract structured insights.

The agent can read:

- `.txt` files
- `.pdf` files

It then extracts structured information such as title, dates, priority, owner/vendor, money values, key points, risks, action items, word count, and estimated reading time.

## Tools Used Inside the Agent

The script separates the work into tool-like classes:

- `DocumentReaderTool`
- `CalculatorTool`
- `InsightExtractorTool`
- `DocumentInsightAgent`

This matches the idea of extending an agent with document readers and calculators.

## Project Structure

```text
module11-tool-plugin-integration/
├── insight_agent.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   └── sample_docs/
│       ├── incident_report.txt
│       ├── patient_access_policy.pdf
│       └── vendor_contract.txt
└── output/
```

## Setup

```bash
cd module11-tool-plugin-integration
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`pypdf` is required for PDF text extraction.

## Run the Demo

```bash
python insight_agent.py --demo
```

This creates:

```text
output/insights.json
output/insights_report.md
```

## Analyze One File

```bash
python insight_agent.py --path data/sample_docs/incident_report.txt
```

or:

```bash
python insight_agent.py --path data/sample_docs/patient_access_policy.pdf
```
