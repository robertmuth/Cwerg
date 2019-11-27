#!/usr/bin/python3

import subprocess
import sys

import os


def RunGcc(fn: str, exe: str):
    print("RunGcc [%s] -> [%s]" % (fn, exe))
    return subprocess.call(["gcc", fn, "-o", exe])


def RunAndCaptureStdout(command):
    print("Run %s" % command)
    p = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
    return p.stdout


def CheckReference(reference, actual):
    print("CheckReference [%s]" % reference)
    expected = open(reference, "rb").read()

    if actual != expected:
        print("DELTA")
        print(actual)
        print(expected)


def RunTest(fn: str):
    print("=" * 50)
    print(fn)
    print("=" * 50)

    RunGcc(fn, "./a.out")
    stdout = RunAndCaptureStdout('./a.out; echo "exit $?"')
    reference = fn[:-2] + ".reference_output"
    if os.path.exists(reference):
        CheckReference(reference, stdout)


def main(argv):
    for fn in argv:
        RunTest(fn)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
