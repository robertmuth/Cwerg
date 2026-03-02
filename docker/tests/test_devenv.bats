#!/bin/env bats

load utils

@test "Checking that python3 exists..." {
  run_in_container which python3
  assert_success
}

@test "Checking that python3 version is >= 3.10..." {
  run_in_container python3 --version
  assert_success
  assert_output --regexp "Python 3\.[0-9]{2,}\.[0-9]+"
}

@test "Checking that g++ exists..." {
  run_in_container which g++
  assert_success
}

@test "Checking that g++ runs..." {
  run_in_container g++ --version
  assert_success
}

@test "Checking that g++ supports c++20..." {
  local src="${TESTS_WORKDIR}/test_c++20.cpp"
  local exe="${TESTS_WORKDIR}/test_c++20.exe"

  cat - >"${src}" <<EOF
    #include <iostream>

    int main() {
      std::cout << "C++20 supported!" << std::endl;
      return 0;
    }
EOF
  # First build it.
  run_in_container sh -c \
    "cd /Cwerg; g++ -std=c++20 ${src} -o ${exe}"
  assert_success
  assert_exists "${exe}"

  # Then run it.
  run_in_container "/Cwerg/${exe}"
  assert_success
  assert_output 'C++20 supported!'
}

@test "Checking that /Cwerg was mounted correctly..." {
  # Though if it weren't, it would be an internal test infrastructure failure,
  # not a failure of the container that we're trying to check.
  run_in_container test -f /Cwerg/cwerg.py
  assert_success
}

# Now move on to more elaborate tests.

test_src='FE/TestData/hello_world_test.cw'
exe_py="${TESTS_WORKDIR}/hello.py.exe"
exe_cxx="${TESTS_WORKDIR}/hello.c++.exe"

@test "Checking that we can run Python Cwerg..." {
  run_in_container sh -c \
    "cd Cwerg; ./cwerg.py -be py -fe py ${test_src} ${exe_py}"
  assert_success
  assert_exists "${exe_py}"
}

@test "Checking that we can run Python compiled binary..." {
  run_in_container "/Cwerg/${exe_py}"
  assert_success
  assert_output --partial "hello world"
}

# bats test_tags=slow
@test "Checking that we can build C++ Cwerg..." {
  run_in_container sh -c "cd Cwerg; make build_compiler"
  assert_success
  assert_exists build/compiler.exe
}

# bats test_tags=slow
@test "Checking that we can run C++ Cwerg..." {

  run_in_container sh -c "cd Cwerg; ./cwerg.py ${test_src} ${exe_cxx}"
  assert_success
  assert_exists "${exe_cxx}"
}

# bats test_tags=slow
@test "Checking that we can run C++ compiled binary..." {
  run_in_container "/Cwerg/${exe_cxx}"
  assert_success
  assert_output --partial "hello world"
}
