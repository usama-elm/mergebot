import logging
import yaml
from jinja2 import Template
from providers.base import RequestProvider
from models.config import MergeBotConfig
from handlers.validation import MergeRequestValidator


async def merge_command(provider: RequestProvider, project_id: int, mr_id: int):
    """Handle the !merge command."""
    try:
        # Get MR info and config
        mr_info = await provider.get_mr_info(project_id, mr_id, ".mrbot.yaml")

        # Parse config
        config = parse_config(mr_info.config_content)

        # Update from master if needed
        if config.auto_master_merge:
            try:
                await provider.update_from_master(project_id, mr_id)
            except Exception as e:
                logging.error(f"Failed to update from master: {str(e)}")

        # Validate the MR
        is_valid, validation_message = MergeRequestValidator.validate(config, mr_info)

        if is_valid:
            # Merge the MR
            await provider.merge(
                project_id, mr_id, f"{mr_info.title}\nMerged by MergeApproveBot"
            )
        else:
            # Leave a comment with validation results
            await provider.leave_comment(project_id, mr_id, validation_message)

    except Exception as e:
        logging.error(f"Error in merge command: {str(e)}")
        try:
            await provider.leave_comment(
                project_id, mr_id, f"Error executing merge: {str(e)}"
            )
        except:
            pass


def parse_config(content: str) -> MergeBotConfig:
    """Parse the configuration from YAML content."""
    try:
        if content:
            config_dict = yaml.safe_load(content)
            return MergeBotConfig(**config_dict)
    except Exception as e:
        logging.error(f"Error parsing config: {str(e)}")

    # Return default config if parsing fails
    return MergeBotConfig()
