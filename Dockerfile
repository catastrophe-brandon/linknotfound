FROM registry.access.redhat.com/ubi8/python-38

LABEL author="eduardomcerqueira@gmail.com"
LABEL maintainer="eduardomcerqueira@gmail.com"
LABEL description="cli tool to find broken links in applications source code"

ENV GITHUB_TOKEN=${GITHUB_TOKEN:-""}
ENV GITHUB_USERNAME=${GITHUB_USERNAME:-"eduardocerqueira"}
ENV GITHUB_EMAIL=${GITHUB_EMAIL:-"eduardomcerqueira@gmail.com"}
ARG LINKNOTFOUND_RUN=${LINKNOTFOUND_RUN:-"test"}

RUN env | grep -e LINKNOTFOUND_RUN -e GITHUB -e GITHUB_TOKEN

RUN git config --global user.name $GITHUB_USERNAME
RUN git config --global user.email $GITHUB_EMAIL
RUN git config --global http.sslVerify false

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir devpi-client
RUN pip install --no-cache-dir -U pip setuptools setuptools_scm wheel

# install from repo/
# RUN git clone https://github.com/eduardocerqueira/linknotfound.git
# install from local, for debug and troubleshooting
ADD . linknotfound
WORKDIR linknotfound
COPY ops/scripts/docker_entrypoint.sh linknotfound/docker_entrypoint.sh

USER root
RUN chmod +x linknotfound/docker_entrypoint.sh
RUN chown -R 1001:0 .
RUN chmod -R 755 .

USER 1001
RUN pip install --no-cache-dir -e .
RUN pip freeze |grep linknotfound

# check on build
WORKDIR linknotfound
RUN linknotfound $LINKNOTFOUND_RUN

# on running
ENTRYPOINT ./docker_entrypoint.sh
