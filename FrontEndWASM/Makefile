

DIR=build

$(info $(shell mkdir -p $(DIR)))


TESTS = fd_write.wasm print_i32_ln.wasm factorial.wasm fibonacci.wasm echo.wasm

TEST_32_EXES =  $(TESTS:%.wasm=$(DIR)/%.32.exe)
TEST_64_EXES =  $(TESTS:%.wasm=$(DIR)/%.64.exe)

tests: $(DIR)/parse_test $(TEST_32_EXES) $(TEST_64_EXES)

$(DIR)/parse_test:
	@echo "[$@]"
	./parser.py TestData/hello.wasm > $@.out

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


clean:
	rm -f $(DIR)/*