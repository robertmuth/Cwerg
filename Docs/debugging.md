## Debugging Hints

* most debugging should happen in the Python implementation which also has
  most of the (unit) tests.
  
* for print(f) debugging use the following idioms to print Fun/Bbl/Ins
    ```
    print("\n".join(serialize.FunRenderToAsm(fun)))
    print ("\n".join(serialize.BblRenderToAsm(bbl)))
    print(serialize.InsRenderToAsm(ins))
    ```
  
* the Tools/  directory contains debugging aids

* C++ built-in web browser

