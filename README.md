# Company Use Case Generator 

An **AI-powered Business Transformation Assistant** that automates **company research, use case generation, and executive-style report creation** using **AWS Bedrock LLMs**, multi-agent orchestration, and web scraping.

---

## Features
- **Company Research Agent** (`src/agents/company_research.py`)  
  - Multi-agent swarm for comprehensive business analysis.  
  - Web scraping + document parsing (PDF/DOCX).  
  - Identifies revenue models, operations, challenges, and opportunities.  

- **Use Case Generator** (`src/agents/use_case_generator.py`)  
  - Creates structured, XML-tagged **business transformation initiatives**.  
  - Aligns use cases with industry trends, company documents, and custom context.  
  - Includes AWS service recommendations and ROI metrics.  

- **Report Generator** (`src/agents/report_generator.py`)  
  - Produces **executive-ready PDF reports** with citations and strategic recommendations.  
  - Uses XML formatting for structured content parsing.  
  - Supports both **WeasyPrint** and **ReportLab** for PDF export.  

- **Web Scraper Utility** (`src/services/web_scraper.py`)  
  - Powered by **BeautifulSoup** + **Google Search**.  
  - Extracts market insights and competitive intelligence.  

- **AWS Integration** (`src/services/aws_clients.py`, `src/core/bedrock_manager.py`)  
  - Uses **Amazon Bedrock** (Anthropic Claude, Amazon Nova models).  
  - Stores outputs in **S3**.  
  - Tracks workflow status via **DynamoDB**.  

- **Main Orchestrator** (`src/orchestrator.py`)  
  - End-to-end flow: research → use case generation → consolidated report.  
  - Supports file parsing, custom prompts, and session tracking.  
  - Provides polling and session management.  

---

## ⚙️ Tech Stack
- **Languages:** Python 3.10+  
- **AI Models:** AWS Bedrock (Claude Sonnet, Amazon Nova)  
- **Libraries:**  
  - `strands` (agent orchestration)  
  - `beautifulsoup4`, `googlesearch`, `requests` (web scraping)  
  - `weasyprint` / `reportlab` (PDF generation)  
- **Cloud:** AWS (Bedrock, S3, DynamoDB)  

```
Company_usecase_generator/
│
├── src/
│ ├── agents/
│ │ ├── company_research.py # Multi-agent company research
│ │ ├── use_case_generator.py # Generate structured use cases
│ │ └── report_generator.py # Create executive PDF reports
│ ├── core/
│ │ ├── bedrock_manager.py # AWS Bedrock model manager
│ │ └── models.py # Data models for profiles & use cases
│ ├── services/
│ │ ├── aws_clients.py # AWS client initialization (S3, DynamoDB)
│ │ └── web_scraper.py # Web scraping utilities
│ ├── utils/
│ │ ├── cache_manager.py # Cache handling with DynamoDB
│ │ ├── prompt_processor.py # Custom prompt processor
│ │ ├── session_manager.py # Session tracking utilities
│ │ └── status_tracker.py # Status checkpoints & tracking
│ └── orchestrator.py # Main orchestrator (end-to-end pipeline)
│
├── reports/ # Generated PDF reports
└── README.md # Project documentation
```
<img width="3840" height="3473" alt="Untitled diagram _ Mermaid Chart-2025-09-13-222157" src="https://github.com/user-attachments/assets/e8f80efd-7699-48ad-9258-51df0dd86c43" />


<meta name="msvalidate.01" content="30A7B1CCD906578D2BC08DBE78801080" />
