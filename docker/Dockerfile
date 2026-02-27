# This Dockerfile creates a container for a development environment for Cwerg.
#
# To build the docker image, run the following from the Cwerg directory:
#   docker build -t cwerg-dev-env docker
#
# To base it on a different distro, override BASEIMGAE, e.g., add:
#   --build-arg BASEIMAGE=alpine:3.23
#
# To use this dev environment, run the following from the Cwerg directory:
#   docker run -it --rm -v .:/Cwerg cwerg-dev-env
# Your Cwerg repository directory from the host will be mounted as /Cwerg inside
# the container.
#
# The image includes the build environment for the C++ version of Cwerg as well
# as a Python interpreter to run the Python version of Cwerg and the Cwerg
# compiler driver.

ARG BASEIMAGE=ubuntu:24.04

#############################################################################
# Create a development environment for the Cwerg compiler.
#############################################################################
FROM ${BASEIMAGE}

# hadolint ignore=DL3008,DL3018  # Pin versions in apt/apk.
RUN  <<EO_RUN
  set -ex

  if grep -q "ID=alpine" /etc/os-release; then 
    apk add --update --no-cache \
      make cmake g++ libunwind-dev libunwind-static xz-static python3
    # Only /usr/bin/env is present by default, but cwerg uses /bin/env.
    ln -s /bin/busybox /bin/env
  else
    # Ubuntu and friends.
    apt-get update
    apt-get install -y --no-install-recommends \
      make cmake g++ libunwind-dev python3

    # Clean up apt installation caches and unnecessary packages.
    apt-get autoremove -y
    rm -rf /var/lib/apt/lists/*
    apt-get clean
  fi
EO_RUN

# Location to mount the Cwerg git repository.
VOLUME ["/Cwerg"]

# Image metadata.
ARG IMAGE_VERSION=unknown
LABEL \
  org.opencontainers.image.name="cwerg-dev-env" \
  org.opencontainers.image.description="Cwerg Development Environment" \
  org.opencontainers.image.version="${IMAGE_VERSION}" \
  org.opencontainers.image.url="https://github.com/RobertMuth/Cwerg" \
  org.opencontainers.image.source="https://github.com/RobertMuth/Cwerg"
