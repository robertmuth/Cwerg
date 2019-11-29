#!/usr/bin/python3

import os
import subprocess
import sys


def RunGcc(fn: str, exe: str):
    print("RunGcc [%s] -> [%s]" % (fn, exe))
    return subprocess.call(["gcc", "-Wno-builtin-declaration-mismatch", fn, "-o", exe])


def RunClang(fn: str, exe: str):
    print("RunClang [%s] -> [%s]" % (fn, exe))
    return subprocess.call(["clang", "-Wno-incompatible-library-redeclaration", fn, "-o", exe])


def RunAndCaptureStdout(command):
    print("Run %s" % command)
    p = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
    return p.stdout


def Canonicalize(fn, fn_canoicalized):
    print("Canonicalize [%s] -> [%s]" % (fn, fn_canoicalized))
    p = subprocess.run("./canonicalize.py %s > %s" % (fn, fn_canoicalized), shell=True)
    return p.stdout


def CheckDelta(expected, actual):
    if actual != expected:
        print("DELTA")
        print(actual)
        print(expected)


CANONICALIZED_C = "./canonicalized.c"


def RunTest(fn: str):
    print("=" * 50)
    print(fn)
    print("=" * 50)

    RunClang(fn, "./a.out")
    stdout = RunAndCaptureStdout('./a.out; echo "exit $?"')
    reference = fn[:-2] + ".reference_output"
    if os.path.exists(reference):
        CheckDelta(open(reference, "rb").read(), stdout)
    Canonicalize(fn, CANONICALIZED_C)
    RunClang(CANONICALIZED_C, "./a.out")
    stdout2 = RunAndCaptureStdout('./a.out; echo "exit $?"')
    CheckDelta(stdout, stdout2)


def main(argv):
    for fn in argv:
        RunTest(fn)
    print("OK")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
