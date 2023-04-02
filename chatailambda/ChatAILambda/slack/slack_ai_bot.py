import os
import json
import boto3
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import logging.config
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)


# Set up AWS Lambda client
lambda_client = boto3.client('lambda', region_name=os.environ["AWS_REGION"])
# API key for the "Hello, World!" Lambda function
ssm = boto3.client('ssm', region_name=os.environ["AWS_REGION"])
apikeyresponse = ssm.get_parameter(
    Name='/prod/chatai/lambda.api.key',
    WithDecryption=True
)
api_key = apikeyresponse["Parameter"]["Value"]

bottokenresponse = ssm.get_parameter(
    Name='/prod/chatai/slack.bot.token',
    WithDecryption=True
)
bot_token = bottokenresponse["Parameter"]["Value"]

apptokenresponse = ssm.get_parameter(
    Name='/prod/chatai/slack.app.token',
    WithDecryption=True
)
app_token = apptokenresponse["Parameter"]["Value"]

slack_client = WebClient(token=app_token)

def say(channel, message):
    try:
        response = slack_client.chat_postMessage(channel=channel, text=message)
    except SlackApiError as e:
        print(f"Error posting message: {e}")

app = App(token=bot_token)

@app.event("app_mention")
async def command_handler(body, channelId):
    text = body['event']['text']
    user = body['event']['user']

    # Ignore messages from the bot itself
    if user == 'helloworld':
        return
    logger.info("api key : %s",api_key)

    logger.info("calling lambda")

    # Process the text and get the response from the Lambda function
    response = lambda_client.invoke(
        FunctionName='chatai-message',
        InvocationType='RequestResponse',
        Payload=json.dumps({'text': text}),
        ClientContext=json.dumps({'custom': {'x-api-key': api_key}})
    )

    # Parse the response from the Lambda function
    response_payload = json.loads(response['Payload'].read().decode())
    logger.info("got response: %s", response_payload)

    # Send the response back to the Slack channel
    await say(channelId, response_payload['response'])

    return response_payload