ARG K_DISTRO=jammy
ARG K_COMMIT
FROM runtimeverificationinc/kframework-k:ubuntu-${K_DISTRO}-${K_COMMIT}
RUN    apt-get update        \
    && apt-get upgrade --yes \
    && apt-get install --yes \
         curl

ARG USER=user
ARG GROUP
ARG USER_ID=1000
ARG GROUP_ID=1000
RUN groupadd -g ${GROUP_ID} ${GROUP} && useradd -m -u ${USER_ID} -s /bin/sh -g ${GROUP} ${USER}
USER ${USER}:${GROUP}

RUN mkdir /home/${USER}/workspace
WORKDIR /home/${USER}/workspace

ENV PATH=/home/${USER}/.local/bin:${PATH}
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && uv --version
