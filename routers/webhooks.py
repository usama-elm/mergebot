import logging
from litestar import APIRouter, Request, HTTPException, Path, post
import asyncio

from providers.base import WebhookProvider, RequestProvider
from providers.gitlab import GitLabWebhookProvider, GitLabRequestProvider
from handlers.merge import merge_command
from handlers.check import check_command
from handlers.validation import MergeRequestValidator

router = APIRouter()

# Provider registry
webhook_providers = {"gitlab": GitLabWebhookProvider}

request_providers = {"gitlab": GitLabRequestProvider}

# Event handlers
event_handlers = {
    "!merge": merge_command,
    "!check": check_command,
    "\anew_mr": None,  # Will be implemented
}


@post("/mergebot/webhook/{provider:str}/{owner:str}/{repo:str}/")
async def webhook_handler(
    request: Request,
    provider: str = Path(...),
    owner: str = Path(...),
    repo: str = Path(...),
):
    # Create provider instance
    if provider not in webhook_providers:
        raise HTTPException(status_code=404, detail=f"Provider {provider} not found")

    webhook_provider_class = webhook_providers[provider]
    webhook_provider = webhook_provider_class()

    # Parse the request
    try:
        await webhook_provider.parse_request(request)
    except Exception as e:
        logging.error(f"Error parsing request: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    # Determine the event
    event = "\anew_mr" if webhook_provider.is_new() else webhook_provider.get_cmd()

    # Handle the event asynchronously
    if event in event_handlers and event_handlers[event]:
        # Process in background
        asyncio.create_task(
            process_event(
                event,
                provider,
                webhook_provider.get_project_id(),
                webhook_provider.get_id(),
            )
        )

    return {"status": "ok"}


async def process_event(
    event: str,
    provider: str,
    project_id: int,
    mr_id: int,
):
    """Process an event in the background."""
    try:
        if provider not in request_providers:
            logging.error(f"Provider {provider} not found")
            return

        request_provider_class = request_providers[provider]
        request_provider = request_provider_class()

        # Execute the handler
        handler = event_handlers.get(event)
        if handler:
            await handler(request_provider, project_id, mr_id)

    except Exception as e:
        logging.error(f"Error processing event {event}: {str(e)}")
