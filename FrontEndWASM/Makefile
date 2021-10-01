

DIR=build

$(info $(shell mkdir -p $(DIR)))


TESTS_32_64 = memory.wasm fd_write.wasm print_i32_ln.wasm factorial.wasm fibonacci.wasm echo.wasm i32.wasm block.wasm
TESTS_64 = if.wasm global.wasm loop.wasm print_i64_ln.wasm call_indirect.wasm

TEST_32_EXES = $(TESTS_32_64:%.wasm=$(DIR)/%.32.exe)
TEST_64_EXES = $(TESTS_32_64:%.wasm=$(DIR)/%.64.exe)  $(TESTS_64:%.wasm=$(DIR)/%.64.exe) \
               $(DIR)/mal.64.exe $(DIR)/c-ray-f.64.exe $(DIR)/lists.64.exe \
               $(DIR)/spectral-norm.64.exe $(DIR)/nbody.64.exe \
               $(DIR)/fannkuch-redux.64.exe $(DIR)/matrix.64.exe \
               $(DIR)/amoeba_test.64.exe $(DIR)/nv_voronoi.64.exe \
               $(DIR)/brotli.64.exe

tests: $(DIR)/parse_test $(TEST_64_EXES) $(TEST_32_EXES)

$(DIR)/parse_test:
	@echo "[$@]"
	./parser.py TestData/test.wasm > $@.out

# not the "hello world 1 2 3" argument is only used by the echo.wasm benchmark
$(DIR)/%.32.exe: TestData/%.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 32 $< > $@.asm
	cat ../StdLib/syscall.a32.asm wasi.32.asm  $@.asm  | $(PYPY) ../CodeGenA32/codegen.py -mode binary  -add_startup_code - $@
	./$@ hello world 1 2 3 >$@.out
	diff $@.out $<.golden

# not the "hello world 1 2 3" argument is only used by the echo.wasm benchmark
$(DIR)/%.64.exe: TestData/%.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat ../StdLib/syscall.a64.asm wasi.64.asm  $@.asm  | $(PYPY) ../CodeGenA64/codegen.py -mode binary  -add_startup_code - $@
	./$@ hello world 1 2 3 >$@.out
	diff $@.out $<.golden

$(DIR)/c-ray-f.64.exe: TestData/c-ray-f.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat ../StdLib/syscall.a64.asm wasi.64.asm  $@.asm  | $(PYPY) ../CodeGenA64/codegen.py -mode binary  -add_startup_code - $@
	./$@  -s 1024x768 < ./TestData/c-ray-f.scene  >$@.out
	cmp -l $@.out ./TestData/c-ray-f.golden.ppm

$(DIR)/mal.64.exe: TestData/mal.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat ../StdLib/syscall.a64.asm wasi.64.asm  $@.asm  | $(PYPY) ../CodeGenA64/codegen.py -mode binary  -add_startup_code - $@
	./$@  ./TestData/test-fib.mal 16 >$@.out
	diff $@.out $<.golden

$(DIR)/lists.64.exe: TestData/lists.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat ../StdLib/syscall.a64.asm wasi.64.asm  $@.asm  | $(PYPY) ../CodeGenA64/codegen.py -mode binary  -add_startup_code - $@
	./$@  3000 >$@.out
	diff $@.out $<.golden

$(DIR)/spectral-norm.64.exe: TestData/spectral-norm.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat ../StdLib/syscall.a64.asm wasi.64.asm  $@.asm  | $(PYPY) ../CodeGenA64/codegen.py -mode binary  -add_startup_code - $@
	./$@  1000 >$@.out
	diff $@.out $<.golden

$(DIR)/nbody.64.exe: TestData/nbody.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat ../StdLib/syscall.a64.asm wasi.64.asm  $@.asm  | $(PYPY) ../CodeGenA64/codegen.py -mode binary  -add_startup_code - $@
	./$@  500000 >$@.out
	diff $@.out $<.golden

$(DIR)/fannkuch-redux.64.exe: TestData/fannkuch-redux.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat ../StdLib/syscall.a64.asm wasi.64.asm  $@.asm  | $(PYPY) ../CodeGenA64/codegen.py -mode binary  -add_startup_code - $@
	./$@ 10 >$@.out
	diff $@.out $<.golden

$(DIR)/matrix.64.exe: TestData/matrix.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat ../StdLib/syscall.a64.asm wasi.64.asm  $@.asm  | $(PYPY) ../CodeGenA64/codegen.py -mode binary  -add_startup_code - $@
	./$@ 3000 >$@.out
	diff $@.out $<.golden

$(DIR)/amoeba_test.64.exe: TestData/amoeba_test.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat ../StdLib/syscall.a64.asm wasi.64.asm  $@.asm  | $(PYPY) ../CodeGenA64/codegen.py -mode binary  -add_startup_code - $@
	./$@ >$@.out
	diff $@.out $<.golden

$(DIR)/nv_voronoi.64.exe: TestData/nv_voronoi.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat ../StdLib/syscall.a64.asm wasi.64.asm  $@.asm  | $(PYPY) ../CodeGenA64/codegen.py -mode binary  -add_startup_code - $@
	./$@ >$@.out
	diff $@.out $<.golden

$(DIR)/brotli.64.exe: TestData/brotli.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat ../StdLib/syscall.a64.asm wasi.64.asm  $@.asm  | $(PYPY) ../CodeGenA64/codegen.py -mode binary  -add_startup_code - $@
	./$@ < TestData/brotli.alice.txt >$@.out
	diff $@.out $<.golden

clean:
	rm -f $(DIR)/*
