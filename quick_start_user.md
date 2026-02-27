# Quickstart For Using Cwerg

Currently, Cwerg works on recent Linux systems only.
It has been primarily tested on Ubuntu 24.04.

Be prepared for a bumpy ride - the language and its tools are very much work-in-progress.

Bug reports on github are appreciated.

## Installation

* Install the repository from github by running:

  `git clone https://github.com/robertmuth/Cwerg`

  Note: You may need to install the `git` package first.

## Development and Runtime Environment

You can either build and run the compiler directly on your host system or on the
provided docker container.
* **Host system**: You will have to install the required packages yourself. To
  run the compiler driver and the Python version of the compiler, you need to
  install the `python3` package version >= 3.10. To build the native C++ version
  of the compiler you need to install the following packages:
  `make cmake g++ libunwind-dev`.
* **Docker container**: You need to have the `docker` package installed on your
  host. Then build the docker container that encapsulates a ready configured
  development environment:

  `docker build -t cwerg-dev-env Cwerg/docker`

  Start a shell in the container:

  `docker run -it --rm -v Cwerg:/Cwerg cwerg-dev-env`

  Then run the command lines indicated below inside this shell.

  Note: Your host's Cwerg repository is mapped to path `/Cwerg` in the
  container.

## Running

* The compiler driver is available at `Cwerg/cwerg.py`.

  Run this to build hello world:

  `Cwerg/cwerg.py -be py -fe py Cwerg/FE/TestData/hello_world_test.cw hello.exe`

  Followed by:

  `./hello.exe`

* The compilation in the previous step was kind of slow because it uses the
  interpreted Python version of the front- and backend. To use the faster native
  C++ versions, we must build them first by running:

  `cd Cwerg/ ; make build_compiler`

* Now you can run the much faster native compiler like so:

  `./cwerg.py FE/TestData/hello_world_test.cw hello.exe`

## Next Steps

* Read the [Tutorial](FE/Docs/tutorial.md)
* For inspiration, look at the examples and the fledgling standard library in `FE/TestData`, `FE/LangTest`, and `FE/Lib`
* If you want start hacking on the compiler itself have a look at [quick_start_developer.md](quick_start_developer.md)
