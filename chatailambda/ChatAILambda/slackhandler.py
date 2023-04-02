import logging.config
import json

logging.config.fileConfig('logging.conf')

from slack.slack_ai_bot import command_handler



logger = logging.getLogger(__name__)


def handler(event, context):
    logger.info("slack handler request in")
    # Get the input text from the event
    text = event.get('text', '')

    # Call the command_handler function from the slack_ai_bot module
    logger.info("calling slack handler")
    response = command_handler(text)
    logger.info("slack handler response: %s", response)

    # Return the response as a JSON object
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
