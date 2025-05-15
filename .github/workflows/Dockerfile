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

ENV PATH="/home/${USER}/.cargo/bin:${PATH}"
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y
RUN rustup toolchain install nightly-2024-11-29 --component llvm-tools --component rustc-dev --component rust-src
RUN rustup default nightly-2024-11-29-x86_64-unknown-linux-gnu

RUN mkdir /home/${USER}/workspace
WORKDIR /home/${USER}/workspace

ENV PATH=/home/${USER}/.local/bin:${PATH}
RUN curl -LsSf https://astral.sh/uv/0.7.2/install.sh  | sh && uv --version
