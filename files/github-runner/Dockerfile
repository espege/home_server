FROM ubuntu:24.04

ARG RUNNER_VERSION="2.329.0" # https://github.com/actions/runner/releases
ARG TZ_LOCATION="America/Montreal"
ENV DEBIAN_FRONTEND=noninteractive

LABEL Author="SPG"
LABEL BaseImage="ubuntu:24.04"
LABEL RunnerVersion=${RUNNER_VERSION}

# update the base packages + add a non-sudo user
RUN apt-get update -y && apt-get upgrade -y && useradd -m docker

# Make sure tzdata doesn't prompt during next step
RUN ln -fs /usr/share/zoneinfo/${TZ_LOCATION} /etc/localtime && DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata

# install the packages and dependencies along with jq so we can parse JSON (add additional packages as necessary)
RUN apt-get install -y --no-install-recommends \
    curl nodejs wget unzip vim git jq build-essential python3 python3-venv python3-pip

# cd into the user directory, download and unzip the github actions runner
RUN cd /home/docker && mkdir actions-runner && cd actions-runner \
    && curl -O -L https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz \
    && tar xzf ./actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

# install some additional dependencies
RUN chown -R docker ~docker && /home/docker/actions-runner/bin/installdependencies.sh

# add over the start.sh script
ADD scripts/start.sh start.sh

# make the script executable
RUN chmod +x start.sh

# set the user to "docker" so all subsequent commands are run as the docker user
USER docker

# set the entrypoint to the start.sh script
ENTRYPOINT ["./start.sh"]
