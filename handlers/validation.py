import re
from typing import Tuple
from models.merge_request import MergeRequestInfo
from models.config import MergeBotConfig


class MergeRequestValidator:
    @staticmethod
    def check_title(
        config: MergeBotConfig, mr_info: MergeRequestInfo
    ) -> Tuple[bool, bool]:
        if config.title_regex != ".*":
            match = re.match(config.title_regex, mr_info.title)
            return bool(match), True
        return True, False

    @staticmethod
    def check_description_regex(
        config: MergeBotConfig, mr_info: MergeRequestInfo
    ) -> Tuple[bool, bool]:
        if config.description_regex != ".*":
            match = re.match(config.description_regex, mr_info.description)
            return bool(match), True
        return True, False

    @staticmethod
    def check_approvals(
        config: MergeBotConfig, mr_info: MergeRequestInfo
    ) -> Tuple[bool, bool]:
        return len(mr_info.approvals) >= config.min_approvals, True

    @staticmethod
    def check_approvers(
        config: MergeBotConfig, mr_info: MergeRequestInfo
    ) -> Tuple[bool, bool]:
        if config.approvers:
            for approver in config.approvers:
                if approver not in mr_info.approvals:
                    return False, True
            return True, True
        return True, False

    @staticmethod
    def check_pipelines(
        config: MergeBotConfig, mr_info: MergeRequestInfo
    ) -> Tuple[bool, bool]:
        return mr_info.failed_pipelines == 0, not config.allow_failing_pipelines

    @staticmethod
    def check_tests(
        config: MergeBotConfig, mr_info: MergeRequestInfo
    ) -> Tuple[bool, bool]:
        return mr_info.failed_tests == 0, not config.allow_failing_tests

    @classmethod
    def validate(
        cls, config: MergeBotConfig, mr_info: MergeRequestInfo
    ) -> Tuple[bool, str]:
        checkers = [
            ("Le titre respecte les règles", cls.check_title),
            ("La description respecte les règles", cls.check_description_regex),
            ("Nombre d'approbations", cls.check_approvals),
            ("Approbateurs requis", cls.check_approvers),
            ("Pipeline", cls.check_pipelines),
            ("Tests", cls.check_tests),
        ]

        results = []
        is_valid = True

        for text, check_func in checkers:
            ok, applicable = check_func(config, mr_info)
            if not applicable:
                continue

            if ok:
                results.append(f"{text} ✅")
            else:
                results.append(f"{text} ❌")
                is_valid = False

        return is_valid, "\n\n".join(results)
