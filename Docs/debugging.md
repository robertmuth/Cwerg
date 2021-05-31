## Debugging Hints

* most debugging should happen in the Python implementation which also has
  most of the (unit) tests.
  
* for print(f) debugging use the following idioms to print Fun/Bbl/Ins

    ```
    print("\n".join(serialize.FunRenderToAsm(fun)))
    print ("\n".join(serialize.BblRenderToAsm(bbl)))
    print(serialize.InsRenderToAsm(ins))
    ```
  
* the Tools/  directory contains several debugging aids
  
  * reg_alloc_explorer.py - for debugging the (A32) register allocator
  * inspector.py - for browsing the IR before and after various transformations


### Built-in Web Datastructure browser 

Several of the c++ binaries have a built-in webserver (e.g. Base/optimize_tool and 
CodeGenA32/codegen_tool).
The webserver needs to be explicitly activated via a commandline flag that specifies the port 
the server is listening on, e.g. `-webserver_port=8080`.

The webserver let's you browse the current IR. You can add software breakpoints by defining global 
objects like
```
BreakPoint bp_after_load("after_load");
```
and then call 
```
bp_after_load.Break();
```
at the point where you want to inspect the IR. 
The breakpoint can be resumed via the Web interface.

### GDB

Read up on tui mode

https://sourceware.org/gdb/current/onlinedocs/gdb/TUI.html

Sample session
```
break main
run
c-x 2    [two window view]
layout asm
layout regs
c-x s    [toggle single key mode]
i        [stepi]
i
i
c-x s
```



