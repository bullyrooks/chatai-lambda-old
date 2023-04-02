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
from aws_cdk import aws_iam as iam
from aws_cdk import aws_kms as kms

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

        # Create a KMS key
        ssm_key = kms.Key.from_key_arn(self, "DefaultSSMKey", key_arn="arn:aws:kms:us-west-2:108452827623:key/c4cc2c51-c954-4f6c-a383-5e75e6dc8cce")

        # store the key in SSM after creation
        ssm.SecureStringParameter(
            self,
            "ApiKeySecureParameter",
            parameter_name="/prod/chatai/lambda.api.key",
            string_value=test_key.key_value,
            description="API key for devTestKey as a secure string",
            encryption_key=ssm_key
        )
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

        self.slack_lambda = _lambda.DockerImageFunction(
            scope=self,
            id="slack-lambda",
            function_name="slack-lambda",
            code=self.ecr_image,
            environment={
                'HANDLER': 'slackhandler.handler',
            }
        )
        # Assuming your Lambda function is defined as self.slack_lambda
        self.slack_lambda.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMReadOnlyAccess")
        )
        ssm_policy_statement = iam.PolicyStatement(
            actions=["ssm:GetParameter"],
            resources=["arn:aws:ssm:us-west-2:108452827623:parameter/prod/chatai/lambda.api.key",
                       "arn:aws:ssm:us-west-2:108452827623:parameter/prod/chatai/slack.app.token",
                       "arn:aws:ssm:us-west-2:108452827623:parameter/prod/chatai/slack.bot.token",
                       ],
            effect=iam.Effect.ALLOW
        )
        self.slack_lambda.role.add_to_policy(ssm_policy_statement)

        slack_api = RestApi(self, "slack-lambda-gw",
                            rest_api_name="Slack Service",
                            description="This service handles slack requests")

        slack_integration = LambdaIntegration(
            self.slack_lambda,
            request_templates={"application/json": '{ "statusCode": "200" }'})

        # Add a method to the API Gateway with API key requirement
        slack_api.root.add_method("POST", slack_integration)
