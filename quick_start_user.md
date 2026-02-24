# Quickstart For Using Cwerg


Currently, Cwerg works on recent Linux systems only.
It has been primarily tested on Ubuntu 24.04.

Be prepared for a bumpy ride - the language and its tools are very much work-in-progress.

Bug reports on github are appreciated.

## Installation


* Install the repository from github by running:
  `git clone https://github.com/robertmuth/Cwerg`

  Note: you may need to install the `git` package first

* The compiler driver will then be available at `Cwerg/cwereg.py`
  Run this to build hello work:

  `Cwerg/cwerg.py -be py -fe py Cwerg/FE/TestData/hello_world_test.cw hello.exe`

  Followed by

  `./hello.exe`

  Note: you may need to install the `python3` package first

* The compilation in the previous step was kind of slow because it uses
  the interpreted Python version of the front- and backend. To use the faster native C++ versions
  we must build them first by running:

  `cd Cwerg/ ; make build_compiler`

  Note: you may need to install the `make cmake g++ libunwind-dev` packages first

* Now you can run the much fast native compiler like so:

  `Cwerg/cwerg.py Cwerg/FE/TestData/hello_world_test.cw hello.exe`


## Next Steps

* Read the [Tutorial](FE/Docs/tutorial.md)
* Look the example and fledgling standard library in `FE/TestData`, `FE/LangTest`, `FE/Lib`
* if you want start hacking on the compiler itself have a look at [quick_start_developer.md]