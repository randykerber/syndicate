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
        self._outbox_base = data_dir / "outbox"
        self._ship_base = data_dir / "ship"

        # Subclasses define these
        self.agent_name = None  # e.g., "claude", "gemini"
        self.output_filename = None  # e.g., "CLAUDE.md"

    @property
    def outbox_dir(self) -> Path:
        """Agent-specific outbox directory (computed from agent_name)."""
        if self.agent_name is None:
            raise ValueError("agent_name must be set before accessing outbox_dir")
        return self._outbox_base / self.agent_name

    @property
    def ship_dir(self) -> Path:
        """Agent-specific ship directory (computed from agent_name)."""
        if self.agent_name is None:
            raise ValueError("agent_name must be set before accessing ship_dir")
        return self._ship_base / self.agent_name

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

    def get_common_from_warehouse(self) -> Path:
        """
        Get curated COMMON.md from warehouse.

        Default implementation - no staging copy needed.

        Returns:
            Path to warehouse/common/COMMON.md
        """
        path = self.data_dir / "warehouse" / "common" / "COMMON.md"
        if not path.exists():
            raise FileNotFoundError(f"Missing: {path}")
        print(f"   ✓ Using: {path.name} from warehouse/common")
        return path

    def get_agent_specific_from_warehouse(self) -> Path:
        """
        Get agent-specific content from warehouse.

        Default implementation - no staging copy needed.
        Looks for warehouse/agents/{agent_name}/{AGENT}-specific.md

        Returns:
            Path to agent-specific file in warehouse
        """
        # Construct filename like "CLAUDE-specific.md", "GEMINI-specific.md"
        filename = f"{self.agent_name.upper()}-specific.md"
        path = self.data_dir / "warehouse" / "agents" / self.agent_name / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing: {path}")
        print(f"   ✓ Using: {filename} from warehouse/agents/{self.agent_name}")
        return path

    def get_common(self) -> Path:
        """
        Get common context content (shared across agents).

        Default: get from warehouse. Subclasses can override for custom sources.

        Returns:
            Path to common content file
        """
        return self.get_common_from_warehouse()

    def get_agent_specific(self) -> Path:
        """
        Get agent-specific context content.

        Default: get from warehouse. Subclasses can override for custom sources.

        Returns:
            Path to agent-specific content file
        """
        return self.get_agent_specific_from_warehouse()

    @property
    def include_coding(self) -> bool:
        """Whether to include coding-specific context."""
        return True  # All current agents are coding-oriented

    @property
    def include_personal(self) -> bool:
        """Whether to include personal context (interests, recreation, etc.)"""
        return False  # Only ChatGPT and Gemini include personal

    @property
    def include_info(self) -> bool:
        """Whether to include info files (subscriptions, etc.)"""
        return True  # Most agents benefit from factual info

    def get_personal_files(self) -> List[Path]:
        """Get personal context files. Returns empty list if not included."""
        if not self.include_personal:
            return []

        path = self.data_dir / "warehouse" / "common" / "PERSONAL.md"
        if not path.exists():
            raise FileNotFoundError(f"Missing: {path}")
        print(f"   ✓ Using: PERSONAL.md from warehouse/common")
        return [path]

    def get_coding_files(self) -> List[Path]:
        """Get coding-specific files. Returns empty list if not included."""
        if not self.include_coding:
            return []

        # Future: could return coding-specific supplemental files
        # For now, coding context is in COMMON.md
        return []

    def get_info_files(self) -> List[Path]:
        """Get supplementary info files from warehouse/common/info/."""
        if not self.include_info:
            return []

        info_dir = self.data_dir / "warehouse" / "common" / "info"
        if not info_dir.exists():
            return []

        # Recursively find all .md files in info/ directory
        info_files = sorted(info_dir.rglob("*.md"))
        for path in info_files:
            print(f"   ✓ Using: {path.relative_to(self.data_dir / 'warehouse' / 'common')}")
        return info_files

    def gather_inputs(self) -> List[Path]:
        """
        Collect source parts needed for this agent.

        Assembles from:
        - Common context (always)
        - Agent-specific context (always)
        - Personal files (if include_personal=True)
        - Coding files (if include_coding=True)
        - Info files (if include_info=True)

        Returns:
            List of Path objects to source files
        """
        inputs = [
            self.get_common(),
            self.get_agent_specific(),
        ]

        # Add optional components
        inputs.extend(self.get_personal_files())
        inputs.extend(self.get_coding_files())
        inputs.extend(self.get_info_files())

        return inputs

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

        TEMPORARY: Currently deploys to local ship/ directory for testing.
        Later will deploy to env/dot/config/{agent}/ with backup.

        Steps:
        1. Copy to outbox (for inspection)
        2. Copy to ship (temporary local deployment)

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

        # Step 2: Copy to ship (TEMPORARY - for testing)
        ship_path = self.ship_dir / self.output_filename
        ship_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(artifact, ship_path)
        print(f"🚢 Shipped to: {ship_path}")

        return ship_path

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
