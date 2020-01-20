TESTS = Tests/*c

TESTS_FOR_TRANSLATE = \
Tests/20000523-1.c \
Tests/2003-10-12-GlobalVarInitializers.c \
Tests/arrays_decl_ref.c \
Tests/20020129-1.c \
Tests/2005-05-12-Int64ToFP.c \
Tests/corner_cases.c \
Tests/2002-05-02-CastTest.c \
Tests/2005-05-13-SDivTwo.c \
Tests/nqueen.c \
Tests/2002-12-13-MishaTest.c \
Tests/2005-11-29-LongSwitch.c \
Tests/pr19606.c \
Tests/2003-04-22-Switch.c \
Tests/rename.c \
Tests/2006-02-04-DivRem.c \
Tests/sumarray.c \
Tests/2003-05-22-LocalTypeTest.c \
Tests/20080424-1.c \
Tests/2003-07-08-BitOpsTest.c \
Tests/990127-1.c 


# Tests/2006-01-29-SimpleIndirectCall.c 
# Tests/2003-05-14-initialize-string.c 


tests: 
	./test_harness.py $(TESTS)

meta_tests:
	./meta.py $(TESTS)

mypy:
	mypy --ignore-missing-imports *py

t1:
	./translate.py Tests/nqueen.c

tranlate:
	./translate.py $(TESTS_FOR_TRANSLATE)


