FROM node:lts-alpine3.20

RUN apk add --no-cache py3-pip
RUN python -mvenv /venv
RUN . /venv/bin/activate && pip install boto3

WORKDIR /app
RUN npm init --yes
RUN npm install -g typescript
RUN npx tsc --init
RUN npm i --save-dev @types/node
RUN npm install @aws-sdk/client-bedrock-runtime

COPY *.* ./
COPY targets/ts-container/Dockerfile ./
CMD . /venv/bin/activate && \
    python llm_client.py gen-2.py gen-2-specs.txt Dockerfile -o gen3.ts -x 'tsc --'
