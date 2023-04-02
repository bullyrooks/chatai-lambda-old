import os
import importlib
import json
import logging.config
import slackhandler

logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)

def handler(event, context):
    logger.info("in entrypoint")
    handler_module_name, handler_function_name = os.environ['HANDLER'].rsplit('.', 1)
    logger.info("handler: %s, %s", handler_module_name, handler_function_name)
    handler_module = importlib.import_module(handler_module_name)
    logger.info("got handler module")
    handler_function = getattr(handler_module, handler_function_name)
    logger.info("got handler function")
    return handler_function(event, context)

if __name__ == '__main__':
    # Simulate an event and context for local testing
    test_event = {}
    test_context = None

    response = handler(test_event, test_context)
    print(json.dumps(response, indent=2))