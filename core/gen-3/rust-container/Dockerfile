FROM public.ecr.aws/docker/library/rust:alpine3.20 

RUN rustup update
RUN apk add --no-cache musl-dev

RUN apk add --no-cache py3-pip
RUN python -mvenv /venv
RUN . /venv/bin/activate && pip install boto3 pyyaml

WORKDIR /build
COPY *.* ./
COPY gen-3/rust-container/*.* ./
CMD . /venv/bin/activate && \
    echo "Review the specs and code below, then follow the rewrite instructions." | \
    python gen-2.py -l rust \
    - gen-2-specs.txt gen-2.py rust-guide.txt project/Cargo.toml \
    -n 2 -o project -x 'cargo build'
