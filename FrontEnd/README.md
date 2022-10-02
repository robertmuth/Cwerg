## Experimental Frontend For The Cwerg Language

This is completely unfinished and experimental

### Expected Highlights

* Source code will be stored as serialized S-Exprression with tooling to
  convert back and forth to a yet to be defined concrete syntax.
  The tooling will also do most of the semantic checking.
* Comments wil be explicit in the AST and cannot occur in arbitrary    places
* There wont be classes only records (= structs)
* Templated Modules will provide namespaces and generics (similar to later versions of Oberon)
* nit/fini function order defined by Module dependencies
* There will be support for Sum Types to support Result and Optional
  types.
* Arrays and Slices types will be supported at the language level
* Slices will reduce the need for pointer arithmetic
* Run-time checked indexing is available for Arrays and Slices
* Maps will NOT be supported at the language level
* Utf-8 will NOT be supported at the language level
* All types can be wrapped (= distinct types in Nim/Odin)
* Variables are non-mutable by default
* Pointees are non-mutable by default
* Identifier visibility is non-public by default
* Complexity budget: about 10kLOC
  

### Pointers, Arrays, Slices, Strings

Pointers, Arrays, Slices are not mutable by default but come in mutable
flavors. Casting preserves mutabiity. Mutable entity can be passed
as non-mutable function arguments.

Pointers

* can point to anything including Scalars. Arrays and Slices
* syntactic indexing is not available but 
* pointer arithmetic is allowed and unchecked:
 `^(ptr + 8)`  is equivalent to C's `ptr[8]` or `*(ptr + 8)` 
* pointers can be cast to arrays

Arrays

* have a fixed length known at compile-time
* indexing (`a_array[i]`) is available AND run-time checked
* taking the address of an array does not decay into an ordinary pointer
* ordinary pointers can be obtained via `ptr = &a_array[0]`
* arrays can be cast to arrays of smaller length
* arrays can be converted to slices by applying the slicing operator
  `a_slice = a_array[:]`
* arrays are implicitly converted to slices if passed to a slice    function argument

Slices
* are fat pointer - starting address + length 
* are intended to be the main work horse
* indexing (`a_slice[i]`) is available AND run-time checked
* slicing `b_slice = a_slice[start:length]` can be used for checked "arithmetic"


Strings 
* are just Arrays of unsigned bytes
* they are not null terminated
