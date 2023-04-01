FROM public.ecr.aws/lambda/python:3.8

COPY ./requirements.txt .

RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"
#https://docs.datadoghq.com/serverless/installation/python/?tab=containerimage
COPY --from=public.ecr.aws/datadog/lambda-extension:latest /opt/extensions/ /opt/extensions

COPY lambda.py ${LAMBDA_TASK_ROOT}
COPY logging.conf ${LAMBDA_TASK_ROOT}
COPY chatai ${LAMBDA_TASK_ROOT}/chatai

ARG DD_KEY
ARG APP_VERSION
