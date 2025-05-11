import os
import gitlab
import msgspec
from litestar import Request, HTTPException
from models.merge_request import MergeRequestInfo
from providers.base import WebhookProvider, RequestProvider


class GitLabWebhookProvider(WebhookProvider):
    def __init__(self):
        self.payload = None
        self.note = ""
        self.action = ""
        self.project_id = 0
        self.id = 0

    async def parse_request(self, request: Request) -> None:
        event_header = request.headers.get("X-Gitlab-Event", "")
        if not event_header.strip():
            raise HTTPException(
                status_code=401, detail="Unauthorized: Missing GitLab event header"
            )

        body = await request.body()
        self.payload = body.decode("utf-8")

        # Parse the JSON body
        try:
            data = msgspec.json.decode(body)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid payload: {str(e)}")

        # Handle merge request comment event
        if "object_attributes" in data and "note" in data.get("object_attributes", {}):
            self.project_id = data.get("project_id", 0)
            self.id = data.get("merge_request", {}).get("iid", 0)
            self.note = data.get("object_attributes", {}).get("note", "")

        # Handle merge request event
        elif "object_attributes" in data and "action" in data.get(
            "object_attributes", {}
        ):
            self.project_id = data.get("project", {}).get("id", 0)
            self.id = data.get("object_attributes", {}).get("iid", 0)
            self.action = data.get("object_attributes", {}).get("action", "")

    def is_new(self) -> bool:
        return self.action == "open"

    def is_valid(self) -> bool:
        return True

    def get_cmd(self) -> str:
        if self.note.startswith("!"):
            return self.note
        return ""

    def get_id(self) -> int:
        return self.id

    def get_project_id(self) -> int:
        return self.project_id


class GitLabRequestProvider(RequestProvider):
    def __init__(self):
        token = os.environ.get("GITLAB_TOKEN", "")
        url = os.environ.get("GITLAB_URL", "")

        if not token:
            raise ValueError("GitLab token not provided")

        if url:
            self.client = gitlab.Gitlab(url=url, private_token=token)
        else:
            self.client = gitlab.Gitlab(private_token=token)

        self.mr = None

    async def _load_mr(self, project_id: int, merge_id: int) -> None:
        if self.mr is not None:
            return

        try:
            project = self.client.projects.get(project_id)
            self.mr = project.mergerequests.get(merge_id)
        except Exception as e:
            raise ValueError(f"Failed to load merge request: {str(e)}")

    async def merge(self, project_id: int, merge_id: int, message: str) -> None:
        await self._load_mr(project_id, merge_id)
        self.mr.merge(
            squash=True, should_remove_source_branch=True, squash_commit_message=message
        )

    async def leave_comment(self, project_id: int, merge_id: int, message: str) -> None:
        await self._load_mr(project_id, merge_id)
        self.mr.notes.create({"body": message})

    async def get_mr_info(
        self, project_id: int, merge_id: int, path: str
    ) -> MergeRequestInfo:
        await self._load_mr(project_id, merge_id)

        # Check if MR is valid
        is_valid = self.mr.state == "opened" and not self.mr.has_conflicts

        # Get configuration content
        config_content = ""
        try:
            project = self.client.projects.get(project_id)
            file_content = project.files.get(file_path=path, ref=project.default_branch)
            config_content = file_content.decode().decode("utf-8")
        except Exception:
            pass  # Use default config if not found

        # Get approvals
        approvals = {}
        for note in self.mr.notes.list(all=True):
            if (
                note.body == "approved this merge request"
                and note.author["id"] != self.mr.author["id"]
            ):
                approvals[note.author["username"]] = {}
            elif note.body == "unapproved this merge request":
                approvals.pop(note.author["username"], None)

        # Check failed pipelines
        failed_pipelines = 0
        if (
            hasattr(self.mr, "pipeline")
            and self.mr.pipeline
            and self.mr.pipeline["status"] != "success"
        ):
            failed_pipelines = 1

        return MergeRequestInfo(
            approvals=approvals,
            failed_pipelines=failed_pipelines,
            failed_tests=0,  # We would need another API call to get this
            title=self.mr.title,
            description=self.mr.description or "",
            config_content=config_content,
            is_valid=is_valid,
        )

    async def update_from_master(self, project_id: int, merge_id: int) -> None:
        # This would typically use GitPython to update from master
        # For now we'll use the GitLab API to merge the target branch into the source branch
        await self._load_mr(project_id, merge_id)

        try:
            project = self.client.projects.get(project_id)
            self.mr.merge_ref()
        except Exception as e:
            raise ValueError(f"Failed to update from master: {str(e)}")
