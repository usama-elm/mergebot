from abc import ABC, abstractmethod
from litestar import Request
from models.merge_request import MergeRequestInfo


class WebhookProvider(ABC):
    @abstractmethod
    async def parse_request(
        self,
        request: Request,
    ) -> None:
        pass

    @abstractmethod
    def is_new(self) -> bool:
        pass

    @abstractmethod
    def is_valid(self) -> bool:
        pass

    @abstractmethod
    def get_cmd(self) -> str:
        pass

    @abstractmethod
    def get_id(self) -> int:
        pass

    @abstractmethod
    def get_project_id(self) -> int:
        pass


class RequestProvider(ABC):
    @abstractmethod
    async def merge(
        self,
        project_id: int,
        merge_id: int,
        message: str,
    ) -> None:
        pass

    @abstractmethod
    async def leave_comment(
        self,
        project_id: int,
        merge_id: int,
        message: str,
    ) -> None:
        pass

    @abstractmethod
    async def get_mr_info(
        self,
        project_id: int,
        merge_id: int,
        path: str,
    ) -> MergeRequestInfo:
        pass

    @abstractmethod
    async def update_from_master(
        self,
        project_id: int,
        merge_id: int,
    ) -> None:
        pass
