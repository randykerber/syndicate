"""
Context Builder - Abstract base class for building and deploying agent context files.

Follows a process/task/function model with clear stages:
1. ensure_fresh_staging_area() - Clean workspace
2. gather_inputs() - Collect source parts
3. build() - Assemble final artifact
4. dispatch_results() - Deploy to destination
5. report_failure() - Handle errors
6. run() - Orchestrate full workflow
"""

import shutil
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import List, Optional


class ContextBuilder(ABC):
    """
    Abstract base class for building and deploying agent context files.

    Subclasses override methods to customize behavior for specific agents
    (Claude, Gemini, Warp, etc.).
    """

    def __init__(self, data_dir: Optional[Path] = None, env_dir: Optional[Path] = None):
        """
        Initialize builder with data and environment directories.

        Args:
            data_dir: Root data directory (default: syndicate/data/ace)
            env_dir: Environment config directory (default: ~/gh/randykerber/env/dot/config)
        """
        # Default paths - can be overridden via config later
        if data_dir is None:
            # Assume running from syndicate/python, go up to project root
            project_root = Path(__file__).parent.parent.parent.parent.parent
            data_dir = project_root / "data" / "ace"

        if env_dir is None:
            env_dir = Path.home() / "gh" / "randykerber" / "env" / "dot" / "config"

        self.data_dir = data_dir
        self.env_dir = env_dir
        self.staging_dir = data_dir / "staging"
        self.outbox_dir = data_dir / "outbox"

        # Subclasses define these
        self.agent_name = None  # e.g., "claude", "gemini"
        self.output_filename = None  # e.g., "CLAUDE.md"

    def ensure_fresh_staging_area(self) -> Path:
        """
        Create clean staging area for build process.

        Returns:
            Path to staging directory for this build
        """
        agent_staging = self.staging_dir / self.agent_name

        if agent_staging.exists():
            shutil.rmtree(agent_staging)

        agent_staging.mkdir(parents=True, exist_ok=True)

        print(f"📂 Created staging area: {agent_staging}")
        return agent_staging

    @abstractmethod
    def gather_inputs(self) -> List[Path]:
        """
        Collect source parts needed for this agent.

        Returns:
            List of Path objects to source files
        """
        pass

    def build(self, staging: Path, inputs: List[Path]) -> Path:
        """
        Assemble final artifact from inputs.

        Default implementation: simple concatenation.
        Subclasses can override for more sophisticated assembly.

        Args:
            staging: Staging directory for this build
            inputs: List of input files to concatenate

        Returns:
            Path to built artifact
        """
        output_path = staging / self.output_filename

        print(f"🔨 Building {self.output_filename}...")
        print(f"   Inputs: {[p.name for p in inputs]}")

        with output_path.open('w') as outfile:
            for i, input_path in enumerate(inputs):
                if i > 0:
                    outfile.write("\n\n---\n\n")  # Separator between parts

                print(f"   + {input_path.name}")
                with input_path.open('r') as infile:
                    outfile.write(infile.read())

        print(f"✅ Built: {output_path}")
        return output_path

    def dispatch_results(self, artifact: Path) -> Path:
        """
        Deploy built artifact to destination.

        Steps:
        1. Copy to outbox (for inspection)
        2. Backup existing destination file
        3. Copy to final destination

        Args:
            artifact: Path to built artifact in staging

        Returns:
            Path to deployed file
        """
        # Step 1: Copy to outbox
        outbox_path = self.outbox_dir / self.output_filename
        outbox_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(artifact, outbox_path)
        print(f"📦 Copied to outbox: {outbox_path}")

        # Step 2: Create backup of destination
        dest_dir = self.env_dir / self.agent_name
        dest_path = dest_dir / self.output_filename

        if dest_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = dest_dir / f"{self.output_filename}.{timestamp}.bak"
            shutil.copy2(dest_path, backup_path)
            print(f"💾 Backup created: {backup_path}")

        # Step 3: Deploy to destination
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(artifact, dest_path)
        print(f"🚀 Deployed: {dest_path}")

        return dest_path

    def report_failure(self, error: Exception):
        """
        Handle build/deployment failures.

        Args:
            error: Exception that occurred
        """
        print(f"\n❌ Build failed for {self.agent_name}: {error}")
        raise

    def run(self) -> Path:
        """
        Orchestrate full build and deployment workflow.

        Returns:
            Path to deployed artifact
        """
        try:
            print(f"\n{'=' * 60}")
            print(f"Building context for: {self.agent_name.upper()}")
            print(f"{'=' * 60}\n")

            # Stage 1: Prepare workspace
            staging = self.ensure_fresh_staging_area()

            # Stage 2: Collect inputs
            inputs = self.gather_inputs()

            # Stage 3: Build artifact
            artifact = self.build(staging, inputs)

            # Stage 4: Deploy
            deployed = self.dispatch_results(artifact)

            print(f"\n✅ SUCCESS: {self.output_filename} deployed to {deployed}")
            return deployed

        except Exception as e:
            self.report_failure(e)
