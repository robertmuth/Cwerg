DIR=build

$(info $(shell mkdir -p $(DIR)))

############################################################
# CodeGen
############################################################

opcode_gen.h: opcode_tab.py
	@echo "[$@]"
	$(PYPY) ./opcode_tab.py gen_h < opcode_gen.h > $(DIR)/$@.tmp
	@mv $(DIR)/$@.tmp $@

opcode_gen.cc: opcode_tab.py opcode_gen.h
	@echo "[$@]"
	$(PYPY) ./opcode_tab.py gen_cc  < opcode_gen.cc > $(DIR)/$@.tmp
	@mv $(DIR)/$@.tmp $@

GENERATED = opcode_gen.h opcode_gen.cc
