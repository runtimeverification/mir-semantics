ARG K_DISTRO=jammy

K_COMMIT=$(grep -Po '[0-9.]+' ./deps/k_release)
docker build . --tag ${TAG} --build-arg K_COMMIT=${K_COMMIT}

FROM runtimeverificationinc/kframework-k:ubuntu-${K_DISTRO}-${K_COMMIT}

RUN    apt-get update        \
    && apt-get upgrade --yes \
    && apt-get install --yes \
         curl

RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/usr python3 - --version 1.3.2

ARG USER_ID=1000
ARG GROUP_ID=1000
RUN groupadd -g $GROUP_ID user && useradd -m -u $USER_ID -s /bin/sh -g user user

COPY --chown=user:user . /home/user