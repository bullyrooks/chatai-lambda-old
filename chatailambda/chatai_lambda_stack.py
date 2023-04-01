import os

from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as _lambda )
from aws_cdk.aws_apigateway import ApiKey, UsagePlan, RestApi, UsagePlanProps, ThrottleSettings, LambdaIntegration
from aws_cdk.aws_ecr import Repository
from constructs import Construct


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
        )

        api = RestApi(self, "chatai-lambda-gw",
                                 rest_api_name="ChatAI Service",
                                 description="This service fronts chatai.",
                                 deploy_options={
                                     "api_key_source_type": "HEADER"
                                 })

        chatai_integration = LambdaIntegration(
            self.chatai_lambda,
            request_templates={"application/json": '{ "statusCode": "200" }'})

        # Add a method to the API Gateway with API key requirement
        api.root.add_method("GET", chatai_integration, api_key_required=True)

        # Create an API key
        test_key = ApiKey(self, "DEV Test Key", api_key_name="devTestKey", enabled=True)

        # Create a usage plan
        development_usage_plan = UsagePlan(self,
                                           "Dev Usage Plan",
                                           api_stages=[
                                               UsagePlanProps(api=api, stage=api.deployment_stage)
                                           ],
                                           throttle=ThrottleSettings(
                                               rate_limit=100 / 3600,  # requests per second
                                               burst_limit=10  # maximum number of requests in a burst
                                           ),
                                           quota={
                                               "limit": 100,  # number of requests
                                               "period": apigateway.Period.HOUR  # time period
                                           }
                                           )

        # Associate the API key with the usage plan
        development_usage_plan.add_api_key(test_key)
