from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway, CfnParameter,
)
import os
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
            # Function name on AWS
            function_name="chatai_message",
            # Use aws_cdk.aws_lambda.DockerImageCode.from_image_asset to build
            # a docker image on deployment
            code=self.ecr_image,
        )

        api = apigateway.RestApi(self, "chatai-lambda-gw",
                                 rest_api_name="ChatAI Service",
                                 description="This service fronts chatai.")

        chatai_integration = apigateway.LambdaIntegration(
            self.chatai_lambda,
            request_templates={"application/json": '{ "statusCode": "200" }'})

        api.root.add_method("GET", chatai_integration)
