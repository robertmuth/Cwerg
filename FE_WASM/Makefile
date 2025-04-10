

DIR=build

# setting these is not strictly necessary because Linux will auto-detect the proper qemu to use
QEMUX64 =
QEMUA64 = qemu-aarch64-static
QEMUA32 = qemu-arm-static

$(info $(shell mkdir -p $(DIR)))

tests: $(DIR)/parse_test tests_x64 tests_a32 tests_a64
	@echo "[OK FrontEndWASM]"

TESTS_32_64 = memory.wasm fd_write.wasm print_i32_ln.wasm factorial.wasm fibonacci.wasm echo.wasm i32.wasm block.wasm
TESTS_64 = if.wasm global.wasm loop.wasm print_i64_ln.wasm call_indirect.wasm

tests_a32:  $(TESTS_32_64:%.wasm=$(DIR)/%.a32.exe)
tests_a64: $(TESTS_32_64:%.wasm=$(DIR)/%.a64.exe)  $(TESTS_64:%.wasm=$(DIR)/%.a64.exe) \
               $(DIR)/mal.a64.exe $(DIR)/c-ray-f.a64.exe $(DIR)/lists.a64.exe \
               $(DIR)/spectral-norm.a64.exe $(DIR)/nbody.a64.exe \
               $(DIR)/fannkuch-redux.a64.exe $(DIR)/matrix.a64.exe \
               $(DIR)/amoeba_test.a64.exe $(DIR)/nv_voronoi.a64.exe \
               $(DIR)/brotli.a64.exe $(DIR)/objzero_test.a64.exe \
               $(DIR)/nanosvg_test.a64.exe $(DIR)/binary-trees.a64.exe

tests_x64: $(TESTS_64:%.wasm=$(DIR)/%.x64.exe) $(TESTS_32_64:%.wasm=$(DIR)/%.x64.exe) \
                $(DIR)/lists.x64.exe \
                $(DIR)/spectral-norm.x64.exe  $(DIR)/nbody.x64.exe \
                $(DIR)/fannkuch-redux.x64.exe \
                $(DIR)/matrix.x64.exe \
                $(DIR)/nv_voronoi.x64.exe \
                $(DIR)/binary-trees.x64.exe

# need open
# mal.a64.exe
# c-ray-f.a64.exe
# brotli.a64.exe
# objzero_test.a64.exe
# nanosvg_test.a64.exe

# amoeba_test.x64.exe   has problem with signedness of zwero

tests: $(DIR)/parse_test tests_x64 tests_a32 tests_a64


STD_LIB_X64 = ../BE/StdLib/startup.x64.asm ../BE/StdLib/syscall.x64.asm
STD_LIB_A64 = ../BE/StdLib/startup.a64.asm ../BE/StdLib/syscall.a64.asm
STD_LIB_A32 = ../BE/StdLib/startup.a32.asm ../BE/StdLib/syscall.a32.asm

CODEGEN_A32 = ../BE/CodeGenA32/codegen.py
CODEGEN_A64 = ../BE/CodeGenA64/codegen.py
CODEGEN_X64 = ../BE/CodeGenX64/codegen.py

$(DIR)/parse_test:
	@echo "[$@]"
	./parser.py TestData/test.wasm > $@.out

# not the "hello world 1 2 3" argument is only used by the echo.wasm benchmark
$(DIR)/%.a32.exe: TestData/%.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 32 $< > $@.asm
	cat $(STD_LIB_A32) wasi.32.asm $@.asm  | $(PYPY) $(CODEGEN_A32) -mode binary - $@
	$(QEMUA32) $@ hello world 1 2 3 >$@.out
	diff $@.out $<.golden

# not the "hello world 1 2 3" argument is only used by the echo.wasm benchmark
$(DIR)/%.a64.exe: TestData/%.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat $(STD_LIB_A64) wasi.64.asm  $@.asm  | $(PYPY) $(CODEGEN_A64) -mode binary - $@
	$(QEMUA64) $@ hello world 1 2 3 >$@.out
	diff $@.out $<.golden

# not the "hello world 1 2 3" argument is only used by the echo.wasm benchmark
$(DIR)/%.x64.exe: TestData/%.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat $(STD_LIB_X64) wasi.lite.64.asm  $@.asm  | $(PYPY) $(CODEGEN_X64) -mode binary - $@
	$(QEMUX64) $@ hello world 1 2 3 >$@.out
	diff $@.out $<.golden

$(DIR)/c-ray-f.a64.exe: TestData/c-ray-f.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat $(STD_LIB_A64) wasi.64.asm  $@.asm  | $(PYPY) $(CODEGEN_A64) -mode binary - $@
	$(QEMUA64) $@  -s 1024x768 < ./TestData/c-ray-f.scene  >$@.out
	cmp -l $@.out ./TestData/c-ray-f.golden.ppm

$(DIR)/mal.a64.exe: TestData/mal.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat $(STD_LIB_A64) wasi.64.asm  $@.asm  | $(PYPY) $(CODEGEN_A64) -mode binary - $@
	$(QEMUA64) $@  ./TestData/test-fib.mal 16 >$@.out
	diff $@.out $<.golden

$(DIR)/lists.a64.exe: TestData/lists.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat $(STD_LIB_A64) wasi.64.asm  $@.asm  | $(PYPY) $(CODEGEN_A64) -mode binary - $@
	$(QEMUA64) $@  3000 >$@.out
	diff $@.out $<.golden

$(DIR)/lists.x64.exe: TestData/lists.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat $(STD_LIB_X64) wasi.lite.64.asm  $@.asm  | $(PYPY) $(CODEGEN_X64) -mode binary - $@
	$(QEMUX64) $@  3000 >$@.out
	diff $@.out $<.golden

