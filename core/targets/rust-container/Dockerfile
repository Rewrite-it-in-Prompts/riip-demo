FROM public.ecr.aws/docker/library/rust:alpine3.20 

RUN rustup update
RUN apk add --no-cache musl-dev

RUN apk add --no-cache py3-pip
RUN python -mvenv /venv
RUN . /venv/bin/activate && pip install boto3

WORKDIR /app
COPY *.* ./
COPY targets/rust-container/* ./
CMD . /venv/bin/activate && \
    python gen-1.py llm_client.py gen-1.py gen-2-specs.txt Cargo.toml guidance.txt -n 5 -o gen-2.rs -x 'cargo build'
