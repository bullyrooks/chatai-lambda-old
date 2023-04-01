import os
import json
import boto3
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

app = App()

# Set up AWS Lambda client
lambda_client = boto3.client('lambda', region_name=os.environ["AWS_REGION"])
# API key for the "Hello, World!" Lambda function
api_key = os.environ["LAMBDA_API_KEY"]

@app.event("app_mention")
async def command_handler(body, say):
    text = body['event']['text']
    user = body['event']['user']

    # Ignore messages from the bot itself
    if user == 'helloworld':
        return

    # Process the text and get the response from the Lambda function
    response = lambda_client.invoke(
        FunctionName='chatai-message',
        InvocationType='RequestResponse',
        Payload=json.dumps({'text': text}),
        ClientContext=json.dumps({'custom': {'x-api-key': api_key}})
    )

    # Parse the response from the Lambda function
    response_payload = json.loads(response['Payload'].read().decode())

    # Send the response back to the Slack channel
    await say(response_payload['response'])