#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Run the full pipeline but ONLY print the final report URL (and optional XML dump).

Usage (VS Code launch.json or terminal):
  python debug_report_only.py --company-name "Tesla" --company-url "https://www.tesla.com" --prompt "focus on customer experience and cost optimization" --dump-xml --log-level WARNING
"""

import os
import sys
import uuid
import argparse
import logging

# ----------------------- path setup so both layouts work -----------------------
ROOT = os.path.abspath(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

SRC = os.path.join(ROOT, "src")
if os.path.isdir(SRC) and SRC not in sys.path:
    sys.path.insert(0, SRC)

def _imp(*candidates, required=True):
    """
    Try importing modules from several candidate paths.
    Example: _imp("src.core.models", "models")
    """
    last_err = None
    for name in candidates:
        try:
            return __import__(name, fromlist=["*"])
        except Exception as e:
            last_err = e
            continue
    if required:
        raise last_err
    return None

# ----------------------- tolerant imports (src-first, then flat) ---------------
bedrock_manager  = _imp("src.core.bedrock_manager", "bedrock_manager")
models           = _imp("src.core.models", "models")
# agents
company_research = _imp("src.company_research", "src.agents.company_research", "company_research")
use_case_gen     = _imp("src.use_case_generator", "src.agents.use_case_generator", "use_case_generator")
report_gen       = _imp("src.report_generator", "src.agents.report_generator", "report_generator")
# file parser lives either in src/services or project root in your repo
file_parser_mod  = _imp("src.services.file_parser", "src.file_parser", "file_parser", required=False)
# status tracker (utils or root)
status_tracker   = _imp("src.utils.status_tracker", "status_tracker", required=False)

# ----------------------- main runner ------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Run pipeline and show ONLY the final report URL")
    ap.add_argument("--company-name", required=True)
    ap.add_argument("--company-url", default="")
    ap.add_argument("--files", default="", help="comma-separated S3 or local paths to PDFs/DOCX")
    ap.add_argument("--prompt", default="", help="custom context / focus areas")
    ap.add_argument("--dump-xml", action="store_true", help="also save XML before PDF")
    ap.add_argument("--log-level", default="WARNING", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    ap.add_argument("--skip-upload", action="store_true", help="Do not upload to S3")

    args = ap.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level), format="%(levelname)s | %(message)s")
    log = logging.getLogger("report_only")

    # session & trackers
    session_id = str(uuid.uuid4())
    files = [f.strip() for f in args.files.split(",") if f.strip()]

    # optional status tracker if available
    st = None
    if status_tracker is not None and hasattr(status_tracker, "StatusTracker"):
        st = status_tracker.StatusTracker(session_id=session_id)

    # models
    mm = bedrock_manager.EnhancedModelManager()

    # minimal company profile (the report agent will enrich via research/use cases)
    CompanyProfile = models.CompanyProfile
    profile = CompanyProfile(
        name=args.company_name,
        industry="Technology & Innovation",
        business_model="Digital Platform and Services",
        company_size="Enterprise",
        technology_stack=["Cloud", "Data", "APIs"],
        cloud_maturity="Advanced",
        primary_challenges=["Operational Efficiency", "Customer Experience", "Growth"],
        growth_stage="Scaling",
        compliance_requirements=["Data Privacy", "Security"]
    )

    # parse files (tolerant; skip if parser not present)
    parsed_text = ""
    if files and file_parser_mod is not None:
        try:
            # accept either class FileParser() or module-level parse function
            if hasattr(file_parser_mod, "FileParser"):
                parser = file_parser_mod.FileParser()
                for p in files:
                    try:
                        parsed_text += (parser.parse_file_to_text(p) or "") + "\n"
                    except Exception as e:
                        log.warning("File parse failed for %s: %s", p, e)
            elif hasattr(file_parser_mod, "parse_file_to_text"):
                for p in files:
                    try:
                        parsed_text += (file_parser_mod.parse_file_to_text(p) or "") + "\n"
                    except Exception as e:
                        log.warning("File parse failed for %s: %s", p, e)
        except Exception as e:
            log.warning("File parsing step skipped: %s", e)

    # assemble custom context
    custom_ctx = None
    if args.prompt:
        custom_ctx = {
            "processed_prompt": args.prompt,
            "context_type": "user",
            "focus_areas": [args.prompt]
        }

    # research
    research_swarm = company_research.CompanyResearchSwarm(mm)
    research = research_swarm.conduct_comprehensive_research(
        company_name=args.company_name,
        company_url=args.company_url or "",
        status_tracker=st,
        parsed_files_content=parsed_text or None,
        custom_context=custom_ctx
    )

    # use cases
    generator = use_case_gen.DynamicUseCaseGenerator(mm)
    use_cases = generator.generate_dynamic_use_cases(
        company_profile=profile,
        research_data=research,
        status_tracker=st,
        parsed_files_content=parsed_text or None,
        custom_context=custom_ctx
    )

    # report: build XML, then render/upload PDF
    rg = report_gen.ConsolidatedReportGenerator(mm)

    # get XML string (calling the internal builder on purpose)
    xml = rg._generate_xml_report_with_enhanced_formatting(  # noqa: SLF001
        company_profile=profile,
        use_cases=use_cases,
        research_data=research,
        parsed_files_content=parsed_text or None,
        custom_context=custom_ctx
    )

    # optional save of raw XML for inspection
    if args.dump_xml:
        xml_path = os.path.join(ROOT, f"report_{session_id}.xml")
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml)
        print(f"XML_SAVED: {xml_path}")

    # now render + upload PDF via the class's renderer/uploader
    report_url = rg._generate_and_upload_pdf_from_xml(  # noqa: SLF001
        xml, profile.name, session_id
    )

    # the only final output you asked for:
    print(f"REPORT_URL: {report_url}")

if __name__ == "__main__":
    main()
