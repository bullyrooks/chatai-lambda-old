import os

from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway)
from aws_cdk import aws_ssm as ssm
from aws_cdk.aws_apigateway import (
    ApiKey,
    UsagePlan,
    RestApi,
    ThrottleSettings,
    LambdaIntegration)
from aws_cdk.aws_ecr import Repository
from constructs import Construct
from aws_cdk import aws_secretsmanager as secretsmanager


class ChatAILambdaStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.build_lambda_func()

    def build_lambda_func(self):
        image_tag = os.getenv("IMAGE_TAG", "latest")
        self.ecr_image = _lambda.DockerImageCode.from_ecr(
            repository=Repository.from_repository_name(self, "chatai-lambda-repository", "chatai-lambda"),
            tag_or_digest=image_tag
        )
        self.chatai_lambda = _lambda.DockerImageFunction(
            scope=self,
            id="chatai-lambda",
            function_name="chatai_message",
            code=self.ecr_image,
            environment={
                'HANDLER': 'helloworldhandler.handler'
            }
        )

        chatai_api = RestApi(self, "chatai-lambda-gw",
                             rest_api_name="ChatAI Service",
                             description="This service fronts chatai.",
                             api_key_source_type=apigateway.ApiKeySourceType.HEADER)

        chatai_integration = LambdaIntegration(
            self.chatai_lambda,
            request_templates={"application/json": '{ "statusCode": "200" }'})

        # Add a method to the API Gateway with API key requirement
        chatai_api.root.add_method("GET", chatai_integration, api_key_required=True)

        # Create an API key
        test_key = ApiKey(self, "DEV Test Key", api_key_name="devTestKey", enabled=True)

        # Create a usage plan
        development_usage_plan = UsagePlan(self,
                                           "Dev Usage Plan",
                                           throttle=ThrottleSettings(
                                               rate_limit=10,  # requests per second
                                               burst_limit=2  # maximum number of requests in a burst
                                           ),
                                           quota=apigateway.QuotaSettings(
                                               limit=200,  # number of requests
                                               period=apigateway.Period.DAY  # time period
                                           )
                                           )

        # Associate the API key with the usage plan
        development_usage_plan.add_api_key(test_key)

        ## Slack lambda

        # get the api key needed to talk to the lambda
        lambda_api_key = secretsmanager.Secret.from_secret_complete_arn(
            self, "LambdaApiKey", "arn:aws:secretsmanager:us-west-2:108452827623:secret:prod/chat/lambda.api.key-XrRQPL"
        )

        self.slack_lambda = _lambda.DockerImageFunction(
            scope=self,
            id="slack-lambda",
            function_name="slack-bot",
            code=self.ecr_image,
            environment={
                'HANDLER': 'slackhandler.handler',
                "LAMBDA_API_KEY": lambda_api_key.secret_value,
            }
        )

        slack_api = RestApi(self, "slack-lambda-gw",
                            rest_api_name="Slack Service",
                            description="This service handles slack requests")

        slack_integration = LambdaIntegration(
            self.slack_lambda,
            request_templates={"application/json": '{ "statusCode": "200" }'})

        # Add a method to the API Gateway with API key requirement
        slack_api.root.add_method("POST", slack_integration)
