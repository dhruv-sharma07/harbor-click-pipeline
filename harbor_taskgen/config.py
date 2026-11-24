"""
Harbor Task Generation Pipeline Configuration
Conforms to Harbor v0.25.x Standardized Architecture
Target Repository: pallets/click
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

HARBOR_SCHEMA_VERSION = "0.25.0"

# Target Repository Details
TARGET_REPO_URL = "https://github.com/pallets/click"
TARGET_REPO_NAME = "click"
TARGET_REPO_ORG = "pallets"
DEFAULT_BASELINE_COMMIT = "e0d8b5847e2ef30fa27ce803405c19be38d17ba7"  # Click 8.1.x stable baseline

@dataclass
class TaskEnvironmentConfig:
    os: str = "linux"
    base_image: str = "python:3.11-slim"
    cpus: int = 2
    memory_mb: int = 4096
    storage_mb: int = 10240
    gpus: int = 0

@dataclass
class TaskMetadata:
    name: str
    author: str
    difficulty: str  # easy | medium | hard
    category: str = "software-engineering"
    tags: List[str] = field(default_factory=lambda: ["python", "cli", "pallets-click", "bugfix"])
    summary: str = ""
    baseline_commit: str = DEFAULT_BASELINE_COMMIT
    issue_id: Optional[str] = None

@dataclass
class TaskDefinition:
    metadata: TaskMetadata
    instruction: str
    solution_patch: str
    test_patch: str
    agent_timeout_sec: int = 600
    verifier_timeout_sec: int = 180
    env_config: TaskEnvironmentConfig = field(default_factory=TaskEnvironmentConfig)
