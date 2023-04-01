import logging
import logging.config

logging.config.fileConfig('logging.conf')

from helloworld.chat import Chat


logger = logging.getLogger(__name__)


def handler(event, context):
    logger.info("handler request in")
    return {
        'statusCode': 200,
        'body': Chat.getMessage().json()
    }
