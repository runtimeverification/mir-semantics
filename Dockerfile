ARG K_VERSION
FROM runtimeverificationinc/kframework-k:ubuntu-jammy-$K_VERSION AS builder

RUN apt-get update && apt-get install -y \
    curl \
    git \
    gcc \
    g++ \
    make \
    python3 \
    python3-pip \
    python3-venv

RUN pip3 install poetry

RUN curl https://sh.rustup.rs -sSfy | sh

COPY . /app
WORKDIR /app

RUN make && make dist
RUN cd deps/stable-mir-json && git submodule update --init --recursive && :q

RUN echo "alias poetry-kmir='poetry -C /app/kmir/ run --'" >> /root/.bashrc

FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip

COPY --from=builder /app/kmir/dist/*.whl /app/kmir/dist/

RUN pip3 install /app/kmir/dist/*.whl
