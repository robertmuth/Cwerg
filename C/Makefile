DIR=build

$(info $(shell mkdir -p $(DIR)))

cwerg.h: ../Base/opcode_tab.py
	@echo "[$@]"
	$(PYPY) ../Base/opcode_tab.py gen_c < cwerg.h > $(DIR)/$@.tmp
	@mv $(DIR)/$@.tmp $@