export PYTHONPATH =  $(shell pwd)/..


#@ opcodes.md - regenerate the opcode description
#@
opcodes.md: ../Base/opcode_tab.py
	../Base/opcode_tab.py documentation < $@ > $@.tmp
	@mv $@.tmp $@
