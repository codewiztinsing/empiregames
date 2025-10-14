from .models import Agent
import logging

logger = logging.getLogger(__name__)


def get_agent_referral_link(agent):
    """
    Generate referral link for an agent
    """
    # This would typically be a URL that includes the agent code
    # For now, we'll return the agent code that can be used in the bot
    return f"https://t.me/wowbingobotbotbot?start=agent_{agent.agent_code}"
