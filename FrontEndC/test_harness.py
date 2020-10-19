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
    p = subprocess.run("./canonicalize.py %s > %s" %
                       (fn, fn_canoicalized), shell=True)
    return p.stdout


def CheckDelta(expected, actual):
    if actual != expected:
        print("DELTA")
        print(actual)
        print(expected)
        return True
    return False


CANONICALIZED_C = "./canonicalized_gen.c"
ORIG_EXE = "./orig.exe"
CANONICALIZED_EXE = "./canonicalized.exe"


def RunTest(fn: str):
    print("=" * 50)
    print(fn)
    print("=" * 50)

    bad = False
    bad |= RunClang(fn, ORIG_EXE)
    stdout = RunAndCaptureStdout(f'{ORIG_EXE}; echo "exit $?"')
    reference = fn[:-2] + ".reference_output"
    if os.path.exists(reference):
        CheckDelta(open(reference, "rb").read(), stdout)
    Canonicalize(fn, CANONICALIZED_C)
    bad |= RunClang(CANONICALIZED_C, CANONICALIZED_EXE)
    stdout2 = RunAndCaptureStdout(f'{CANONICALIZED_EXE}; echo "exit $?"')
    bad |= CheckDelta(stdout, stdout2)
    return bad == True


def main(argv):
    bad = 0
    for fn in argv:
        bad += RunTest(fn)
    if bad == 0:
        print("OK")
    else:
        print(f"ERRORS: {bad}")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
