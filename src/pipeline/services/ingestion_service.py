from __future__ import annotations

import logging
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


@dataclass
class ScrapeResult:
    returncode: int
    found: int = 0
    stored: int = 0
    failed: int = 0


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
        
        cmd = [
            sys.executable, "-m", "scrapy", "crawl", "workplace_relations",
            "-a", f"start_date={start_date}",
            "-a", f"end_date={end_date}",
            "-a", f"body={','.join(bodies)}",
            "-a", f"base_url={base_url}",
            "-a", f"user_agents={','.join(user_agents)}",
        ]

        # Inject project root and src dir to PYTHONPATH
        # This allows finding 'src.pipeline' and 'workplace_relations' (which is in src)
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
            capture_output=True,
            text=True,
            check=False
        )

        if process.stdout:
            self.logger.debug(process.stdout)
        if process.stderr:
            self.logger.error(process.stderr)

        return ScrapeResult(returncode=process.returncode)
