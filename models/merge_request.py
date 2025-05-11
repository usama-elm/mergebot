from typing import Any

from msgspec import Struct


class MergeRequestInfo(Struct):
    approvals: dict[str, Any]
    failed_pipelines: int
    failed_tests: int
    title: str
    description: str
    config_content: str
    is_valid: bool
