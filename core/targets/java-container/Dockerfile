FROM amazoncorretto:21.0.4-alpine3.20
RUN set -eux && \
    apk add --clean-protected --no-cache \
            curl \
            bash && \
    curl -Ls https://sh.jbang.dev | bash -s - app setup
ENV PATH="/root/.jbang/bin:${PATH}"

RUN apk add --no-cache py3-pip
RUN python -mvenv /venv
RUN . /venv/bin/activate && pip install boto3

WORKDIR /app
COPY *.* ./
COPY targets/java-container/jbang-deps.txt ./
CMD . /venv/bin/activate && \
    python gen-1.py llm_client.py gen-1.py gen-2-specs.txt jbang-deps.txt -o Gen2.java -x 'jbang -- -t'
