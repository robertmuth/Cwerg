#!/bin/bash
set -o nounset
set -o errexit
echo "PYPY: ${PYPY}"

for test in "$@" ; do
    echo 
    echo "${test}"
    
    echo "STRAIGHT CODE GEN"
    echo "generate code"
    ${PYPY} CodeGenC/codegen.py ${test}  > ${test}.c
    echo "compile code"
    clang -Wall -Wno-unused-variable  -Wno-unused-label ${test}.c -lm -o ${test}.exe
    echo "run code"
    ${test}.exe > ${test}.actual 
    diff ${test}.actual ${test}.golden

    echo "CODE GEN AFTER OPT"
    echo "optimize code"
    ${PYPY} Base/optimize.py < ${test}  > ${test}.opt
    echo "generate code"
    ${PYPY} CodeGenC/codegen.py ${test}.opt  > ${test}.c
    echo "compile code"
    clang -Wall -Wno-unused-variable  -Wno-unused-label ${test}.c -lm -o ${test}.exe
    echo "run code"
    ${test}.exe > ${test}.actual
    diff ${test}.actual ${test}.golden

done
echo "OK"
	 
