import asyncio
import logging.config
import json
import os

from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler
import boto3


logger = logging.getLogger(__name__)

ssm = boto3.client('ssm', region_name=os.environ["AWS_REGION"])
bottokenresponse = ssm.get_parameter(
    Name='/prod/chatai/slack.bot.token',
    WithDecryption=True
)
bot_token = bottokenresponse["Parameter"]["Value"]

# process_before_response must be True when running on FaaS
app = App(process_before_response=True, token=bot_token, logger=logger)

@app.event("app_mention")
def handle_app_mentions(body, say, logger):
    logger.info(body)
    say("What's up?")

def handler(event, context):
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)



