#!/bin/bash

set -o nounset
set -o errexit

# --docstring-as-code:  https://github.com/AlDanial/cloc/issues/375 
readonly CLOC_FLAGS="-quiet --hide-rate --docstring-as-code"




RunCloc() {
 echo '```'
 cloc ${CLOC_FLAGS} "$@" | tail -n +3
 echo '```'
}


ComputeStats() {
    echo "### Regular Code (Python)"
    echo
    RunCloc  --by-file '--match-f=[.](py)$$' '--not-match-f=(cwast|_test|_tab|_gen.*)[.](py)$$' --match-d="$2"  $1


    echo
    echo "### Table Code (Python)"
    echo
    RunCloc --by-file  '--match-f=(cwast|_tab).*[.](py)$$'  --match-d="$2"  $1 

    echo "### Regular Code (C++)"
    echo
    RunCloc --by-file '--match-f=[.](cc|h)$$' '--not-match-f=(_test|_tab|_gen.*)[.](|h|cc)$$' --match-d="$2"  $1
    
    echo
    echo "### Generated Files (C++)"
    echo
    RunCloc --by-file  '--match-f=_gen.*[.](cc|h)$$'  --match-d="$2"  $1   
    
    
}

backend() {
	   
    echo "## ISA Neutral Code"
    ComputeStats BE "Base|Elf"

    echo "## A32 Code"
    ComputeStats BE "CpuA32|CodeGenA32"

    echo "## A64 Code"
    ComputeStats BE "CpuA64|CodeGenA64"

    echo "## X64 Code"
    ComputeStats BE "CpuX64|CodeGenX64"
}


frontend() {
	   
    ComputeStats FE ".*"
}

if [ $# = 0 ]; then
   echo "ERROR: No command specified." >&2
   exit 1
 fi


if [ "$(type -t $1)" != "function" ]; then
   echo "ERROR: unknown command '$1'." >&2
   exit 1
 fi
  
"$@"
