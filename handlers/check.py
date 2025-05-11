import logging
from providers.base import RequestProvider
from handlers.merge import parse_config
from handlers.validation import MergeRequestValidator


async def check_command(provider: RequestProvider, project_id: int, mr_id: int):
    """Handle the !check command."""
    try:
        # Get MR info and config
        mr_info = await provider.get_mr_info(project_id, mr_id, ".mrbot.yaml")

        # Parse config
        config = parse_config(mr_info.config_content)

        # Validate the MR
        is_valid, validation_message = MergeRequestValidator.validate(config, mr_info)

        if is_valid:
            await provider.leave_comment(project_id, mr_id, "You can merge, LGTM :D")
        else:
            await provider.leave_comment(project_id, mr_id, validation_message)

    except Exception as e:
        logging.error(f"Error in check command: {str(e)}")
        try:
            await provider.leave_comment(
                project_id, mr_id, f"Error executing check: {str(e)}"
            )
        except:
            pass
