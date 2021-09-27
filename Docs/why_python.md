## Why Python

The primary implementation language of Cwerg is Python3.
This is a rather odd choice and hence deserve some explanation.

The basic premise is this:
```
    Time-Impl(Python) + Time-Port(Python, C++) <= Time-Impl(C++) 
 ```

Meaning: the time to implement Cwerg in Python and then port it to C++ is
smaller than directly implementing it in C++.
(Here C++ can be substituted with most other compiled languages.)

This approach has worked for the author on previous smaller projects.
The advantage is greatest during the initial exploration phase. It 
remains to be seen if this still holds once the project matures.
(There is a least one other project that has gone a similar route:
http://www.oilshell.org/blog/2016/10/10.html)

Implementing the everything twice has additional benefits:

* it identifies non-deterministic or underspecified parts of the code as
  we require both implementations to produce identical output.
* it finds additional bugs 
* it paves the way for the implementation in other languages 

## Benefits of Python (compared to C++)

* Python has become the Lingua Franca of the programming world.
  It is easy to learn and already understood by many programmers. 

* It has a huge amount of built-in packages

* Due to Python's interpreted nature turn-around times are extremely fast,
  especially compared to a traditional compile and link cycle.
 
* Programmer productivity is also boosted by built-in support 
  for strings, lists and hash-tables, as well as a decent unit-testing 
  framework and introspection.
 
* The code is very compact (often only half the size of equivalent C++ code)
  without sacrificing readability. Thanks to the (relatively) new type
  annotations mechanism, Python programs also scale much better than they
  used to.

## Why not plain C?

The initial plan was to provide a C port but C in 2020 felt like an exercise in masochism
and so the C port morphed into a C++ port.
The hope is to offer plain C bindings on top of it. To facilitate this the C++ stays clear
of exception and virtual functions and only uses a fairly limited part of STL.
All the basic data structure use custom containers. 

## Ports to other Programming Languages

We do not expect the Python code be run in production compilers, so
we encourage re-implementing Cwerg in other languages and will 
maintain a C++ implementation of all relevant components
to make sure that porting will remain reasonably straight forward.
To facilitate porting there is an emphasis for the Python code to be 
readable, well commented and deterministic.

Also, we try to make as much code as possible table driven.
The tables are stored in files named XXX_tab.py and those files
also contain the code to generate the tables for other language ports
like C++.

Implementations in other languages are expected to produce
identical output to the Python reference implementation.

This way Unit tests can stay primarily in Python
until we run into performance problems.



