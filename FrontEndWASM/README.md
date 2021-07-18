## WASM Frontend 

This is still in a very early stage.

There will only be a Python implementation.

The [parser](parser.py) and the [instructions table](opcode_tab.py) do not have any other dependencies and might be useful by themselves.

### References 

https://mvolkmann.github.io/blog/webassembly/

https://github.com/mbasso/awesome-wasm

https://github.com/WebAssembly/spec

https://github.com/bytecodealliance/wasmtime

* https://github.com/WebAssembly/WASI/blob/main/phases/snapshot/docs.md#modules

https://github.com/WebAssembly/wabt  

* ubuntu https://packages.ubuntu.com/search?keywords=wabt
* tests https://github.com/WebAssembly/wabt/tree/main/test/spec
* wasm2wat wasm -> wast
* wat2wasm wast -> wasm

https://github.com/WebAssembly/binaryen

* ubuntu package: https://packages.ubuntu.com/search?keywords=binaryen
* wasm-dis wasm -> wast
* wasm-as wast -> wasm
