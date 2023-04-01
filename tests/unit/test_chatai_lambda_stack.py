import aws_cdk as core
import aws_cdk.assertions as assertions

from chatailambda.chatai_lambda_stack import ChatAILambdaStack

# example tests. To run these tests, uncomment this file along with the example
# resource in python_cdk_helloworld/chatai_lambda_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ChatAILambdaStack(app, "chatai_lambda")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
