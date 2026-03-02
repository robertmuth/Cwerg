# Load bats support libraries.
bats_load_library 'bats-support'
bats_load_library 'bats-assert'
bats_load_library 'bats-file'

debug() {
  echo '# --- DEBUG: ' "$@" >&3
}

force_error() {
  echo '# --- ERROR: ' "$@" >&3
  exit 1
}

setup_all() {
  [[ -n "${DOCKER_IMAGE}" ]] \
    || force_error 'DOCKER_IMAGE environment variable not defined'

  # Make sure the docker image exists.
  docker inspect "${DOCKER_IMAGE}" > /dev/null \
    || force_error "DOCKER_IMAGE '${DOCKER_IMAGE}' does not exist"

  # Create workdir to store temporary stuff. Not all mktemp take a destination
  # directory willingly, so we work around that.
  TESTS_WORKDIR_ORIG="$(mktemp)"
  TESTS_WORKDIR=$(basename "${TESTS_WORKDIR_ORIG}")
  mkdir "${TESTS_WORKDIR}"
  export TESTS_WORKDIR
  # Save build directory, if there is one (for local testing).
  BUILD_SAVED="build-${TESTS_WORKDIR}"
  if [[ -e build ]]; then
    mv build "${BUILD_SAVED}"
  fi
}

teardown_all() {
  # Restore saved build directory.
  if [[ -e "${BUILD_SAVED}" ]]; then
    rm -rf build
    mv "${BUILD_SAVED}" build
  fi
  # Remove temporary work directories.
  rm -rf "${TESTS_WORKDIR}" "${TESTS_WORKDIR_ORIG}"
}

# Run a command in the container.
run_in_container() {
  if [[ -n "${PLATFORM}" ]]; then
    args="--platform ${PLATFORM}"
  fi
  echo "run_in_container: $*"
  # shellcheck disable=SC2086 # Double quote to prevent word splitting
  run docker run ${args} --rm -v .:/Cwerg "${DOCKER_IMAGE}" "$@"
}
