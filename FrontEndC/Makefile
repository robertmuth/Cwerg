TESTS = TestData/*c

TESTS_FOR_TRANSLATE = \
TestData/20000523-1.c \
TestData/2003-10-12-GlobalVarInitializers.c \
TestData/arrays_decl_ref.c \
TestData/20020129-1.c \
TestData/2005-05-12-Int64ToFP.c \
TestData/corner_cases.c \
TestData/2002-05-02-CastTest.c \
TestData/2005-05-13-SDivTwo.c \
TestData/nqueen.c \
TestData/2002-12-13-MishaTest.c \
TestData/2005-11-29-LongSwitch.c \
TestData/pr19606.c \
TestData/2003-04-22-Switch.c \
TestData/rename.c \
TestData/2006-02-04-DivRem.c \
TestData/sumarray.c \
TestData/2003-05-22-LocalTypeTest.c \
TestData/20080424-1.c \
TestData/2003-07-08-BitOpsTest.c \
TestData/990127-1.c 


# TestData/2006-01-29-SimpleIndirectCall.c 
# TestData/2003-05-14-initialize-string.c 


tests: 
	./test_harness.py $(TESTS)

meta_tests:
	./meta.py $(TESTS)

mypy:
	mypy --ignore-missing-imports *py

t1:
	./translate.py TestData/nqueen.c

tranlate:
	./translate.py $(TESTS_FOR_TRANSLATE)

nano:
	./canonicalize.py ../nanojpeg.c > ../nanojpeg.canonicaliced.c
	gcc -Wno-builtin-declaration-mismatch ../nanojpeg.canonicaliced.c -o ../nanojpeg.gcc.exe
	../nanojpeg.gcc.exe ../ash_tree.jpg ../nanojpeg.gcc.ppm
	cmp  ../nanojpeg.gcc.ppm ../ash_tree.ppm
	@echo
	clang -Wno-builtin-requires-header ../nanojpeg.canonicaliced.c -o ../nanojpeg.clang.exe
	../nanojpeg.clang.exe ../ash_tree.jpg ../nanojpeg.clang.ppm
	cmp  ../nanojpeg.clang.ppm ../ash_tree.ppm

clean:
	rm -f *.exe *_gen.c