$(DIR)/spectral-norm.a64.exe: TestData/spectral-norm.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat $(STD_LIB_A64) wasi.64.asm  $@.asm  | $(PYPY) $(CODEGEN_A64) -mode binary - $@
	$(QEMUA64) $@  1000 >$@.out
	diff $@.out $<.golden

$(DIR)/spectral-norm.x64.exe: TestData/spectral-norm.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat $(STD_LIB_X64) wasi.lite.64.asm  $@.asm  | $(PYPY) $(CODEGEN_X64) -mode binary - $@
	$(QEMUX64) $@  1000 >$@.out
	diff $@.out $<.golden

$(DIR)/nbody.a64.exe: TestData/nbody.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat $(STD_LIB_A64) wasi.64.asm  $@.asm  | $(PYPY) $(CODEGEN_A64) -mode binary - $@
	$(QEMUA64) $@  500000 >$@.out
	diff $@.out $<.golden

$(DIR)/nbody.x64.exe: TestData/nbody.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat $(STD_LIB_X64) wasi.lite.64.asm  $@.asm  | $(PYPY) $(CODEGEN_X64) -mode binary - $@
	$(QEMUX64) $@  500000 >$@.out
	diff $@.out $<.golden

$(DIR)/fannkuch-redux.a64.exe: TestData/fannkuch-redux.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat $(STD_LIB_A64) wasi.64.asm  $@.asm  | $(PYPY) $(CODEGEN_A64) -mode binary - $@
	$(QEMUA64) $@ 10 >$@.out
	diff $@.out $<.golden

$(DIR)/fannkuch-redux.x64.exe: TestData/fannkuch-redux.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat $(STD_LIB_X64) wasi.lite.64.asm  $@.asm  | $(PYPY) $(CODEGEN_X64) -mode binary - $@
	$(QEMUX64) $@ 10 >$@.out
	diff $@.out $<.golden

$(DIR)/matrix.a64.exe: TestData/matrix.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat $(STD_LIB_A64) wasi.64.asm  $@.asm  | $(PYPY) $(CODEGEN_A64) -mode binary - $@
	$(QEMUA64) $@ 3000 >$@.out
	diff $@.out $<.golden

$(DIR)/matrix.x64.exe: TestData/matrix.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat $(STD_LIB_X64) wasi.lite.64.asm  $@.asm  | $(PYPY) $(CODEGEN_X64) -mode binary - $@
	$(QEMUX64) $@ 3000 >$@.out
	diff $@.out $<.golden

$(DIR)/amoeba_test.a64.exe: TestData/amoeba_test.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat $(STD_LIB_A64) wasi.64.asm  $@.asm  | $(PYPY) $(CODEGEN_A64) -mode binary - $@
	$(QEMUA64) $@ >$@.out
	diff $@.out $<.golden

$(DIR)/amoeba_test.x64.exe: TestData/amoeba_test.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat $(STD_LIB_X64) wasi.lite.64.asm  $@.asm  | $(PYPY) $(CODEGEN_X64) -mode binary - $@
	$(QEMUX64) $@ >$@.out
	diff $@.out $<.golden

$(DIR)/nv_voronoi.a64.exe: TestData/nv_voronoi.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat $(STD_LIB_A64) wasi.64.asm  $@.asm  | $(PYPY) $(CODEGEN_A64) -mode binary - $@
	$(QEMUA64) $@ >$@.out
	diff $@.out $<.golden

$(DIR)/nv_voronoi.x64.exe: TestData/nv_voronoi.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat $(STD_LIB_X64) wasi.lite.64.asm  $@.asm  | $(PYPY) $(CODEGEN_X64) -mode binary - $@
	$(QEMUX64) $@ >$@.out
	diff $@.out $<.golden

$(DIR)/brotli.a64.exe: TestData/brotli.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat $(STD_LIB_A64) wasi.64.asm  $@.asm  | $(PYPY) $(CODEGEN_A64) -mode binary - $@
	$(QEMUA64) $@ < TestData/brotli.alice.txt >$@.out
	diff $@.out $<.golden

$(DIR)/objzero_test.a64.exe: TestData/objzero_test.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat $(STD_LIB_A64) wasi.64.asm  $@.asm  | $(PYPY) $(CODEGEN_A64) -mode binary - $@
	$(QEMUA64) $@ ./TestData/LeePerrySmith.obj >$@.out
	diff $@.out $<.golden

$(DIR)/nanosvg_test.a64.exe: TestData/nanosvg_test.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat $(STD_LIB_A64) wasi.64.asm  $@.asm  | $(PYPY) $(CODEGEN_A64) -mode binary - $@
	$(QEMUA64) $@ ./TestData/nanosvg_23.svg ./$@.out >$@.out.log
	diff $@.out $<.golden

$(DIR)/binary-trees.a64.exe: TestData/binary-trees.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat $(STD_LIB_A64) wasi.64.asm  $@.asm  | $(PYPY) $(CODEGEN_A64) -mode binary - $@
	$(QEMUA64) $@ 15 >$@.out
	diff $@.out $<.golden

$(DIR)/binary-trees.x64.exe: TestData/binary-trees.wasm
	@echo "[$@]"
	$(PYPY) ./wasm2cwerg.py 64 $< > $@.asm
	cat $(STD_LIB_X64) wasi.lite.64.asm  $@.asm  | $(PYPY) $(CODEGEN_X64) -mode binary - $@
	$(QEMUX64) $@ 15 >$@.out
	diff $@.out $<.golden

clean:
	rm -f $(DIR)/*
