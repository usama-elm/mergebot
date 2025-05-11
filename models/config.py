from msgspec import Struct, field


class MergeBotConfig(Struct):
    min_approvals: int = field(default=1)
    approvers: list[str] = field(default_factory=list)
    allow_failing_pipelines: bool = field(default=True)
    allow_failing_tests: bool = field(default=True)
    title_regex: str = field(default=".*")
    description_regex: str = field(default=".*")
    greetings_template: str = field(
        default="Requirements:\n - Min approvals: {{ min_approvals }}\n - Title regex: {{ title_regex }}\n\nOnce you've done, send **!merge** command and I will merge it!"
    )
    auto_master_merge: bool = field(default=False)
