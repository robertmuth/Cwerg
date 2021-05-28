.SUFFIXES:  # no built-in rules
DIR=build

$(info $(shell mkdir -p $(DIR)))

hello-x64:
	gcc -static -Wl,-z,norelro -O2 hello.c -o hello-x64 

hello_barebones-x64:
	as hello_barebones.s -o $(DIR)/hello_barebones.o
	ld hello_barebones.o -o $(DIR)/hello_barebones-x64


clean:
	rm -f $(DIR)/*
