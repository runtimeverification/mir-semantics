ARG K_COMMIT
FROM runtimeverificationinc/kframework-k:ubuntu-focal-${K_COMMIT}

RUN    apt-get update            \
    && apt-get upgrade --yes     \
    && apt-get install --yes     \
            debhelper            \
            python3              \
            python3-pip          \
            python-pygments      \
            rapidjson-dev        \
            z3                   \
            zlib1g-dev

RUN pip3 install virtualenv

RUN    git clone 'https://github.com/z3prover/z3' --branch=z3-4.8.15 \
    && cd z3                                                         \
    && python scripts/mk_make.py                                     \
    && cd build                                                      \
    && make -j8                                                      \
    && make install                                                  \
    && cd ../..                                                      \
    && rm -rf z3

RUN curl -sL https://deb.nodesource.com/setup_14.x | bash -
RUN    apt-get update               \
    && apt-get upgrade --yes        \
    && apt-get install --yes nodejs

RUN curl -sSL https://get.haskellstack.org/ | sh

ARG USER_ID=1000
ARG GROUP_ID=1000
RUN groupadd -g $GROUP_ID user && useradd -m -u $USER_ID -s /bin/sh -g user user

USER user:user
WORKDIR /home/user
