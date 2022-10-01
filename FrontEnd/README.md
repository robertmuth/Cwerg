## Experimental Frontend For The Cwerg Language

This is completely unfinished and experimental

Expected Highlights

* Source code will be stored as serialized S-Exprression with tooling to
  convert back and forth to a yet to be defined concrete syntax.
  The tooling will also do most of the semantic checking.
* Comments wil be explicit in the AST and cannot occur in arbitrary    places
* There wont be classes only records (= structs)
* Templated Modules will provide namespaces and generics (similar to later versions of Oberon)
* nit/fini function order defined by Module dependencies
* There will be support for Sum Types to support Result and Optional
  types.
* Array/vector types will be supported at the language level but NOT maps
* Slices eliminate the need for pointer arithmetic
* Types can be wrapped (= distinct types in Nim/Odin)
* Variables are non-mutable by default
* Pointees are non-mutable by default
* Identifier visibility is non-public by default
* Complexity budget: about 10kLOC
