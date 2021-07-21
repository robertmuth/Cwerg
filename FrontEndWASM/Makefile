

DIR=build

$(info $(shell mkdir -p $(DIR)))

tests: $(DIR)/parse_test $(DIR)/wasi_a32_test $(DIR)/wasi_a64_test

$(DIR)/parse_test:
	./parser.py TestData/fac.wasm > $@.out
	./parser.py TestData/hello.wasm >> $@.out
	./parser.py TestData/wasmtime.hello.wasm >> $@.out

$(DIR)/wasi_a32_test:
	./wasm2cwerg.py 32 TestData/wasmtime.hello.wasm > $@.asm
	cat ../StdLib/syscall.a32.asm wasi.32.asm  $@.asm  | ../CodeGenA32/codegen.py -mode binary  - $@.exe
	./$@.exe >$@.out
	diff $@.out TestData/wasmtime.hello.wasm.golden

$(DIR)/wasi_a64_test:
	./wasm2cwerg.py 64 TestData/wasmtime.hello.wasm > $@.asm
	cat ../StdLib/syscall.a64.asm wasi.64.asm  $@.asm  | ../CodeGenA64/codegen.py -mode binary  - $@.exe
	./$@.exe >$@.out
	diff $@.out TestData/wasmtime.hello.wasm.golden

clean:
	rm -f $(DIR)/*
