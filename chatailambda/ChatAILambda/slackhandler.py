import asyncio
import logging.config
import json


from slack.slack_ai_bot import command_handler, say


logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)


def handler(event, context):
    logger.info("slack handler request in: %s", event)
    logger.info("slack body: %s", event['body'])

    # Call the command_handler function from the slack_ai_bot module
    logger.info("calling slack handler")
    loop = asyncio.get_event_loop()
    response = loop.run_until_complete(command_handler(event['body'], say))

    logger.info("slack handler response: %s", response)

    # Return the response as a JSON object
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }


