import os
import importlib
import json

def handler(event, context):
    handler_module_name, handler_function_name = os.environ['HANDLER'].rsplit('.', 1)
    handler_module = importlib.import_module(handler_module_name)
    handler_function = getattr(handler_module, handler_function_name)

    return handler_function(event, context)

if __name__ == '__main__':
    # Simulate an event and context for local testing
    test_event = {}
    test_context = None

    response = handler(test_event, test_context)
    print(json.dumps(response, indent=2))