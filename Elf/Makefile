.SUFFIXES:  # no built-in rules
DIR=build

$(info $(shell mkdir -p $(DIR)))

QEMU_A64 = qemu-aarch64-static
QEMU_A32 = qemu-arm-static
QEMU_X64 =

tests: tests_py tests_c
	@echo "[OK Elf]"

tests_py: $(DIR)/clone_x64_test $(DIR)/clone_a32_test $(DIR)/gen_x64_test $(DIR)/gen_a32_test $(DIR)/gen_a64_test

tests_c: $(DIR)/clone_a32_test_c $(DIR)/clone_x64_test_c $(DIR)/gen_a32_test_c  $(DIR)/gen_x64_test_c

############################################################
# Python Port
############################################################

$(DIR)/clone_x64_test:
	@echo "[$@]"
	$(PYPY) ./elfhelper.py clone TestData/hello-x64 $@.clone.out > $@.out 2>&1
	cmp -l $@.clone.out TestData/hello-x64

$(DIR)/clone_a32_test:
	@echo "[$@]"
	$(PYPY) ./elfhelper.py clone TestData/hello_barebones-a32 $@.clone.out > $@.out 2>&1
	cmp -l  $@.clone.out TestData/hello_barebones-a32


$(DIR)/gen_x64_test:
	@echo "[$@]"
	$(PYPY) ./gen_elf_test.py genx64 $@.exe > $@.log.out 2>&1
	chmod a+rx $@.exe
	$(QEMU_X64) ./$@.exe > $@.out
	diff $@.out TestData/gen.x64.golden

$(DIR)/gen_a32_test:
	@echo "[$@]"
	$(PYPY) ./gen_elf_test.py gena32 $@.exe  > $@.log.out 2>&1
	chmod a+rx $@.exe
	$(QEMU_A32) ./$@.exe > $@.out
	diff $@.out TestData/gen.a32.golden

$(DIR)/gen_a64_test:
	@echo "[$@]"
	$(PYPY) ./gen_elf_test.py gena64 $@.exe  > $@.log.out 2>&1
	chmod a+rx $@.exe
	$(QEMU_A64) ./$@.exe > $@.out
	diff $@.out TestData/gen.a64.golden

############################################################
# C++ Port
############################################################
BUILD_DIR=../build

ELF_TOOL = $(BUILD_DIR)/elf_tool.exe

$(ELF_TOOL):
	@cd $(BUILD_DIR); $(MAKE) -s elf_tool.exe


GEN_ELF_TEST=$(BUILD_DIR)/gen_elf_test.exe

$(GEN_ELF_TEST):: enum_gen.cc enum_gen.h gen_elf_test.cc
	@cd $(BUILD_DIR); $(MAKE) -s gen_elf_test.exe

enum_gen.h: enum_tab.py
	@echo "[$@]"
	$(PYPY) ./enum_tab.py gen_h < enum_gen.h > $(DIR)/$@.tmp
	@mv $(DIR)/$@.tmp $@

enum_gen.cc: enum_tab.py enum_gen.h
	@echo "[$@]"
	$(PYPY) ./enum_tab.py gen_c  < enum_gen.cc > $(DIR)/$@.tmp
	@mv $(DIR)/$@.tmp $@

$(DIR)/clone_a32_test_c: $(ELF_TOOL)
	@echo "[$@]"
	$(ELF_TOOL) TestData/hello_barebones-a32

$(DIR)/clone_x64_test_c:
	@echo "[$@]"
	$(ELF_TOOL) TestData/hello-x64

$(DIR)/gen_a32_test_c: $(GEN_ELF_TEST)
	@echo "[$@]"
	$(PYPY) ./gen_elf_test.py gena32 $@.py.exe  > $@.py.log.out 2>&1
	$(GEN_ELF_TEST) gena32 $@.exe  > $@.log.out 2>&1
	cmp -l $@.py.exe  $@.exe
	chmod a+rx $@.exe
	./$@.exe > $@.out
	diff $@.out TestData/gen.a32.golden

$(DIR)/gen_x64_test_c: $(GEN_ELF_TEST)
	@echo "[$@]"
	$(PYPY) ./gen_elf_test.py genx64 $@.py.exe  > $@.py.log.out 2>&1
	$(GEN_ELF_TEST) genx64 $@.exe  > $@.log.out 2>&1
	cmp -l $@.py.exe  $@.exe
	chmod a+rx $@.exe
	./$@.exe > $@.out
	diff $@.out TestData/gen.x64.golden

$(DIR)/gen_a64_test_c: $(GEN_ELF_TEST)
	@echo "[$@]"
	$(PYPY) ./gen_elf_test.py gena64 $@.py.exe  > $@.py.log.out 2>&1
	$(GEN_ELF_TEST) gena64 $@.exe  > $@.log.out 2>&1
	cmp -l $@.py.exe  $@.exe
	chmod a+rx $@.exe
	./$@.exe > $@.out
	diff $@.out TestData/gen.a64.golden

############################################################
# Misc
############################################################

clean:
	rm -f $(DIR)/*
