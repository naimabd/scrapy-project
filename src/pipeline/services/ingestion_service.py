from __future__ import annotations

import json
import logging
import os
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


@dataclass
class ScrapeResult:
    returncode: int
    stored: int = 0
    unchanged: int = 0
    failed: int = 0
    dropped: int = 0
    pages_scraped: int = 0
    elapsed_seconds: float = 0.0
    raw_stats: dict = field(default_factory=dict)


class IngestionService:
    def __init__(
        self,
        logger: logging.Logger,
        project_root: Path | None = None,
    ) -> None:
        self.logger = logger
        # Default to the root of the project where scrapy.cfg lives
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent

    def run_scrape(
        self,
        start_date: str,
        end_date: str,
        bodies: list[str],
        base_url: str,
        user_agents: list[str],
        env_vars: dict[str, str],
    ) -> ScrapeResult:
        """Runs the Scrapy spider as a subprocess."""
        cwd = self.project_root
        
        import sys
        
        # Temp file for Scrapy to write stats into after spider closes
        stats_fd, stats_path = tempfile.mkstemp(suffix=".json", prefix="scrapy_stats_")
        os.close(stats_fd)

        cmd = [
            sys.executable, "-m", "scrapy", "crawl", "workplace_relations",
            "-a", f"start_date={start_date}",
            "-a", f"end_date={end_date}",
            "-a", f"body={','.join(bodies)}",
            "-a", f"base_url={base_url}",
            "-a", f"user_agents={','.join(user_agents)}",
            "-s", f"STATS_EXPORT_FILE={stats_path}",
        ]

        # Inject project root and src dir to PYTHONPATH
        src_dir = str(cwd / "src")
        env = os.environ.copy()
        env.update(env_vars)
        
        python_path = [str(cwd), src_dir]
        if env.get("PYTHONPATH"):
            python_path.append(env["PYTHONPATH"])
            
        env["PYTHONPATH"] = ":".join(python_path)

        self.logger.info(f"Starting Scrapy subprocess in {cwd}")
        
        process = subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False
        )

        # Forward every line from the spider subprocess to our logger
        if process.stdout:
            for line in process.stdout.splitlines():
                self.logger.info(line)

        raw_stats: dict = {}
        stats_missing = False
        try:
            with open(stats_path, encoding="utf-8") as fh:
                raw_stats = json.load(fh)
        except FileNotFoundError:
            stats_missing = True
            self.logger.error("WARNING: Scrapy stats file not found \u2014 spider may have crashed before writing stats.")
        except json.JSONDecodeError as exc:
            self.logger.error(f"WARNING: Could not parse Scrapy stats file: {exc}")
        finally:
            try:
                os.unlink(stats_path)
            except OSError:
                pass

        if process.returncode != 0 and stats_missing:
            self.logger.error(f"ERROR: Scrapy exited with code {process.returncode} and produced no stats.")

        def _safe_int(key: str) -> int:
            val = raw_stats.get(key, 0)
            try:
                return int(val)
            except (ValueError, TypeError):
                return 0

        def _safe_float(key: str) -> float:
            val = raw_stats.get(key, 0.0)
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0.0

        return ScrapeResult(
            returncode=process.returncode,
            stored=_safe_int("landing_pipeline/stored"),
            unchanged=_safe_int("landing_pipeline/unchanged"),
            failed=_safe_int("landing_pipeline/failed"),
            dropped=_safe_int("item_dropped_count"),
            pages_scraped=_safe_int("downloader/response_count"),
            elapsed_seconds=_safe_float("elapsed_time_seconds"),
            raw_stats=raw_stats,
        )
