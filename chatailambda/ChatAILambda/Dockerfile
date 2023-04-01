FROM public.ecr.aws/lambda/python:3.8

COPY ./requirements.txt .

RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY entrypoint.py ${LAMBDA_TASK_ROOT}
COPY helloworldhandler.py ${LAMBDA_TASK_ROOT}
COPY slackhandler.py ${LAMBDA_TASK_ROOT}
COPY logging.conf ${LAMBDA_TASK_ROOT}
COPY helloworld ${LAMBDA_TASK_ROOT}/helloworld
COPY slack ${LAMBDA_TASK_ROOT}/slack

ARG DD_KEY
ARG APP_VERSION

CMD ["entrypoint.handler"]
