import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app import APP_VERSION
from checker.inspector import inspect_hosts
from config.validator import validate_hosts_config
from main import load_hosts, parse_tags, setup_logging
from reporter.reporter import generate_report

logger = logging.getLogger(__name__)
REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)


class RunRequest(BaseModel):
    hosts_file: str = Field("hosts.json", description="Config file name under config/")
    tags: Optional[str] = Field(None, description="Comma separated tag filters, e.g., env=prod,role=db")
    commands: Optional[List[str]] = Field(None, description="Override default command list")
    max_workers: int = Field(5, gt=0, le=64, description="Thread pool size")
    log_level: str = Field("INFO", description="Root logger level")


class RunResult(BaseModel):
    report_path: str
    summary: Dict[str, Any]
    results: List[Dict[str, Any]]


app = FastAPI(
    title="Py Automation Scripts API",
    version=APP_VERSION,
    description="Web wrapper for SSH inspection CLI",
)


@app.on_event("startup")
def configure_logging() -> None:
    setup_logging("INFO")
    logger.info("FastAPI service started, version %s", APP_VERSION)


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok", "version": APP_VERSION}


@app.get("/version")
def version() -> dict:
    return {"version": APP_VERSION}


@app.post("/run", response_model=RunResult)
def run_inspection(payload: RunRequest) -> RunResult:
    setup_logging(payload.log_level)
    hosts = load_hosts(payload.hosts_file)
    validate_hosts_config(hosts)

    tags_filter = parse_tags(payload.tags)
    results = inspect_hosts(
        hosts,
        tags_filter=tags_filter,
        commands=payload.commands,
        max_workers=payload.max_workers,
    )
    report_path = generate_report(results)
    if not report_path:
        raise HTTPException(status_code=500, detail="Failed to generate report")

    report_content = _load_report(report_path)
    return RunResult(
        report_path=report_path,
        summary=report_content.get("summary", {}),
        results=report_content.get("results", []),
    )


@app.get("/reports/latest")
def latest_report() -> dict:
    report_path = _get_latest_report()
    if not report_path:
        raise HTTPException(status_code=404, detail="No reports found")
    return _load_report(report_path)


def _get_latest_report() -> Optional[Path]:
    reports = sorted(REPORT_DIR.glob("report_*.json"), reverse=True)
    return reports[0] if reports else None


def _load_report(report_path: Union[str, Path]) -> Dict[str, Any]:
    path = Path(report_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Report {report_path} not found")
    with open(path, "r", encoding="utf-8") as fp:
        return json.load(fp)
